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
	"atune/common/models"
	"atune/common/project"
	"atune/common/utils"
	"fmt"
	"os"
	"strconv"
)

// Optimizer : the type implement the bayes serch service
type Optimizer struct {
	Prj *project.YamlPrjSvr
	utils.MutexLock
}

//BenchMark : the benchmark data
type BenchMark struct {
	Content []byte
}

var optimizerPutURL string
var optimization *Optimizer
var minEval string
var respPutIns *models.RespPutBody
var iter int
var maxIter int
var optimizer = Optimizer{}

// InitTuned method for init tuning
func (o *Optimizer) InitTuned(ch chan *PB.AckCheck, askIter int) error {
	//dynamic profle setting
	if !optimizer.TryLock() {
		return fmt.Errorf("dynamic optimizer search has been in running")
	}
	maxIter = askIter
	if maxIter > o.Prj.Maxiterations {
		maxIter = o.Prj.Maxiterations
		log.Infof("project:%s max iterations:%d", o.Prj.Project, o.Prj.Maxiterations)
		ch <- &PB.AckCheck{Name: fmt.Sprintf("server project %s max iterations %d\n",
			o.Prj.Project, o.Prj.Maxiterations)}
	}

	exist, err := utils.PathExist(config.DefaultTempPath)
	if err != nil {
		return err
	}
	if !exist {
		if err = os.MkdirAll(config.DefaultTempPath, 0750); err != nil {
			return err
		}
	}

	projectName := fmt.Sprintf("project %s\n", o.Prj.Project)
	err = utils.WriteFile(config.TuningFile, projectName, config.FilePerm,
		os.O_WRONLY|os.O_CREATE|os.O_TRUNC)
	if err != nil {
		log.Error(err)
		return err
	}

	optimizerBody := new(models.OptimizerPostBody)
	optimizerBody.MaxEval = maxIter

	optimizerBody.Knobs = make([]models.Knob, 0)

	for _, item := range o.Prj.Object {
		knob := new(models.Knob)
		knob.Dtype = item.Info.Dtype
		knob.Name = item.Name
		knob.Type = item.Info.Type
		knob.Ref = item.Info.Ref
		knob.Range = item.Info.Scope
		knob.Items = item.Info.Items
		knob.Step = item.Info.Step
		knob.Options = item.Info.Options
		optimizerBody.Knobs = append(optimizerBody.Knobs, *knob)
	}

	respPostIns, err := optimizerBody.Post()
	if err != nil {
		return err
	}
	if respPostIns.Status != "OK" {
		log.Errorf(respPostIns.Status)
		return fmt.Errorf("create task failed: %s", respPostIns.Status)
	}

	log.Infof("create task id is %s", respPostIns.TaskID)
	url := config.GetURL(config.OptimizerURI)
	optimizerPutURL = fmt.Sprintf("%s/%s", url, respPostIns.TaskID)

	log.Infof("optimizer put url is: %s", optimizerPutURL)

	optimization = o
	minEval = ""
	iter = 0

	benchmark := BenchMark{Content: nil}
	if err := benchmark.DynamicTuned(ch); err != nil {
		return err
	}

	return nil
}

/*
DynamicTuned method using bayes algorithm to search the best performance parameters
*/
func (bench *BenchMark) DynamicTuned(ch chan *PB.AckCheck) error {
	var eval string
	var err error
	if bench.Content != nil {
		eval = string(bench.Content)

		optimizationTerm := fmt.Sprintf("The %dth optimization result is: %s\n"+
			" The %dth evaluation value is: %s", iter, respPutIns.Param, iter, eval)
		ch <- &PB.AckCheck{Name: optimizationTerm}

		log.Info(optimizationTerm)
		err = utils.WriteFile(config.TuningFile, optimizationTerm+"\n", config.FilePerm,
			os.O_APPEND|os.O_WRONLY)
		if err != nil {
			log.Error(err)
			return err
		}

		floatEval, err := strconv.ParseFloat(eval, 64)
		if err != nil {
			log.Error(err)
			return err
		}

		if minEval == "" {
			minEval = eval
		}

		floatMinEval, err := strconv.ParseFloat(minEval, 64)
		if err != nil {
			log.Error(err)
			return err
		}

		if floatEval < floatMinEval {
			minEval = eval
		}
	}

	os.Setenv("ITERATION", strconv.Itoa(iter))

	optPutBody := new(models.OptimizerPutBody)
	optPutBody.Iterations = iter
	optPutBody.Value = eval
	respPutIns, err = optPutBody.Put(optimizerPutURL)
	if err != nil {
		log.Errorf("get setting parameter error: %v", err)
		return err
	}

	log.Infof("setting params is: %s", respPutIns.Param)
	if err := optimization.Prj.RunSet(respPutIns.Param); err != nil {
		log.Error(err)
		return err
	}

	log.Info("set the parameter success")
	if err := optimization.Prj.RestartProject(); err != nil {
		log.Error(err)
		return err
	}
	log.Info("restart project success")

	if iter == maxIter {
		optimizationTerm := fmt.Sprintf("\n The final optimization result is: %s\n"+
			" The final evaluation value is: %s", respPutIns.Param, minEval)
		ch <- &PB.AckCheck{Name: optimizationTerm, Status: utils.SUCCESS}
		err := utils.WriteFile(config.TuningFile, optimizationTerm+"\n", config.FilePerm,
			os.O_APPEND|os.O_WRONLY)
                if err != nil {
			log.Error(err)
			return err
		}

		if err = deleteTask(optimizerPutURL); err != nil {
			log.Error(err)
		}
		optimizer.Unlock()
		return nil
	}

	iter++
	return nil
}

func deleteTask(url string) error {
	resp, err := http.Delete(url)
	if err != nil {
		log.Info("delete task faild:", err)
		return err
	}
	defer resp.Body.Close()
	return nil
}
