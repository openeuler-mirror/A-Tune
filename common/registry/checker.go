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

package registry

import (
	PB "gitee.com/openeuler/A-Tune/api/profile"
)

// CheckerInstance :interface for init service
type CheckerInstance interface {
	Init() error
}

// CheckerService :registry for the checker service
type CheckerService struct {
	Name     string
	Instance CheckerInstance
}

var checkerServices []*CheckerService

// RegisterCheckerService method add service to checkerServices slice
func RegisterCheckerService(name string, instance CheckerInstance) {
	checkerServices = append(checkerServices, &CheckerService{
		Name:     name,
		Instance: instance,
	})
}

// GetCheckerServices method return the service slice
func GetCheckerServices() []*CheckerService {
	return checkerServices
}

// CheckService : the interface of which implement check method
type CheckService interface {
	Check(ch chan *PB.AckCheck) error
}

// DisabledService : the interface useful for mem_top checker service
type DisabledService interface {
	IsCheckDisabled() bool
}

// IsCheckDisabled method check the service is disabled or not
func IsCheckDisabled(csv CheckerInstance) bool {
	cInstance, ok := csv.(DisabledService)
	return ok && cInstance.IsCheckDisabled()
}
