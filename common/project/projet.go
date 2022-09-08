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

package project

import (
	"bytes"
	"fmt"
	"math"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"time"

	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/utils"
)

const (
	LESS      = "less"
	GREATER   = "greater"
	DEPEND_ON = "depend_on"
	RELY_ON   = "rely_on"
	MULTIPLE  = "multiple"
)

// Evaluate :store the evaluate object
type Evaluate struct {
	Name string   `yaml:"name"`
	Info EvalInfo `yaml:"info"`
}

// EvalInfo :store the evaluation object
type EvalInfo struct {
	Get       string  `yaml:"get"`
	Type      string  `yaml:"type"`
	Weight    int64   `yaml:"weight"`
	Threshold float64 `yaml:"threshold"`
}

// YamlPrjCli :store the client yaml project
type YamlPrjCli struct {
	Project             string     `yaml:"project"`
	Iterations          int32      `yaml:"iterations"`
	RandomStarts        int32      `yaml:"random_starts"`
	Benchmark           string     `yaml:"benchmark"`
	Engine              string     `yaml:"engine"`
	FeatureFilterEngine string     `yaml:"feature_filter_engine"`
	FeatureFilterCycle  int32      `yaml:"feature_filter_cycle"`
	FeatureFilterIters  int32      `yaml:"feature_filter_iters"`
	FeatureFilterCount  int32      `yaml:"feature_filter_count"`
	FeatureSelector     string     `yaml:"feature_selector"`
	SplitCount          int32      `yaml:"split_count"`
	EvalFluctuation     float64    `yaml:"eval_fluctuation"`
	Evaluations         []Evaluate `yaml:"evaluations"`
	StartsTime          time.Time  `yaml:"-"`
	TotalTime           int64      `yaml:"-"`
	EvalMin             float64    `yaml:"-"`
	EvalMinArray        []float64  `yaml:"-"`
	EvalBaseArray       []float64  `yaml:"-"`
	EvalCurrent         float64    `yaml:"-"`
	EvalCurrentArray    []float64  `yaml:"-"`
	StartIters          int32      `yaml:"-"`
	TotalIters          int32      `yaml:"-"`
	Params              string     `yaml:"-"`
	FeatureFilter       bool       `yaml:"-"`
	Baseline            bool       `yaml:"-"`
}

// YamlPrjSvr :store the server yaml project
type YamlPrjSvr struct {
	Project       string        `yaml:"project"`
	Object        []*YamlPrjObj `yaml:"object"`
	Maxiterations int32         `yaml:"maxiterations"`
	Startworkload string        `yaml:"startworkload"`
	Stopworkload  string        `yaml:"stopworkload"`
}

// YamlObj :yaml Object
type YamlObj struct {
	Name        string    `yaml:"name"`
	Desc        string    `yaml:"desc"`
	GetScript   string    `yaml:"get"`
	SetScript   string    `yaml:"set"`
	Needrestart string    `yaml:"needrestart"`
	Skip        bool      `yaml:"skip"`
	Type        string    `yaml:"type"`
	Step        float32   `yaml:"step,omitempty"`
	Items       []float32 `yaml:"items"`
	Options     []string  `yaml:"options"`
	Scope       []float32 `yaml:"scope,flow"`
	Dtype       string    `yaml:"dtype"`
	Ref         string    `yaml:"ref"`
	Except      string    `yaml:"except"`
}

// YamlPrjObj :store the yaml object
type YamlPrjObj struct {
	Name      string          `yaml:"name"`
	Info      YamlObj         `yaml:"info"`
	Relations []*RelationShip `yaml:"relationships"`
	Clusters  []interface{}
}

type RelationShip struct {
	Type    string `yaml:"type"`
	Target  string `yaml:"target"`
	Value   string `yaml:"value"`
	SrcName string `yaml:"src_name"`
}

