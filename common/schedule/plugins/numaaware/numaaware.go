/*
 * Copyright (c) 2020 Huawei Technologies Co., Ltd.
 * A-Tune is licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Create: 2020-04-28
 */

package numaaware

import (
	"fmt"
	"io/ioutil"
	"strconv"
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/schedule/framework"
	"gitee.com/openeuler/A-Tune/common/sysload"
	"gitee.com/openeuler/A-Tune/common/system"
	"gitee.com/openeuler/A-Tune/common/topology"
	"gitee.com/openeuler/A-Tune/common/utils"
)

// NumaAware pick node concerning NUMA topology
type NumaAware struct {
	cpus       map[int]bool
	threadTask map[uint64]bool
}

// Name of plugin
const Name = "numaaware"

// Name return name of plugin
func (na *NumaAware) Name() string {
	return Name
}

// Preprocessing do some work before pick nodes
func (na *NumaAware) Preprocessing(bindtaskinfo *[]*framework.BindTaskInfo) {
	log.Infof("preprocessing in %s plugin", Name)
}

// PickNodesforPids set nodes for given tasks
func (na *NumaAware) PickNodesforPids(bindtaskinfo *[]*framework.BindTaskInfo) {
	log.Infof("PickNodesforPids in %s plugin", Name)

	systemInstance := system.GetSystem()
	if systemInstance == nil {
		log.Errorf("[numaaware]failed to get system instance")
		return
	}
	irqsForNetwork := systemInstance.GetIrq(config.Network)
	if irqsForNetwork == nil {
		log.Errorf("[numaaware]failed to get irqs for network: %s", config.Network)
		return
	}
	numaId := systemInstance.GetDeviceNuma(config.Network)
	if numaId == -1 {
		log.Errorf("[numaaware]failed to get numa for network: %s", config.Network)
		return
	}
	cpusForNumaId := systemInstance.GetCPU(numaId)
	if cpusForNumaId == nil {
		log.Errorf("[numaaware]failed to get cpus for numa: %d", numaId)
		return
	}
	log.Infof("[numaaware]network: %s, irqs: %v, numaId: %d, cpus: %v",
		config.Network, irqsForNetwork, numaId, cpusForNumaId)

	na.cpus = make(map[int]bool)
	isNeedBind := false
	for _, irq := range irqsForNetwork {
		cpuId := systemInstance.GetIrqAffinity(irq)
		if cpuId == -1 {
			continue
		}
		if na.cpus[cpuId] || cpuId < cpusForNumaId[0] || cpuId > cpusForNumaId[len(cpusForNumaId)-1] {
			isNeedBind = true
			break
		}
		na.cpus[cpuId] = true
	}

	if isNeedBind {
		na.cpus = make(map[int]bool)
		index := 0
		for _, irq := range irqsForNetwork {
			if err := systemInstance.SetIrqAffinity(irq, cpusForNumaId[index]); err != nil {
				log.Error(err)
				continue
			}
			na.cpus[cpusForNumaId[index]] = true
			index++
		}
		log.Infof("[numaaware]the network bind cpus: %v", na.cpus)
	}
}

// Postprocessing do some work after task bindings
func (na *NumaAware) Postprocessing(bindtaskinfo *[]*framework.BindTaskInfo) {
	if len(*bindtaskinfo) == 0 {
		return
	}

	na.pickNodeForTask(bindtaskinfo)
	log.Infof("BalanceNode in %s plugin", Name)
}

// New create a NumaAware
func New() (framework.Plugin, error) {
	return &NumaAware{}, nil
}

