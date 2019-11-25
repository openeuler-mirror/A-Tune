/*
 * Copyright (c) 2019 Huawei Technologies Co., Ltd.
 * A-Tune is licensed under the Mulan PSL v1.
 * You can use this software according to the terms and conditions of the Mulan PSL v1.
 * You may obtain a copy of Mulan PSL v1 at:
 *     http://license.coscl.org.cn/MulanPSL
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v1 for more details.
 * Create: 2019-10-29
 */

package system

type System struct {
	cpus     []int
	irqs     []int
	numa     []int
	isolated []int
	nics     []string
}

var instance *System = nil

func (system *System) Init() error {
	return nil
}

func (system *System) GetAllCpu() []int {
	return system.cpus
}

func (system *System) GetCpu(numa int) []int {
	return system.cpus
}

func (system *System) GetIsolatedCpu() []int {
	return system.cpus
}

func (system *System) GetAllIrq() []int {
	return system.irqs
}

func (system *System) GetIrq(device string) []int {
	return system.irqs
}

func (system *System) GetNuma() []int {
	return system.numa
}

func (system *System) GetDeviceNuma(device string) int {
	return 0
}

func (system *System) GetNICs() []string {
	return system.nics
}

func (system *System) GetPids(Application string) []int {
	/* Get pid from application */

	return nil
}

func GetSystem() *System {
	if instance == nil {
		instance = new(System)
		instance.Init()
	}

	return instance
}
