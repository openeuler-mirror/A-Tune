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

package models

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"strings"
	
	"gitee.com/openeuler/A-Tune/common/config"
	HTTP "gitee.com/openeuler/A-Tune/common/http"
	"gitee.com/openeuler/A-Tune/common/log"
)

// MonitorBody :the body send to monitor service
type MonitorBody struct {
	Module  string `json:"module"`
	Purpose string `json:"purpose"`
	Fmt     string `json:"fmt"`
	Path    string `json:"path"`
	Para    string `json:"para"`
}

// MonitorGetResp :the response of the monitor service
type MonitorGetResp struct {
	Status string `json:"status"`
	Value  string `json:"value"`
}

// Get method calling the get method of the monitor service
func (m *MonitorBody) Get() (*MonitorGetResp, error) {
	url := config.GetURL(config.MonitorURI)
	res, err := HTTP.Get(url, m)
	if err != nil {
		return nil, err
	}

	defer res.Body.Close()
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("connect to monitor service failed")
	}

	resBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respPutIns := new(MonitorGetResp)
	err = json.Unmarshal(resBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil
}

// MonitorGet method calling the get method of the monitor service, return error if failed
func MonitorGet(module string, purpose string, format string, path string, para string) (string, error) {
	monitorBody := &MonitorBody{
		Module:  strings.ToUpper(module),
		Purpose: strings.ToUpper(purpose),
		Fmt:     format,
		Path:    path,
		Para:    para,
	}

	respGetIns, err := monitorBody.Get()
	if err != nil {
		log.Errorf("model monitor module %s get data failed: %v", module, err)
		return "", err
	}

	if respGetIns.Status != "OK" {
		log.Errorf("model monitor module %s get data failed, error: %s", module, respGetIns.Value)
		return "", fmt.Errorf(respGetIns.Value)
	}
	return respGetIns.Value, nil
}
