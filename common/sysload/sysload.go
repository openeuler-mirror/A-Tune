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

package sysload

import (
	"bufio"
	"container/list"
	"fmt"
	"os"
	"runtime"
	"strconv"
	"strings"
	"time"

	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/topology"
	"gitee.com/openeuler/A-Tune/common/utils"
)

// #include <unistd.h>
import "C"

var Sysload SystemLoad

func init() {
	Sysload.Init()
}

var clockTicks uint64

// ScaleShift is in order to avoid float compute
const ScaleShift uint64 = 10
const nsecPerSec uint64 = 1000000000
const cpuIDIndex = 3

type timeUsage struct {
	lastUpdate time.Time
	user       uint64
	system     uint64
	load       int
}

// cpu stat type enum
type CPUStatType int

const (
	CPUStatCPUNum    CPUStatType = 0
	CPUStatUser      CPUStatType = 1
	CPUStatNice      CPUStatType = 2
	CPUStatSystem    CPUStatType = 3
	CPUStatIdle      CPUStatType = 4
	CPUStatIOWait    CPUStatType = 5
	CPUStatIRQ       CPUStatType = 6
	CPUStatSoftIRQ   CPUStatType = 7
	CPUStatSteal     CPUStatType = 8
	CPUStatGuest     CPUStatType = 9
	CPUStatGuestNice CPUStatType = 10
	CPUStatMAX       CPUStatType = 11
)

// data structure containing update time and all cpu stat
type CPUStat struct {
	lastUpdate time.Time
	Fields     [CPUStatMAX]uint64
}

func (cs *CPUStat) delta(newcs *CPUStat, oldcs *CPUStat) {
	duration := uint64(newcs.lastUpdate.Sub(oldcs.lastUpdate)) / nsecPerSec * clockTicks
	if duration == 0 {
		return
	}

	for i := CPUStatCPUNum + 1; i < CPUStatMAX; i++ {
		cs.Fields[i] = (scaleUp((newcs.Fields[i] - oldcs.Fields[i])) / (duration))
	}
}

func (cs *CPUStat) load() int {
	var sum uint64

	sum = 0
	for i := CPUStatCPUNum + 1; i < CPUStatMAX; i++ {
		if i == CPUStatIdle {
			continue
		}
		sum += cs.Fields[i]
	}
	return int(sum)
}

func (cs *CPUStat) idle() int {
	return int(cs.Fields[CPUStatIdle])
}

func (cs *CPUStat) irq() int {
	return int(cs.Fields[CPUStatIRQ] + cs.Fields[CPUStatSoftIRQ])
}

func init() {
	clockTicks = uint64(C.sysconf(C._SC_CLK_TCK))
}

func scaleUp(i uint64) uint64 {
	return i << ScaleShift
}

func (usage *timeUsage) init(now *time.Time, user uint64, system uint64) {
	usage.lastUpdate = *now
	usage.user = user
	usage.system = system
}

func (usage *timeUsage) update(now *time.Time, user uint64, system uint64) {
	duration := uint64(now.Sub(usage.lastUpdate)) / nsecPerSec * clockTicks
	if duration == 0 {
		return
	}

	usage.load = int(scaleUp((user-usage.user)+(system-usage.system)) / (duration))
	usage.lastUpdate = *now
	usage.user = user
	usage.system = system
}

// TaskLoad represent load with cpu usage
type TaskLoad struct {
	id    uint64
	usage timeUsage
}

// Init of TaskLoad init load with timestamp
func (load *TaskLoad) Init(now *time.Time, user uint64, system uint64) {
	load.usage.init(now, user, system)
}

// Update of TaskLoad update load with new timestamp
func (load *TaskLoad) Update(now *time.Time, user uint64, system uint64) {
	load.usage.update(now, user, system)
}

// CPULoad represent cpu load with cpu usage
type CPULoad struct {
	last CPUStat
	stat CPUStat
}

// Init of CPULoad init load with timestamp
func (load *CPULoad) Init(stat CPUStat) {
	load.last = stat
	load.stat = stat
}

// Update of CPULoad update load with new timestamp
func (load *CPULoad) Update(stat CPUStat) {
	load.stat.delta(&stat, &load.last)
	load.last = stat
}

// SystemLoad provides cpus and tasks load according running time
type SystemLoad struct {
	cpusLoad  []CPULoad
	tasksLoad list.List
}

func parseCPUStatLine(str string) (CPUStat, error) {
	var stat CPUStat
	var err error

	statFields := strings.Fields(str)
	for i := CPUStatCPUNum; i < CPUStatMAX; i++ {
		if i == CPUStatCPUNum {
			cpu := statFields[CPUStatCPUNum]
			stat.Fields[i], err = strconv.ParseUint(cpu[cpuIDIndex:], utils.DecimalBase, utils.Uint64Bits)
			if err != nil {
				err = fmt.Errorf("convert cpu number from %s failed", cpu)
				return stat, err
			}
			continue
		}
		stat.Fields[i], err = strconv.ParseUint(statFields[i], utils.DecimalBase, utils.Uint64Bits)
		if err != nil {
			err = fmt.Errorf("convert cpu user time from %s failed", statFields[i])
			return stat, err
		}

	}

	return stat, nil
}

func (sysload *SystemLoad) cpusLoadUpdate(init bool) {
	file, err := os.Open(utils.ProcDir + "stat")
	if err != nil {
		log.Error(err)
		return
	}

	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	now := time.Now()
	for scanner.Scan() {
		line := scanner.Text()
		if line[0:cpuIDIndex] != "cpu" {
			break
		}
		if line[cpuIDIndex] == ' ' {
			continue
		}
		stat, err := parseCPUStatLine(line)
		stat.lastUpdate = now
		if err != nil {
			log.Error(err)
			continue
		}
		if init {
			sysload.cpusLoad[stat.Fields[CPUStatCPUNum]].Init(stat)
		} else {
			sysload.cpusLoad[stat.Fields[CPUStatCPUNum]].Update(stat)
		}
	}
	file.Close()
}

