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
	"gitee.com/openeuler/A-Tune/common/log"
)

// Configurator :body send to cpi service
type Configurator struct {
	Section string `json:"section"`
	Key     string `json:"key"`
	Value   string `json:"value"`
}

// RespConfigurator :response of call CPI service
type RespConfigurator struct {
	Status string `json:"status"`
	Value  string `json:"value"`
}

// Put method set the key to value, both specified by ConfigPutBody
func (c *Configurator) Put() (*RespConfigurator, error) {
	url := config.GetURL(config.ConfiguratorURI)
	res, err := http.Put(url, c)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode == 404 {
		return nil, fmt.Errorf("section %s is not exist", c.Section)
	}
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("connect to configurator service failed")
	}
	resBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respPutIns := new(RespConfigurator)
	err = json.Unmarshal(resBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil
}

// Post method get the current value of the spefied key and compare with the given value
func (c *Configurator) Post() (*RespConfigurator, error) {
	url := config.GetURL(config.ConfiguratorURI)
	res, err := http.Post(url, c)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode == 404 {
		return nil, fmt.Errorf("section %s is not exist", c.Section)
	}
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("connect to configurator service failed")
	}
	resBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respPutIns := new(RespConfigurator)
	err = json.Unmarshal(resBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil
}

// Get method get the current value of the spefied key by ConfigPutBody
func (c *Configurator) Get() (*RespConfigurator, error) {
	url := config.GetURL(config.ConfiguratorURI)
	res, err := http.Get(url, c)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode == 404 {
		return nil, fmt.Errorf("section %s is not exist", c.Section)
	}
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("connect to configurator service failed")
	}

	resBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respIns := new(RespConfigurator)
	err = json.Unmarshal(resBody, respIns)
	if err != nil {
		return nil, err
	}

	return respIns, nil
}

// ConfiguratorGet method calling the monitor service get method
func ConfiguratorGet(section string, key string) (string, error) {
	body := &Configurator{
		Section: section,
		Key:     key,
	}

	respIns, err := body.Get()
	if err != nil {
		log.Errorf("configurator get method return err: %v", err)
		return "", err
	}

	if respIns.Status != "OK" {
		return "", fmt.Errorf("error: %s", respIns.Value)
	}

	return respIns.Value, nil
}
