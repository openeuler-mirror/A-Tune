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
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/http"
)

// Profile : the data that send to http backup and resume service
type Profile struct {
	Section string `json:"section"`
	Config  string `json:"config"`
	Path    string `json:"path"`
}

//RespBody : the returned value of the backup or resume method
type RespBody struct {
	Status string `json:"status"`
	Value  string `json:"value"`
}

//Backup method the value specified by the Prfile
func (p *Profile) Backup() (*RespBody, error) {
	url := config.GetURL(config.ProfileURI)
	res, err := http.Get(url, p)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode != 200 {
		return nil, fmt.Errorf("backup profile %s failed", p.Config)
	}

	respData, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respIns := new(RespBody)
	err = json.Unmarshal(respData, respIns)
	if err != nil {
		return nil, err
	}
	return respIns, nil
}

//Resume method resume the value specified by the Prfile
func (p *Profile) Resume() (*RespBody, error) {
	url := config.GetURL(config.ProfileURI)
	res, err := http.Put(url, p)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode != 200 {
		return nil, fmt.Errorf("resume config %s failed", p.Config)
	}

	respData, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respIns := new(RespBody)
	err = json.Unmarshal(respData, respIns)
	if err != nil {
		return nil, err
	}
	return respIns, nil
}
