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
	"gitee.com/openeuler/A-Tune/common/config"
)

// DaemonInstance :interface for Daemon service
type DaemonInstance interface {
	Init() error
	Set(cfg *config.Cfg)
}

// DaemonService :registry for the daemon service
type DaemonService struct {
	Name     string
	Instance DaemonInstance
}

var daemonServices []*DaemonService

// RegisterDaemonService method add service to damonService slice
func RegisterDaemonService(name string, instance DaemonInstance) {
	daemonServices = append(daemonServices, &DaemonService{
		Name:     name,
		Instance: instance,
	})
}

// GetDaemonServices method return the service slice
func GetDaemonServices() []*DaemonService {
	return daemonServices
}

// BackgroundService : the interface of the background service
type BackgroundService interface {
	Run() error
}
