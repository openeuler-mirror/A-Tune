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
	"fmt"
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/http"
)

// Training : The data that send to http service for training
type Training struct {
	DataPath   string `json:"datapath"`
	ModelPath  string `json:"modelpath"`
	OutputPath string `json:"outputpath"`
}

// Post method call training service
func (t *Training) Post() (bool, error) {
	url := config.GetURL(config.TrainingURI)
	response, err := http.Post(url, t)
	if err != nil {
		return false, err
	}

	defer response.Body.Close()
	if response.StatusCode != 200 {
		return false, fmt.Errorf("training data failed")
	}

	return true, nil
}
