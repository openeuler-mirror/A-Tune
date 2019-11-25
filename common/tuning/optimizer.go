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

package tuning

import (
	PB "atune/api/profile"
	"atune/common/config"
	"atune/common/http"
	"atune/common/log"
	"atune/common/project"
	"encoding/json"
	"fmt"
	"io/ioutil"
)

type optimizerBody struct {
	MaxEval int    `json:"max_eval"`
	Knobs   []knob `json:"knobs"`
}

type knob struct {
	Dtype string  `json:"dtype"`
	Name  string  `json:"name"`
	Type  string  `json:"type"`
	Range []int64 `json:"range"`
	Items []int64 `json:"items"`
	Step  int64   `json:"step"`
	Ref   string  `json:"ref"`
}

type respPostBody struct {
	TaskID string `json:task_id`
}

type optimizerPutBody struct {
	Iterations int    `json:"iterations"`
	Value      string `json:"value"`
}

type respPutBody struct {
	Param string `json:"param"`
}

func (o *optimizerBody) Post() (*respPostBody, error) {
	url := config.GetUrl(config.OptimizerURI)
	res, err := http.Post(url, o)
	if err != nil {
		return nil, err
	}

	defer res.Body.Close()

	respBody, err := ioutil.ReadAll(res.Body)
	respPostIns := new(respPostBody)

	err = json.Unmarshal(respBody, respPostIns)
	if err != nil {
		return nil, err
	}

	return respPostIns, nil
}

func (o *optimizerPutBody) Put(url string) (*respPutBody, error) {
	res, err := http.Put(url, o)
	if err != nil {
		return nil, err
	}

	defer res.Body.Close()

	respBody, err := ioutil.ReadAll(res.Body)
	respPutIns := new(respPutBody)

	err = json.Unmarshal(respBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil

}

// Optimizer : the type implement the bayes serch service
type Optimizer struct {
	Prj *project.YamlPrj
}

/*
DynamicTuned method using bayes algorithm to search the best performance parameters
*/
func (o *Optimizer) DynamicTuned(ch chan *PB.AckCheck) error {
	//dynamic profle setting
	iterations := o.Prj.Iterations
	optimizerBody := new(optimizerBody)
	optimizerBody.MaxEval = iterations

	optimizerBody.Knobs = make([]knob, 0)

	for _, item := range o.Prj.Object {
		knob := new(knob)
		knob.Dtype = item.Info.Dtype
		knob.Name = item.Name
		knob.Type = item.Info.Type
		knob.Ref = item.Info.Ref
		knob.Range = item.Info.Scope
		knob.Items = item.Info.Items
		knob.Step = item.Info.Step
		optimizerBody.Knobs = append(optimizerBody.Knobs, *knob)
	}

	respPostIns, err := optimizerBody.Post()
	if err != nil {
		return err
	}

	log.Infof("create task id is %s", respPostIns.TaskID)
	url := config.GetUrl(config.OptimizerURI)
	optimizerPutURL := fmt.Sprintf("%s/%s", url, respPostIns.TaskID)

	log.Infof("optimizer put url is: %s", optimizerPutURL)

	var eval string
	for i := 0; i <= iterations+1; i++ {
		optPutBody := new(optimizerPutBody)
		optPutBody.Iterations = i
		optPutBody.Value = eval

		respPutIns, err := optPutBody.Put(optimizerPutURL)
		if err != nil {
			log.Errorf("get setting parameter error: %v", err)
			return err
		}
		if i == iterations {
			ch <- &PB.AckCheck{Name: fmt.Sprintf("Optimized result is: %s", respPutIns.Param)}
			break
		}

		log.Infof("setting params is: %s", respPutIns.Param)
		if err := o.Prj.RunSet(respPutIns.Param); err != nil {
			log.Error(err)
			return err
		}

		log.Info("set the parameter success")
		if err := o.Prj.RestartProject(); err != nil {
			log.Error(err)
			return err
		}
		log.Info("restart project success")

		benchmarkByte, err := o.Prj.BenchMark()
		if err != nil {
			log.Error(err)
			return err
		}

		eval, err = o.Prj.Evaluation(benchmarkByte)
		if err != nil {
			log.Error(err)
			return err
		}

		log.Info(eval)
	}

	resp, err := http.Delete(optimizerPutURL)
	if err != nil {
		log.Info("delete task faild:", err)
	}
	defer resp.Body.Close()

	resBytes, err := ioutil.ReadAll(resp.Body)
	log.Debug(string(resBytes))
	return nil
}