// BenchMark method call the benchmark script
func (y *YamlPrjCli) BenchMark() (string, string, error) {
	benchStr := make([]string, 0)
	log.Debugf("run benchmark script: %s", y.Benchmark)
	benchOutByte, err := ExecGetOutput(y.Benchmark)
	if err != nil {
		fmt.Println(string(benchOutByte))
		return "", "", fmt.Errorf("failed to run benchmark, err: %v", err)
	}

	var sum float64
	for index, evaluation := range y.Evaluations {
		newScript := strings.Replace(evaluation.Info.Get, "$out", string(benchOutByte), -1)
		bout, err := ExecGetOutput(newScript)
		if err != nil {
			err = fmt.Errorf("failed to exec %s, err: %v", newScript, err)
			return "", "", err
		}

		floatOut, err := strconv.ParseFloat(strings.Replace(string(bout), "\n", "", -1), 64)
		if err != nil {
			log.Debugf("output of benchmark script: %s", string(benchOutByte))
			log.Debugf("output of evaluation script for %s: %s", evaluation.Name, string(bout))
			err = fmt.Errorf("failed to parse result of the evaluation of %s, err: %v", evaluation.Name, err)
			return "", "", err
		}

		if evaluation.Info.Type == "negative" {
			floatOut = -floatOut
		}
		floatOut, _ = strconv.ParseFloat(fmt.Sprintf("%.2f", floatOut), 64)
		y.EvalCurrentArray[index] = floatOut
		if y.Baseline {
			y.EvalBaseArray[index] = floatOut
			y.EvalMinArray[index] = floatOut
		}
		benchStr = append(benchStr, fmt.Sprintf("%s=%.2f", evaluation.Name, floatOut))
	}

	sum = y.calculateBenchMark()

	if utils.IsEquals(y.EvalMin, 0.0) && len(y.Evaluations) == 1 {
		y.EvalMin = sum
	}
	if !y.FeatureFilter && sum < y.EvalMin {
		for index, eval := range y.EvalCurrentArray {
			y.EvalMinArray[index] = eval
		}
		y.EvalMin = sum
	}
	y.EvalCurrent = sum
	y.Baseline = false
	return fmt.Sprintf("evaluations=%.2f", sum), strings.Join(benchStr, ","), nil
}

func (y *YamlPrjCli) BestPerformance() string {
	bestPerformance := make([]string, 0)
	for index, evaluation := range y.Evaluations {
		bestPerformance = append(bestPerformance, fmt.Sprintf("%s=%.2f", evaluation.Name, math.Abs(y.EvalMinArray[index])))
	}
	return strings.Join(bestPerformance, ",")
}

func (y *YamlPrjCli) CurrPerformance() string {
	currPerformance := make([]string, 0)
	for index, evaluation := range y.Evaluations {
		currPerformance = append(currPerformance, fmt.Sprintf("%s=%.2f", evaluation.Name, math.Abs(y.EvalCurrentArray[index])))
	}
	return strings.Join(currPerformance, ",")
}

func (y *YamlPrjCli) BasePerformance() string {
	basePerformance := make([]string, 0)
	for index, evaluation := range y.Evaluations {
		basePerformance = append(basePerformance, fmt.Sprintf("%s=%.2f", evaluation.Name, math.Abs(y.EvalBaseArray[index])))
	}
	return strings.Join(basePerformance, ",")
}

func (y *YamlPrjCli) calculateBenchMark() float64 {
	if len(y.EvalCurrentArray) == 1 {
		return y.EvalCurrentArray[0]
	}

	var sum float64
	for index, evaluation := range y.Evaluations {
		sum += y.improveRate(index) * float64(evaluation.Info.Weight) / 100
	}

	return -sum
}

func (y *YamlPrjCli) improveRate(index int) float64 {
	if y.EvalBaseArray[index] > 0 {
		if y.EvalCurrentArray[index] > y.EvalBaseArray[index] {
			return (y.EvalBaseArray[index] - y.EvalCurrentArray[index]) / y.EvalBaseArray[index] * 100
		}
		return (y.EvalBaseArray[index] - y.EvalCurrentArray[index]) / y.EvalCurrentArray[index] * 100
	}
	if y.EvalCurrentArray[index] > y.EvalBaseArray[index] {
		return (y.EvalCurrentArray[index] - y.EvalBaseArray[index]) / y.EvalCurrentArray[index] * 100
	}
	return (y.EvalCurrentArray[index] - y.EvalBaseArray[index]) / y.EvalBaseArray[index] * 100
}

