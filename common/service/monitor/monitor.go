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
	HTTP "atune/common/http"
	"atune/common/log"
	"atune/common/profile"
	"atune/common/registry"
	"atune/common/sqlstore"
	"atune/common/utils"
	"encoding/json"
	"fmt"
	"io/ioutil"
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

// MonitorBody :the body send to monitor service
type MonitorBody struct {
	Module  string `json:"module"`
	Purpose string `json:"purpose"`
	Fmt     string `json:"fmt"`
	Path    string `json:"path"`
	Para    string `json:"para"`
}

// RespBody :the response of the monitor service
type RespBody struct {
	Status string `json:"status"`
}

// Get method calling the get method of the monitor service
func (m *MonitorBody) Get() (*RespBody, error) {
	url := config.GetUrl(config.MonitorURI)
	res, err := HTTP.Get(url, m)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("connect to monitor service faild")
	}
	resBody, err := ioutil.ReadAll(res.Body)
	respPutIns := new(RespBody)
	err = json.Unmarshal(resBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil
}

// Run method start the monitor service
func (m *Monitor) Run() error {
	if err := utils.WaitForPyservice(); err != nil {
		log.Errorf("waiting for pyservice faild: %v", err)
		return err
	}

	if err := activeProfile(); err != nil {
		return err
	}

	monitorModules := strings.Split(m.Cfg.Raw.Section("monitor").Key("module").String(), ",")
	monitorPath := config.DefaultCheckerPath

	exist, err := utils.PathExist(monitorPath)
	if err != nil {
		return err
	}

	if !exist {
		os.MkdirAll(monitorPath, os.ModePerm)
	}

	for _, module := range monitorModules {
		module = strings.TrimSpace(module)
		modulePurpose := strings.Split(module, "_")
		if len(modulePurpose) != 2 {
			log.Errorf("module format %s is not corrent!")
			continue
		}

		filename := module + "." + config.FileFormat
		filename = path.Join(monitorPath, filename)

		monitorBody := &MonitorBody{
			Module:  strings.ToUpper(modulePurpose[0]),
			Purpose: strings.ToUpper(modulePurpose[1]),
			Fmt:     config.FileFormat,
			Path:    filename,
		}

		respGetIns, err := monitorBody.Get()
		if err != nil {
			log.Errorf("collect module %s faild", module)
			continue
		}

		if respGetIns.Status != "OK" {
			log.Errorf("collect module %s faild, error: %s", module, respGetIns.Status)
			continue
		}
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
		return fmt.Errorf("No active profile or more than 1 active profile")
	}

	//profile_names := strings.Split(strings.Trim(profiles.Result[0].ProfileType, "\n"), " ")
	profileType := profiles.Result[0].Class
	pro, _ := profile.LoadFromWorkloadType(profileType)
	pro.RollbackActive(nil)

	return nil
}
