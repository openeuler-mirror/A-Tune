/*
 * Copyright (c) 2019 Huawei Technologies Co., Ltd.
 * A-Tune is licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Create: 2019-10-29
 */

package system

import (
	"bufio"
	"encoding/xml"
	"fmt"
	"io/ioutil"
	"os"
	"path"
	"strconv"
	"strings"
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/models"
	"gitee.com/openeuler/A-Tune/common/utils"
)

type cpu struct {
	cpus []int
}

// System information
type System struct {
	numa     map[int]cpu
	isolated []int
	nics     []string
}

var instance *System = nil

// Init system instance
func (system *System) Init() error {
	system.numa = make(map[int]cpu)

	numaFile := path.Join(config.DefaultCheckerPath, "mem_numa.raw")
	_, err := models.MonitorGet("mem", "numa", "raw", numaFile, "")
	if err != nil {
		return err
	}

	if err := system.loadNuma(numaFile); err != nil {
		return err
	}

	networkTopoFile := path.Join(config.DefaultCheckerPath, "net_topo.xml")
	_, err = models.MonitorGet("net", "topo", "xml", networkTopoFile, "")
	if err != nil {
		return err
	}
	if err := system.loadNics(networkTopoFile); err != nil {
		return err
	}

	if err := system.loadIsolcpus(); err != nil {
		return err
	}

	return nil
}

// GetAllCPU :get all system cpus
func (system *System) GetAllCPU() []int {
	cpus := make([]int, 0)
	for _, value := range system.numa {
		cpus = append(cpus, value.cpus...)
	}
	return cpus
}

// GetCPU :get numa cpus
func (system *System) GetCPU(numa int) []int {
	if _, ok := system.numa[numa]; ok {
		return system.numa[numa].cpus
	}

	return nil
}

// GetIsolatedCPU :get system isolated cpus
func (system *System) GetIsolatedCPU() []int {
	return system.isolated
}

// GetAllIrq : get all system irqs
func (system *System) GetAllIrq() []int {
	irqs, err := system.loadIrqs("")
	if err != nil {
		return nil
	}
	return irqs
}

// GetIrq : get device irqs
func (system *System) GetIrq(device string) []int {
	irqs, err := system.loadIrqs(device)
	if err != nil {
		return nil
	}
	return irqs
}

// GetNuma : get all system numa nodes
func (system *System) GetNuma() []int {
	numas := make([]int, 0)
	for key := range system.numa {
		numas = append(numas, key)
	}
	return numas
}

// GetDeviceNuma : get device numa node
func (system *System) GetDeviceNuma(device string) int {
	key := fmt.Sprintf("class/net/%s/device/numa_node", device)
	numaNode, err := models.ConfiguratorGet("sysfs.sysfs", key)
	if err != nil {
		return -1
	}

	value, err := strconv.Atoi(numaNode)
	if err != nil {
		return -1
	}

	return value
}

// GetIrqAffinity : get irq affinity list
func (system *System) GetIrqAffinity(irq int) int {
	irqAffinityPath := fmt.Sprintf("%s/irq/%d/smp_affinity_list", utils.ProcDir, irq)
	line := utils.ReadAllFile(irqAffinityPath)
	line = strings.Replace(line, "\n", "", -1)
	cpuId, err := strconv.Atoi(line)
	if err != nil {
		log.Errorf("get cpuId from %s failed\n", irqAffinityPath)
		return -1
	}
	return cpuId
}

// SetIrqAffinity : set irq affinity
func (system *System) SetIrqAffinity(irq int, cpuId int) error {
	path := fmt.Sprintf("%s/irq/%d/smp_affinity_list", utils.ProcDir, irq)
	err := utils.WriteFile(path, strconv.Itoa(cpuId), utils.FilePerm, os.O_WRONLY)
	if err != nil {
		return err
	}
	return nil
}

// GetNICs :get system network interfaces
func (system *System) GetNICs() []string {
	return system.nics
}

// GetPids :get all pids of application
func (system *System) GetPids(application string) []int {
	pidsStr, err := models.ConfiguratorGet("affinity.processid", application)
	if err != nil {
		log.Errorf(err.Error())
		return nil
	}

	pidsArr := strings.Fields(strings.TrimSpace(pidsStr))
	pids := make([]int, 0)

	for _, pid := range pidsArr {
		value, _ := strconv.Atoi(pid)
		pids = append(pids, value)
	}
	return pids
}

func (system *System) loadNuma(path string) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}

	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		parts := strings.Fields(scanner.Text())
		if len(parts) < 4 {
			continue
		}
		if "cpus" == strings.Trim(parts[2], ":") {
			cpus := make([]int, 0)
			cpuParts := parts[3:]
			for _, cpuIndex := range cpuParts {
				cpu, _ := strconv.Atoi(cpuIndex)
				cpus = append(cpus, cpu)
			}

			node, _ := strconv.Atoi(parts[1])
			system.numa[node] = cpu{cpus: cpus}
		}
	}

	return nil
}

func (system *System) loadNics(path string) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}

	defer file.Close()

	data, err := ioutil.ReadAll(file)
	if err != nil {
		return err
	}

	networkTopo := NetworkTopo{}
	err = xml.Unmarshal(data, &networkTopo)
	if err != nil {
		return err
	}

	for _, network := range networkTopo.Networks {
		if network.Name == "" {
			system.nics = append(system.nics, network.NetChild.Name)
			continue
		}
		system.nics = append(system.nics, network.Name)
	}

	return nil
}

func (system *System) loadIrqs(device string) ([]int, error) {
	if device != "" {
		device = fmt.Sprintf(";--nic=%s", device)
	}

	irqsStr, err := models.MonitorGet("sys", "interrupts", "raw", "", device)
	if err != nil {
		return nil, err
	}
	irqs := make([]int, 0)

	if strings.TrimSpace(irqsStr) == "" {
		return irqs, nil
	}
	for _, value := range strings.Split(irqsStr, " ") {
		irq, _ := strconv.Atoi(value)
		irqs = append(irqs, irq)
	}

	return irqs, nil
}

func (system *System) loadIsolcpus() error {
	isolcpus, err := models.ConfiguratorGet("bootloader.cmdline", "isolcpus")
	if err != nil {
		return err
	}

	if strings.TrimSpace(isolcpus) == "" {
		return nil
	}
	isolCPUSlice := strings.Split(isolcpus, ",")
	fmt.Println("isolCPUSlice:", isolCPUSlice)
	for _, cpuIndex := range isolCPUSlice {
		if !strings.Contains(cpuIndex, "-") {
			cpu, _ := strconv.Atoi(cpuIndex)
			system.isolated = append(system.isolated, cpu)
			continue
		}
		cpuRange := strings.Split(cpuIndex, "-")
		if len(cpuRange) != 2 {
			continue
		}
		low, _ := strconv.Atoi(cpuRange[0])
		high, _ := strconv.Atoi(cpuRange[1])
		if high <= low {
			continue
		}

		for cpu := low; cpu <= high; cpu++ {
			system.isolated = append(system.isolated, cpu)
		}
	}

	return nil
}

// GetSystem return System instance
func GetSystem() *System {
	if instance == nil {
		instance = new(System)
		err := instance.Init()
		if err != nil {
			log.Errorf(err.Error())
			return nil
		}
	}

	return instance
}
