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
	"io/ioutil"
	"os"
	"path"
	"strconv"
	"strings"
	"time"
)

// Optimizer : the type implement the bayes serch service
type Optimizer struct {
	Prj *project.YamlPrjSvr
}

//BenchMark : the benchmark data
type BenchMark struct {
	Content []byte
}

var optimizerPutURL string
var optimization *Optimizer
var finalEval string
var minEvalSum float64
var respPutIns *models.RespPutBody
var iter int
var maxIter int
var startIterTime string

// InitTuned method for init tuning
func (o *Optimizer) InitTuned(ch chan *PB.AckCheck, askIter int) error {
	//dynamic profle setting
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

	initConfigure := ""
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

		out, err := project.ExecCommand(item.Info.GetScript)
		if err != nil {
			return fmt.Errorf("faild to exec %s, err: %v", item.Info.GetScript, err)
		}
		initConfigure += strings.TrimSpace(knob.Name+"="+string(out)) + ","
	}

	err = utils.WriteFile(path.Join(config.DefaultTempPath,
		o.Prj.Project+config.TuningRestoreConfig), initConfigure,
		config.FilePerm, os.O_WRONLY|os.O_CREATE|os.O_TRUNC)
	if err != nil {
		log.Error(err)
		return err
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
	iter = 0

	benchmark := BenchMark{Content: nil}
	if _, err := benchmark.DynamicTuned(ch); err != nil {
		return err
	}

	return nil
}

/*
DynamicTuned method using bayes algorithm to search the best performance parameters
*/
func (bench *BenchMark) DynamicTuned(ch chan *PB.AckCheck) (bool, error) {
	var evalValue string
	var err error
	if bench.Content != nil {
		evalValue, err = bench.evalParsing(ch)
		if err != nil {
			return true, err
		}
	}

	os.Setenv("ITERATION", strconv.Itoa(iter))

	optPutBody := new(models.OptimizerPutBody)
	optPutBody.Iterations = iter
	optPutBody.Value = evalValue
	respPutIns, err = optPutBody.Put(optimizerPutURL)
	if err != nil {
		log.Errorf("get setting parameter error: %v", err)
		return true, err
	}

	log.Infof("setting params is: %s", respPutIns.Param)
	if err := optimization.Prj.RunSet(respPutIns.Param); err != nil {
		log.Error(err)
		return true, err
	}

	log.Info("set the parameter success")
	if err := optimization.Prj.RestartProject(); err != nil {
		log.Error(err)
		return true, err
	}
	log.Info("restart project success")

	startIterTime = time.Now().Format(config.DefaultTimeFormat)

	if iter == maxIter {
		finalEval := strings.Replace(finalEval, "=-", "=", -1)
		optimizationTerm := fmt.Sprintf("\n The final optimization result is: %s\n"+
			" The final evaluation value is: %s", respPutIns.Param, finalEval)
		log.Info(optimizationTerm)
		ch <- &PB.AckCheck{Name: optimizationTerm, Status: utils.SUCCESS}

		if err = deleteTask(optimizerPutURL); err != nil {
			log.Error(err)
		}
		return true, nil
	}

	iter++
	return false, nil
}

//restore tuning config
func (o *Optimizer) RestoreConfigTuned() error {
	tuningRestoreConf := path.Join(config.DefaultTempPath, o.Prj.Project+config.TuningRestoreConfig)
	exist, err := utils.PathExist(tuningRestoreConf)
	if err != nil {
		return err
	}
	if !exist {
		log.Errorf("%s project has not been executed the dynamic optimizer search", o.Prj.Project)
		return fmt.Errorf("%s project has not been executed the dynamic optimizer search",
			o.Prj.Project)
	}

	content, err := ioutil.ReadFile(tuningRestoreConf)
	if err != nil {
		log.Error(err)
		return err
	}

	log.Infof("restoring params is: %s", string(content))
	if err := o.Prj.RunSet(string(content)); err != nil {
		log.Error(err)
		return err
	}

	log.Infof("restore %s project params success", o.Prj.Project)
	return nil
}

func (bench *BenchMark) evalParsing(ch chan *PB.AckCheck) (string, error) {
	eval := string(bench.Content)
	positiveEval := strings.Replace(eval, "=-", "=", -1)
	optimizationTerm := fmt.Sprintf("The %dth optimization result is: %s\n"+
		" The %dth evaluation value is: %s", iter, respPutIns.Param, iter, positiveEval)
	ch <- &PB.AckCheck{Name: optimizationTerm}
	log.Info(optimizationTerm)

	endIterTime := time.Now().Format(config.DefaultTimeFormat)
	iterInfo := make([]string, 0)
	iterInfo = append(iterInfo, strconv.Itoa(iter))
	iterInfo = append(iterInfo, startIterTime)
	iterInfo = append(iterInfo, endIterTime)
	iterInfo = append(iterInfo, positiveEval)
	iterInfo = append(iterInfo, respPutIns.Param)
	output := strings.Join(iterInfo, "|")

	err := utils.WriteFile(config.TuningFile, output+"\n", config.FilePerm,
		os.O_APPEND|os.O_WRONLY)
	if err != nil {
		log.Error(err)
		return "", err
	}

	evalValue := make([]string, 0)
	evalSum := 0.0
	for _, benchStr := range strings.Split(eval, ",") {
		kvs := strings.Split(benchStr, "=")
		if len(kvs) < 2 {
			continue
		}

		floatEval, err := strconv.ParseFloat(kvs[1], 64)
		if err != nil {
			log.Error(err)
			return "", err
		}

		evalSum += floatEval
		evalValue = append(evalValue, kvs[1])
	}

	if iter == 1 || evalSum < minEvalSum {
		minEvalSum = evalSum
		finalEval = eval
	}
	return strings.Join(evalValue, ","), nil
}

func deleteTask(url string) error {
	resp, err := http.Delete(url)
	if err != nil {
		log.Error("delete task faild:", err)
		return err
	}
	defer resp.Body.Close()
	return nil
}
