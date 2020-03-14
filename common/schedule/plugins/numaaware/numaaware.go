package numaaware

import (
	"fmt"
	"strings"

	"atune/common/log"
	"atune/common/sched"
	"atune/common/schedule/framework"
	"atune/common/sysload"
	"atune/common/topology"
	"atune/common/utils"
)

// NumaAware pick node concerning NUMA topology
type NumaAware struct {
}

// Name of plugin
const Name = "numaaware"

const cpuGapPct = 30
const toPercentage = 100

const (
	// NumaNodeNR represents NUMA nodes number
	NumaNodeNR = 4
)

// Name return name of plugin
func (na *NumaAware) Name() string {
	return Name
}

type numaAwareCallback struct {
	node *topology.TopoNode
}

// callback to update cpu load
func (callback *numaAwareCallback) Callback(node *topology.TopoNode) {
	if callback.node == nil {
		callback.node = node
	} else {
		if callback.node.GetLoad() < node.GetLoad() {
			callback.node = node
		}
	}
}

// Preprocessing do some work before pick nodes
func (na *NumaAware) Preprocessing(bindtaskinfo *[]*framework.BindTaskInfo) {
	log.Infof("preprocessing in %s plugin", Name)
}

// PickNodesforPids set nodes for given tasks
func (na *NumaAware) PickNodesforPids(bindtaskinfo *[]*framework.BindTaskInfo) {
	log.Infof("PickNodesforPids in %s plugin", Name)

	var numaID = -1
	var node *topology.TopoNode
	numaID = getLeastFaultNuma(bindtaskinfo)

	if numaID == -1 {
		node = SelectTypeNode(topology.TopoTypeNUMA)
		numaID = node.ID()
	}
	log.Infof("Pick Numa %d for Pids", numaID)

	pickNodeForTask(bindtaskinfo, numaID)
}

// Postprocessing do some work after task bindings
func (na *NumaAware) Postprocessing(bindtaskinfo *[]*framework.BindTaskInfo) {
	if len(*bindtaskinfo) == 0 {
		return
	}

	srcNode := (*bindtaskinfo)[0].Node
	dstNode := groupTargetNode(srcNode)
	if dstNode == nil {
		return
	}

	if shouldMigrateGroup(bindtaskinfo, srcNode, dstNode) {
		log.Infof("migrate task to %d node", dstNode.ID())
		migrateGroup(bindtaskinfo, srcNode, dstNode)
		return
	}

	log.Infof("BalanceNode in %s plugin", Name)
}

// New create a NumaAware
func New() (framework.Plugin, error) {
	return &NumaAware{}, nil
}

func migrateGroup(taskinfo *[]*framework.BindTaskInfo, srcNode *topology.TopoNode, dstNode *topology.TopoNode) {
	for _, task := range *taskinfo {
		newNode := SelectLighterBindNode(dstNode, task.Node.Type())
		migrateTaskToTopoNode(task, newNode)
	}
	srcNode.SubBind()
	dstNode.AddBind()
}

func migrateTaskToTopoNode(taskInfo *framework.BindTaskInfo, newNode *topology.TopoNode) {
	taskLoad := sysload.Sysload.GetTaskLoad(taskInfo.Pid)
	oldNode := taskInfo.Node

	unbindTaskFromTopoNode(taskInfo, oldNode)
	oldNode.SubLoad(taskLoad)

	bindTaskToTopoNode(taskInfo, newNode)
	newNode.AddLoad(taskLoad)
}

func unbindTaskFromTopoNode(taskInfo *framework.BindTaskInfo, node *topology.TopoNode) {
	detachTaskFromTopoNode(taskInfo, node)
}

func bindTaskToTopoNode(taskInfo *framework.BindTaskInfo, node *topology.TopoNode) {
	if err := setTaskAffinity(taskInfo.Pid, node); err != nil {
		log.Error(err)
	}
	node.AddBind()
}

func detachTaskFromTopoNode(task *framework.BindTaskInfo, node *topology.TopoNode) {
	node.SubBind()
}