// Threshold return the threshold, which replace with the benchmark result.
// it is used when the parameters is not match with the relations
func (y *YamlPrjCli) Threshold() (string, string, error) {
	benchStr := make([]string, 0)
	for index, evaluation := range y.Evaluations {
		floatOut := evaluation.Info.Threshold
		if evaluation.Info.Type == "negative" {
			floatOut = -floatOut
		}
		y.EvalCurrentArray[index] = floatOut
		benchStr = append(benchStr, fmt.Sprintf("%s=%.2f", evaluation.Name, floatOut))
	}
	sum := y.calculateBenchMark()
	return fmt.Sprintf("evaluations=%.2f", sum), strings.Join(benchStr, ","), nil
}

// SetHistoryEvalBase method call the set the current EvalBase to history baseline
func (y *YamlPrjCli) SetHistoryEvalBase(tuningHistory *PB.TuningHistory) {
	if !y.Baseline {
		return
	}

	for index, eval := range strings.Split(tuningHistory.BaseEval, ",") {
		evalStr := strings.Split(eval, "=")
		if len(evalStr) != 2 {
			continue
		}
		evalFloat, err := strconv.ParseFloat(evalStr[1], 64)
		if err != nil {
			return
		}
		y.EvalBaseArray[index] = evalFloat
	}

	for index, eval := range strings.Split(tuningHistory.MinEval, ",") {
		evalStr := strings.Split(eval, "=")
		if len(evalStr) != 2 {
			continue
		}
		evalFloat, err := strconv.ParseFloat(evalStr[1], 64)
		if err != nil {
			return
		}
		y.EvalMinArray[index] = evalFloat
	}

	y.EvalMin, _ = strconv.ParseFloat(tuningHistory.SumEval, 64)

	y.TotalTime = tuningHistory.TotalTime
	y.StartIters = tuningHistory.Starts
	y.Baseline = false
}

// ImproveRateString method return the string format of performance improve rate
func (y *YamlPrjCli) ImproveRateString(current float64) string {
	if len(y.Evaluations) > 1 {
		return fmt.Sprintf("%.2f", -current)
	}

	if y.EvalBaseArray[0] < 0 {
		return fmt.Sprintf("%.2f", (current-y.EvalBaseArray[0])/y.EvalBaseArray[0]*100)
	}
	return fmt.Sprintf("%.2f", (y.EvalBaseArray[0]-current)/math.Abs(current)*100)
}

// RunSet method call the set script to set the value
func (y *YamlPrjSvr) RunSet(optStr string) (error, []string) {
	paraMap := make(map[string]string)
	paraSlice := strings.Split(optStr, ",")
	for _, para := range paraSlice {
		kvs := strings.SplitN(para, "=", 2)
		if len(kvs) < 2 {
			continue
		}
		paraMap[kvs[0]] = strings.TrimSpace(kvs[1])
	}
	log.Infof("before change paraMap: %+v\n", paraMap)
	scripts := make([]string, 0)
	for _, obj := range y.Object {
		if obj.Info.Skip {
			log.Infof("item %s is skiped", obj.Name)
			continue
		}

		var objName string
		active := true
		for _, relation := range obj.Relations {
			if relation.Type == RELY_ON && paraMap[relation.Target] != relation.Value {
				active = false
				break
			}
			if relation.Type == DEPEND_ON && paraMap[relation.Target] != relation.Value {
				continue
			}

			if relation.Type == DEPEND_ON {
				objName = relation.SrcName
			}

			if relation.Type == MULTIPLE {
				targetValue, _ := strconv.ParseFloat(paraMap[relation.Target], 32)
				objValue, _ := strconv.ParseFloat(paraMap[obj.Name], 32)
				paraMap[obj.Name] = strconv.Itoa(int(targetValue * objValue))
				continue
			}
		}

		if !active {
			log.Infof("%s value is not match the relations", obj.Name)
			continue
		}

		script := obj.Info.SetScript
		var newScript string

		if len(strings.Fields(paraMap[obj.Name])) > 1 {
			newScript = strings.Replace(script, "$value", "\""+paraMap[obj.Name]+"\"", -1)
		} else {
			newScript = strings.Replace(script, "$value", paraMap[obj.Name], -1)
		}

		newScript = strings.Replace(newScript, "$name", objName, -1)
		scripts = append(scripts, newScript)

		objGroupStr := ""
		reg := regexp.MustCompile(`-[0-9]+$`)
		res := reg.FindAllString(obj.Name, -1)
		if len(res) != 0 {
			for wordPos := 1; wordPos < len(res[0]); wordPos++ {
				objGroupStr += string(res[0][wordPos])
			}
			objGroup, err := strconv.Atoi(string(objGroupStr))
			if err != nil {
				return err, nil
			}
			if objGroup == 0 {
				if utils.InArray(obj.Clusters, config.Address) {
					log.Infof("set script for %s: %s", obj.Name, newScript)
					_, err := ExecCommand(newScript)
					if err != nil {
						return fmt.Errorf("failed to exec %s, err: %v", newScript, err), nil
					}
				} else {
					log.Infof("no operation")
				}
			}
		} else {
			if utils.InArray(obj.Clusters, config.Address) {
				log.Infof("set script for %s: %s", obj.Name, newScript)
				_, err := ExecCommand(newScript)
				if err != nil {
					return fmt.Errorf("failed to exec %s, err: %v", newScript, err), nil
				}
			} else {
				log.Infof("no operation")
			}
		}
	}
	log.Infof("after change paraMap: %+v\n", paraMap)
	return nil, scripts
}