func (na *NumaAware) pickNodeForTask(taskinfo *[]*framework.BindTaskInfo) {
	systemInstance := system.GetSystem()
	if systemInstance == nil {
		log.Errorf("[numaaware]failed to get system instance")
		return
	}
	numaId := systemInstance.GetDeviceNuma(config.Network)
	if numaId == -1 {
		log.Errorf("[numaaware]failed to get numa for network: %s", config.Network)
		return
	}
	cpusForNumaId := systemInstance.GetCPU(numaId)
	if cpusForNumaId == nil {
		log.Errorf("[numaaware]failed to get cpus for numa: %d", numaId)
		return
	}
	numaNode := topology.GetNumaNodeByID(numaId)
	numaNum := numaNode.Parent(topology.TopoTypeChip).GetChildSize()
	irqsForNetwork := systemInstance.GetIrq(config.Network)
	if irqsForNetwork == nil {
		log.Errorf("[numaaware]failed to get irqs for network: %s", config.Network)
		return
	}
	irqPercent := topology.GetIrqCpuPercent(len(irqsForNetwork))
	taskCpuPercent := sysload.Sysload.GetTaskCpuPercent()
	log.Infof("[numaaware]irq percent: %d, task cpu percent: %d", irqPercent, taskCpuPercent)
	if taskCpuPercent <= 110 {
		switch {
		case len(*taskinfo)+len(na.cpus) <= len(cpusForNumaId):
			na.bindTaskNoSharedIrq(numaNode, taskinfo, topology.TopoTypeNUMA)
		case len(*taskinfo) <= len(cpusForNumaId) && taskCpuPercent+irqPercent < 100:
			na.bindTaskSharedIrq(numaNode, taskinfo, topology.TopoTypeNUMA)
		case len(*taskinfo)+len(na.cpus) <= numaNum*len(cpusForNumaId):
			na.bindTaskNoSharedIrq(numaNode, taskinfo, topology.TopoTypeChip)
		case len(*taskinfo) <= numaNum*len(cpusForNumaId) && taskCpuPercent+irqPercent < 100:
			na.bindTaskSharedIrq(numaNode, taskinfo, topology.TopoTypeChip)
		default:
			setNodeForTask(taskinfo, topology.DefaultSelectNode())
		}
	} else {
		na.updateTask(taskinfo)
		taskSize := taskCpuPercent/100 + 1
		switch {
		case taskSize+len(na.cpus) <= len(cpusForNumaId):
			setNodeForTask(taskinfo, numaNode)
		case taskSize+len(na.cpus) <= numaNum*len(cpusForNumaId):
			chipNode := numaNode.Parent(topology.TopoTypeChip)
			setNodeForTask(taskinfo, chipNode)
		default:
			setNodeForTask(taskinfo, topology.DefaultSelectNode())
		}
	}
}

func (na *NumaAware) bindTaskSharedIrq(numaNode *topology.TopoNode,
	taskinfo *[]*framework.BindTaskInfo, topoType topology.TopoType) {
	cpuNodes := make([]*topology.TopoNode, 0)
	numaNode.Parent(topoType).GetAllCpusForNode(&cpuNodes)
	cpuNodesWithIrq := len(*taskinfo) + len(na.cpus) - len(cpuNodes)
	index := 0
	commonNum := 0
	for _, node := range cpuNodes {
		if index >= len(*taskinfo) {
			break
		}
		if !na.cpus[node.ID()] {
			(*taskinfo)[index].Node = node
			index++
		} else if commonNum < cpuNodesWithIrq {
			(*taskinfo)[index].Node = node
			index++
			commonNum++
		}
	}
}

func (na *NumaAware) bindTaskNoSharedIrq(numaNode *topology.TopoNode,
	taskinfo *[]*framework.BindTaskInfo, topoType topology.TopoType) {
	cpuNodes := make([]*topology.TopoNode, 0)
	numaNode.Parent(topoType).GetAllCpusForNode(&cpuNodes)
	index := 0
	for _, node := range cpuNodes {
		if index >= len(*taskinfo) {
			break
		}
		if na.cpus[node.ID()] {
			continue
		}
		(*taskinfo)[index].Node = node
		index++
	}
}

func setNodeForTask(taskinfo *[]*framework.BindTaskInfo, node *topology.TopoNode) {
	log.Infof("[numaaware]node type %d", node.Type())
	for _, task := range *taskinfo {
		task.Node = node
	}
}

func (na *NumaAware) updateTask(taskinfo *[]*framework.BindTaskInfo) {
	if na.threadTask == nil {
		na.threadTask = make(map[uint64]bool)
	}
	for _, task := range *taskinfo {
		pid := task.Pid
		taskThreadsPath := fmt.Sprintf(utils.ProcDir+"%d/task", pid)
		files, err := ioutil.ReadDir(taskThreadsPath)
		if err != nil {
			log.Error(err)
			continue
		}
		for _, file := range files {
			threadPid, err := strconv.ParseUint(file.Name(), utils.DecimalBase, utils.Uint64Bits)
			if err != nil {
				log.Error(err)
				continue
			}
			if na.threadTask[threadPid] {
				continue
			}
			var ti framework.BindTaskInfo
			ti.Pid = threadPid
			ti.Node = topology.DefaultSelectNode()
			*taskinfo = append(*taskinfo, &ti)
			na.threadTask[threadPid] = true
		}
	}
}
