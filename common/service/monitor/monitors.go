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

package monitors

import (
	"atune/common/config"
	"atune/common/log"
	"atune/common/models"
	"atune/common/profile"
	"atune/common/registry"
	"atune/common/sqlstore"
	"atune/common/utils"
	"fmt"
	"os"
	"path"
	"strings"
)

func init() {
	registry.RegisterDaemonService("monitor", &Monitor{})
}

// Monitor : the struct store the monitor service conf message
type Monitor struct {
	Cfg *config.Cfg
}

// Init method
func (m *Monitor) Init() error {
	return nil
}

// Set the config of the monitor
func (m *Monitor) Set(cfg *config.Cfg) {
	m.Cfg = cfg
}

// Run method start the monitor service
func (m *Monitor) Run() error {
	if err := utils.WaitForPyservice(); err != nil {
		log.Errorf("waiting for pyservice faild: %v", err)
		return err
	}

	modules := m.Cfg.Raw.Section("monitor").Key("module").String()
	if modules == "" {
		log.Infof("module conf is empty string")
		return nil
	}
	monitorModules := strings.Split(modules, ",")
	monitorPath := config.DefaultCheckerPath

	exist, err := utils.PathExist(monitorPath)
	if err != nil {
		return err
	}

	if !exist {
		if err = os.MkdirAll(monitorPath, 0750); err != nil {
			return err
		}
	}

	for _, module := range monitorModules {
		module = strings.TrimSpace(module)
		modulePurpose := strings.Split(module, "_")
		if len(modulePurpose) != 2 {
			log.Errorf("module format %s is not corrent!", module)
			continue
		}

		filename := module + "." + config.FileFormat
		filename = path.Join(monitorPath, filename)

		if _, err := models.MonitorGet(strings.ToUpper(modulePurpose[0]),
			strings.ToUpper(modulePurpose[1]),
			config.FileFormat, filename, ""); err != nil {
			log.Errorf("collect module %s faild, error: %v", module, err)
			continue
		}
	}

	if err := activeProfile(); err != nil {
		return err
	}
	return nil
}

func activeProfile() error {
	// Load Current Active Profile
	profiles := &sqlstore.GetClass{Active: true}
	err := sqlstore.GetClasses(profiles)
	if err != nil {
		return err
	}
	if len(profiles.Result) != 1 {
		return fmt.Errorf("no active profile or more than 1 active profile")
	}

	//profile_names := strings.Split(strings.Trim(profiles.Result[0].ProfileType, "\n"), " ")
	profileType := profiles.Result[0].Class
	pro, _ := profile.LoadFromWorkloadType(profileType)
	if err = pro.RollbackActive(nil); err != nil {
		return err
	}

	return nil
}