// RestartProject method call the StartWorkload and StopWorkload script to restart the service
func (y *YamlPrjSvr) RestartProject() (error, []string) {
	startWorkload := y.Startworkload
	stopWorkload := y.Stopworkload

	needRestart := false

	for _, obj := range y.Object {
		if obj.Info.Needrestart == "true" {
			needRestart = true
			break
		}
	}

	scripts := make([]string, 0)
	if needRestart {
		log.Debugf("stop workload script is: %s", stopWorkload)
		out, err := ExecCommand(stopWorkload)
		if err != nil {
			return fmt.Errorf("failed to exec %s, err: %v", stopWorkload, err), nil
		}
		log.Debug(string(out))
		scripts = append(scripts, stopWorkload)

		log.Debugf("start workload script is: %s", startWorkload)
		out, err = ExecCommand(startWorkload)
		if err != nil {
			return fmt.Errorf("failed to exec %s, err: %v", startWorkload, err), nil
		}
		log.Debug(string(out))

		scripts = append(scripts, startWorkload)
	}

	return nil, scripts
}

// MergeProject two yaml project to one object
func (y *YamlPrjSvr) MergeProject(prj *YamlPrjSvr) {
	y.Object = append(y.Object, prj.Object...)
}

// MatchRelations method check if the params match the relations
// if less or greater is not match, return false, else return true
func (y *YamlPrjSvr) MatchRelations(optStr string) bool {
	paraMap := make(map[string]string)
	paraSlice := strings.Split(optStr, ",")
	for _, para := range paraSlice {
		kvs := strings.Split(para, "=")
		if len(kvs) < 2 {
			continue
		}
		paraMap[kvs[0]] = kvs[1]
	}

	for _, obj := range y.Object {
		if obj.Info.Skip {
			log.Infof("item %s is skiped", obj.Name)
			continue
		}
		for _, relation := range obj.Relations {
			if relation.Type != LESS && relation.Type != GREATER {
				continue
			}

			targetValue, _ := strconv.Atoi(paraMap[relation.Target])
			objValue, _ := strconv.Atoi(paraMap[obj.Name])

			if relation.Type == LESS && objValue > targetValue {
				return false
			}

			if relation.Type == GREATER && objValue < targetValue {
				return false
			}
		}
	}
	return true
}

//exec command and get result
func ExecCommand(script string) ([]byte, error) {
	var buf bytes.Buffer
	cmd := exec.Command("sh", "-c", script)
	cmd.Stdout = &buf
	cmd.Stderr = &buf
	err := cmd.Start()
	if err != nil {
		return buf.Bytes(), err
	}
	_, err = cmd.Process.Wait()
	return buf.Bytes(), err
}

//exec command and get complete output including subprocess
func ExecGetOutput(script string) ([]byte, error) {
	cmd := exec.Command("sh", "-c", script)
	return cmd.CombinedOutput()
}
