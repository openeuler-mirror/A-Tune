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

// OptimizerPostBody send to the service to create a optimizer task
type OptimizerPostBody struct {
	MaxEval         int32      `json:"max_eval"`
	Knobs           []Knob     `json:"knobs"`
	Engine          string     `json:"engine"`
	RandomStarts    int32      `json:"random_starts"`
	Xref            [][]string `json:"x_ref,omitempty"`
	Yref            []string   `json:"y_ref,omitempty"`
	FeatureFilter   bool       `json:"feature_filter"`
	SplitCount      int32      `json:"split_count"`
	Noise           float64    `json:"noise"`
	SelFeature      bool       `json:"sel_feature"`
	PrjName         string     `json:"prj_name"`
	FeatureSelector string     `json:"feature_selector"`
}

// Knob body store the tuning properties
type Knob struct {
	Dtype   string    `json:"dtype"`
	Name    string    `json:"name"`
	Options []string  `json:"options"`
	Type    string    `json:"type"`
	Range   []float32 `json:"range"`
	Items   []float32 `json:"items"`
	Step    float32   `json:"step"`
	Ref     string    `json:"ref"`
}

// RespPostBody :the body returned of create optimizer task
type RespPostBody struct {
	TaskID  string `json:"task_id"`
	Status  string `json:"status"`
	Message string `json:"message"`
	Iters   int    `json:"iters"`
}

// OptimizerPutBody send to the optimizer service when iterations
type OptimizerPutBody struct {
	Iterations int    `json:"iterations"`
	Value      string `json:"value"`
	Line	   string `json:"line"`
	PrjName    string `json:"prj_name"`
	MaxIter    int    `json:"max_iter"`
}

// RespPutBody :the body returned of each optimizer iteration
type RespPutBody struct {
	Param    string `json:"param"`
	Message  string `json:"message"`
	Rank     string `json:"rank"`
	Finished bool   `json:"finished"`
}

// Post method create a optimizer task
func (o *OptimizerPostBody) Post() (*RespPostBody, error) {
	url := config.GetURL(config.OptimizerURI)
	res, err := http.Post(url, o)
	if err != nil {
		return nil, err
	}

	defer res.Body.Close()

	respBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	if res.StatusCode != 200 {
		return nil, fmt.Errorf(string(respBody))
	}

	respPostIns := new(RespPostBody)

	err = json.Unmarshal(respBody, respPostIns)
	if err != nil {
		return nil, err
	}

	return respPostIns, nil
}

// Put method send benchmark result to optimizer service
func (o *OptimizerPutBody) Put(url string) (*RespPutBody, error) {
	res, err := http.Put(url, o)
	if err != nil {
		return nil, err
	}

	defer res.Body.Close()

	respBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respPutIns := new(RespPutBody)

	err = json.Unmarshal(respBody, respPutIns)
	if err != nil {
		return nil, err
	}

	if res.StatusCode != 200 {
		return nil, fmt.Errorf(respPutIns.Message)
	}

	return respPutIns, nil
}