func setTaskAffinity(tid uint64, node *topology.TopoNode) error {
	var cpus []uint32

	for cpu := node.Mask().Foreach(-1); cpu != -1; cpu = node.Mask().Foreach(cpu) {
		cpus = append(cpus, uint32(cpu))
	}
	log.Info("bind ", tid, " to cpu ", cpus)
	if err := sched.SetAffinity(tid, cpus); err != nil {
		return err
	}
	return nil
}

func shouldMigrateGroup(taskinfo *[]*framework.BindTaskInfo, srcNode *topology.TopoNode, dstNode *topology.TopoNode) bool {
	if !shouldBalanceBetweenNode(srcNode, dstNode) {
		return false
	}

	gWeight := groupWeight(taskinfo)
	diff := srcNode.GetLoad() - dstNode.GetLoad()
	return diff > gWeight
}

func cpuGap() int {
	return (cpuGapPct << sysload.ScaleShift) / toPercentage
}

func nodeBalanceGap(node *topology.TopoNode) int {
	return node.Mask().Weight() * cpuGap()
}

func shouldBalanceBetweenNode(srcNode *topology.TopoNode, dstNode *topology.TopoNode) bool {
	diff := srcNode.GetLoad() - dstNode.GetLoad()
	gap := nodeBalanceGap(srcNode)
	return diff > gap
}

func groupWeight(taskinfo *[]*framework.BindTaskInfo) int {
	weight := 0

	for _, task := range *taskinfo {
		weight += sysload.Sysload.GetTaskLoad(task.Pid)
	}
	return weight
}

func groupTargetNode(srcNode *topology.TopoNode) *topology.TopoNode {
	if srcNode.Type().Compare(topology.TopoTypeNUMA) >= 0 {
		return nil
	}

	numaNode := srcNode.Parent(topology.TopoTypeNUMA)
	return SelectLighterLoadNode(numaNode, srcNode.Type())
}

func pickNodeForTask(taskinfo *[]*framework.BindTaskInfo, numaID int) {
	numaNode := topology.GetNumaNodeByID(numaID)

	var node *topology.TopoNode
	if len(*taskinfo) == 1 {
		node = SelectLighterLoadNode(numaNode, topology.TopoTypeCPU)
	} else if len(*taskinfo) <= 4 {
		node = SelectLighterLoadNode(numaNode, topology.TopoTypeCluster)
	} else if len(*taskinfo) <= 32 {
		node = numaNode
	} else if len(*taskinfo) <= 64 {
		node = numaNode.Parent(topology.TopoTypeChip)
	} else {
		node = numaNode.Parent(topology.TopoTypeAll)
	}

	log.Infof("numaaware type:%v id:%v", node.Type(), node.ID())
	for _, task := range *taskinfo {
		task.Node = node
	}

}

func getLeastFaultNuma(bindTaskInfo *[]*framework.BindTaskInfo) int {
	var numaFaults [NumaNodeNR]int64
	var maxFaults int64
	var numaID = -1

	for _, task := range *bindTaskInfo {
		topo := getThreadMemTopo(task.Pid)
		for index, count := range topo.NumaFaults {
			numaFaults[index] += count
		}
	}
	for i, faults := range numaFaults {
		if faults > maxFaults {
			maxFaults = faults
			numaID = i
		}
	}
	return numaID
}

// ThreadMemTopo represents access of NUMA nodes
type ThreadMemTopo struct {
	tid        uint64
	NumaFaults [NumaNodeNR]int64
}

// GetThreadMemTopo get thread memory page relation.
func getThreadMemTopo(tid uint64) ThreadMemTopo {
	var topo ThreadMemTopo
	topo.tid = tid
	path := fmt.Sprintf(utils.ProcDir+"%d/task_fault_siblings", tid)
	lines := utils.ReadAllFile(path)
	for _, line := range strings.Split(lines, "\n") {
		if strings.Contains(line, "node") == false {
			continue
		}
		var node int
		var count int64
		_, err := fmt.Sscanf(line, "faults on node %d: %d", &node, &count)
		if err != nil {
			log.Error(err)
			continue
		}
		if node < NumaNodeNR {
			topo.NumaFaults[node] = count
		}
	}
	return topo
}
