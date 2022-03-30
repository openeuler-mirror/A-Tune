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

package monitors

import (
	"os"
	"path"
	"strings"
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/models"
	"gitee.com/openeuler/A-Tune/common/profile"
	"gitee.com/openeuler/A-Tune/common/registry"
	"gitee.com/openeuler/A-Tune/common/sqlstore"
	"gitee.com/openeuler/A-Tune/common/utils"
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
		log.Errorf("waiting for pyservice failed: %v", err)
		return err
	}

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

	modules := m.Cfg.Raw.Section("monitor").Key("module").String()
	if modules == "" {
		log.Errorf("module conf is empty string")
		return nil
	}
	monitorModules := strings.Split(modules, ",")
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
			log.Errorf("collect module %s failed, error: %v", module, err)
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
	profileLogs, err := sqlstore.GetProfileLogs()
	if err != nil {
		return err
	}

	if len(profileLogs) != 1 {
		log.Warnln("no active profile or more than 1 active profile")
		return nil
	}

	profileNames := strings.Split(profileLogs[0].ProfileID, ",")

	pro, _ := profile.Load(profileNames)
	if err = pro.RollbackActive(nil); err != nil {
		return err
	}

	return nil
}
