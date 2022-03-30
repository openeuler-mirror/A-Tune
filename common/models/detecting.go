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
 * Create: 2020-09-30
 */

package models

import (
	"fmt"
	"io/ioutil"
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/http"
)

// Detecting : The data that send to http service for detecting
type Detecting struct {
	AppName    string `json:"appname"`
	DetectPath    string `json:"detectpath"`
}

// Get method call detecting service
func (t *Detecting) Get() (bool, error, string) {
	url := config.GetURL(config.DetectingURI)
	result := " "
	response, err := http.Get(url, t)
	if err != nil {
		return false, err, result
	}

	defer response.Body.Close()

	if response.StatusCode != 200 {
		return false, fmt.Errorf("detecting data failed %d", response.StatusCode), result
	}

	res, err := ioutil.ReadAll(response.Body)
	if err != nil {
		return false, err, result
	}

	return true, nil, string(res)
}