type taskStat struct {
	user   uint64
	system uint64
}

func parseTaskStatLine(str string) (taskStat, error) {
	const taskUserTimeIndex = 13
	const taskSystemTimeIndex = 14
	var stat taskStat
	var err error

	statFields := strings.Fields(str)
	stat.user, err = strconv.ParseUint(statFields[taskUserTimeIndex], utils.DecimalBase, utils.Uint64Bits)
	if err != nil {
		err = fmt.Errorf("convert task user time from %s failed", statFields[taskUserTimeIndex])
		return stat, err
	}
	stat.system, err = strconv.ParseUint(statFields[taskSystemTimeIndex], utils.DecimalBase, utils.Uint64Bits)
	if err != nil {
		err = fmt.Errorf("convert task system time from %s failed", statFields[taskSystemTimeIndex])
		return stat, err
	}
	return stat, nil
}

func getPidFromTid(tid uint64) (uint64, error) {
	var pid uint64

	taskStatusPath := fmt.Sprintf(utils.ProcDir+"%d/status", tid)
	file, err := os.Open(taskStatusPath)
	if err != nil {
		return pid, err
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "Tgid") {
			_, err := fmt.Sscanf(line, "Tgid: %d", &pid)
			return pid, err
		}
	}
	return pid, fmt.Errorf("can not find Tgid from status file")
}

func updateTaskLoad(load *TaskLoad, init bool) {
	pid, err := getPidFromTid(load.id)
	if err != nil {
		log.Error(err)
		return
	}

	taskStatPath := fmt.Sprintf(utils.ProcDir+"%d/stat", pid)
	line := utils.ReadAllFile(taskStatPath)
	if line == "" {
		return
	}
	stat, err := parseTaskStatLine(line)
	if err != nil {
		log.Error(err)
		return
	}

	now := time.Now()
	if init {
		load.Init(&now, stat.user, stat.system)
	} else {
		load.Update(&now, stat.user, stat.system)
	}
}

func (sysload *SystemLoad) tasksLoadUpdate() {
	for task := sysload.tasksLoad.Front(); task != nil; task = task.Next() {
		updateTaskLoad((task.Value).(*TaskLoad), false)
	}
}

// Init of SystemLoad init cpus' and tasks' load with current timestamp
func (sysload *SystemLoad) Init() {
	cpuNum := runtime.NumCPU()

	sysload.cpusLoad = make([]CPULoad, cpuNum)
	sysload.tasksLoad.Init()
	sysload.cpusLoadUpdate(true)
}

// AddTask of SystemLoad monitor new task's load
func (sysload *SystemLoad) AddTask(id uint64) {
	var taskLoad TaskLoad

	taskLoad.id = id
	updateTaskLoad(&taskLoad, true)
	sysload.tasksLoad.PushBack(&taskLoad)
}

// RemoveTask of SystemLoad stop to monitor new task's load
func (sysload *SystemLoad) RemoveTask(id uint64) {
	taskLoad := sysload.findTask(id)
	if taskLoad != nil {
		sysload.tasksLoad.Remove(taskLoad)
	}
}

// Update of SystemLoad update load if cpus and monitored tasks
func (sysload *SystemLoad) Update() {
	sysload.cpusLoadUpdate(false)
	sysload.tasksLoadUpdate()
}

//GetTaskCpuPercent return task average cpu percent
func (sysload *SystemLoad) GetTaskCpuPercent() int {
	if sysload.tasksLoad.Len() == 0 {
		return 0
	}
	sum := 0
	for task := sysload.tasksLoad.Front(); task != nil; task = task.Next() {
		taskLoad := (task.Value).(*TaskLoad)
		sum += taskLoad.usage.load
	}

	cpuNum := runtime.NumCPU()
	totalCpuTime := topology.GetLoad() + topology.GetIdle()
	return sum * 100 * cpuNum / (sysload.tasksLoad.Len() * totalCpuTime)
}

func (sysload *SystemLoad) findTask(id uint64) *list.Element {
	for taskLoad := sysload.tasksLoad.Front(); taskLoad != nil; taskLoad = taskLoad.Next() {
		if (taskLoad.Value).(*TaskLoad).id == id {
			return taskLoad
		}
	}
	return nil
}

// GetCPULoad of SystemLoad get cpu load
func (sysload *SystemLoad) GetCPULoad(cpu int) (int, int, int) {
	if cpu > len(sysload.cpusLoad) {
		return 0, 0, 0
	}

	load := sysload.cpusLoad[cpu].stat.load()
	idle := sysload.cpusLoad[cpu].stat.idle()
	irq := sysload.cpusLoad[cpu].stat.irq()
	return load, idle, irq
}

// ClearCPULoad clear cpu load
func (sysload *SystemLoad) ClearCPULoad(cpu int) {
	if cpu > len(sysload.cpusLoad) {
		return
	}

	var stat CPUStat
	sysload.cpusLoad[cpu].Init(stat)
}

// GetTaskLoad of SystemLoad get task load
func (sysload *SystemLoad) GetTaskLoad(id uint64) int {
	taskLoad := sysload.findTask(id)
	if taskLoad != nil {
		return (taskLoad.Value).(*TaskLoad).usage.load
	}
	return 0
}

// NewSysload alloc a new sysload object
func NewSysload() *SystemLoad {
	var sysload SystemLoad

	sysload.Init()
	for idx, load := range sysload.cpusLoad {
		log.Infof("sysload: cpu: %d, load: %v", idx, load)
	}
	return &sysload
}
