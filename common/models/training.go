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

package models

import (
	"atune/common/config"
	"atune/common/http"
	"fmt"
)

// Training : The data that send to http service for training
type Training struct {
	DataPath   string `json:"datapath"`
	ModelPath  string `json:"modelpath"`
	OutputPath string `json:"outputpath"`
}

// Post method call training service
func (t *Training) Post() (bool, error) {
	url := config.GetUrl(config.TrainingURI)
	response, err := http.Post(url, t)
	if err != nil {
		return false, err
	}

	defer response.Body.Close()
	if response.StatusCode != 200 {
		return false, fmt.Errorf("training data faild")
	}

	return true, nil
}
