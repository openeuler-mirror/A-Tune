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
	"fmt"
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/utils"
	"os/exec"
	"strconv"
	"strings"
	"time"
)

const (
	LESS      = "less"
	GREATER   = "greater"
	DEPEND_ON = "depend_on"
	RELY_ON   = "rely_on"
	MULTIPLE  = "multiple"
)

const (
	BASE_BENCHMARK_VALUE = "baseValue"
	MIN_BENCHMARK_VALUE  = "minValue"
)

// Evaluate :store the evaluate object
type Evaluate struct {
	Name string   `yaml:"name"`
	Info EvalInfo `yaml:"info"`
}

// EvalInfo :store the evaluation object
type EvalInfo struct {
	Get       string `yaml:"get"`
	Type      string `yaml:"type"`
	Weight    int64  `yaml:"weight"`
	Threshold int64  `yaml:"threshold"`
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
	Evaluations         []Evaluate `yaml:"evaluations"`
	StartsTime          time.Time  `yaml:"-"`
	TotalTime           int64      `yaml:"-"`
	EvalMin             float64    `yaml:"-"`
	EvalBase            float64    `yaml:"-"`
	EvalCurrent         float64    `yaml:"-"`
	StartIters          int32      `yaml:"-"`
	Params              string     `yaml:"-"`
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
	Name        string   `yaml:"name"`
	Desc        string   `yaml:"desc"`
	GetScript   string   `yaml:"get"`
	SetScript   string   `yaml:"set"`
	Needrestart string   `yaml:"needrestart"`
	Skip        bool     `yaml:"skip"`
	Type        string   `yaml:"type"`
	Step        float32  `yaml:"step,omitempty"`
	Items       []int64  `yaml:"items"`
	Options     []string `yaml:"options"`
	Scope       []int64  `yaml:"scope,flow"`
	Dtype       string   `yaml:"dtype"`
	Ref         string   `yaml:"ref"`
}

// YamlPrjObj :store the yaml object
type YamlPrjObj struct {
	Name      string          `yaml:"name"`
	Info      YamlObj         `yaml:"info"`
	Relations []*RelationShip `yaml:"relationships"`
}

type RelationShip struct {
	Type    string `yaml:"type"`
	Target  string `yaml:"target"`
	Value   string `yaml:"value"`
	SrcName string `yaml:"src_name"`
}

// BenchMark method call the benchmark script
func (y *YamlPrjCli) BenchMark(featureFilter bool) (string, error) {
	benchStr := make([]string, 0)

	benchOutByte, err := ExecCommand(y.Benchmark)
	if err != nil {
		fmt.Println(string(benchOutByte))
		return "", fmt.Errorf("failed to run benchmark, err: %v", err)
	}

	var sum float64
	for _, evaluation := range y.Evaluations {
		newScript := strings.Replace(evaluation.Info.Get, "$out", string(benchOutByte), -1)
		bout, err := ExecCommand(newScript)
		if err != nil {
			err = fmt.Errorf("failed to exec %s, err: %v", newScript, err)
			return strings.Join(benchStr, ","), err
		}

		floatOut, err := strconv.ParseFloat(strings.Replace(string(bout), "\n", "", -1), 64)
		if err != nil {
			err = fmt.Errorf("failed to parse float, err: %v", err)
			return strings.Join(benchStr, ","), err
		}

		out := strconv.FormatFloat(floatOut*float64(evaluation.Info.Weight)/100, 'f', -1, 64)
		if evaluation.Info.Type == "negative" {
			out = "-" + out
			sum += -floatOut
		} else {
			sum += floatOut
		}
		benchStr = append(benchStr, evaluation.Name+"="+out)
	}

	if !featureFilter {
		if sum < y.EvalMin {
			y.EvalMin = sum
		}
	}
	if utils.IsEquals(y.EvalBase, 0.0) {
		y.EvalBase = sum
		y.EvalMin = sum
	}
	y.EvalCurrent = sum
	return strings.Join(benchStr, ","), nil
}

// Threshold return the threshold, which replace with the benchmark result.
// it is used when the parameters is not match with the relations
func (y *YamlPrjCli) Threshold() (string, error) {
	benchStr := make([]string, 0)
	for _, evaluation := range y.Evaluations {
		out := strconv.FormatFloat(float64(evaluation.Info.Threshold)*float64(evaluation.Info.Weight)/100, 'f', -1, 64)
		if evaluation.Info.Type == "negative" {
			out = "-" + out
		}
		benchStr = append(benchStr, evaluation.Name+"="+out)
	}
	return strings.Join(benchStr, ","), nil
}

// SetHistoryEvalBase method call the set the current EvalBase to history baseline
func (y *YamlPrjCli) SetHistoryEvalBase(tuningHistory *PB.TuningHistory) {
	if !utils.IsEquals(y.EvalBase, 0.0) {
		return
	}

	evaluation := strings.Split(tuningHistory.BaseEval, "=")
	if len(evaluation) != 2 {
		return
	}

	evalBase, _ := strconv.ParseFloat(evaluation[1], 64)
	y.EvalBase = evalBase

	minEval := strings.Split(tuningHistory.MinEval, "=")
	if len(minEval) != 2 {
		return
	}

	y.EvalMin, _ = strconv.ParseFloat(minEval[1], 64)

	y.TotalTime = tuningHistory.TotalTime
	y.StartIters = tuningHistory.Starts
}

// ImproveRateString method return the string format of performance improve rate
func (y *YamlPrjCli) ImproveRateString(current float64) string {
	if y.EvalBase < 0 {
		return fmt.Sprintf("%.2f", (current-y.EvalBase)/y.EvalBase*100)
	}

	return fmt.Sprintf("%.2f", (y.EvalBase-current)/current*100)
}

// RunSet method call the set script to set the value
func (y *YamlPrjSvr) RunSet(optStr string) (error, string) {
	paraMap := make(map[string]string)
	paraSlice := strings.Split(optStr, ",")
	for _, para := range paraSlice {
		kvs := strings.Split(para, "=")
		if len(kvs) < 2 {
			continue
		}
		paraMap[kvs[0]] = kvs[1]
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

		out, err := ExecCommand(obj.Info.GetScript)
		if err != nil {
			return fmt.Errorf("failed to exec %s, err: %v", obj.Info.GetScript, err), ""
		}

		if strings.TrimSpace(string(out)) == paraMap[obj.Name] {
			log.Infof("%s need not be set, value is %s", obj.Name, paraMap[obj.Name])
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
		log.Info("set script:", newScript)
		_, err = ExecCommand(newScript)
		if err != nil {
			return fmt.Errorf("failed to exec %s, err: %v", newScript, err), ""
		}
		scripts = append(scripts, newScript)
	}
	log.Infof("after change paraMap: %+v\n", paraMap)
	return nil, strings.Join(scripts, ",")
}

// RestartProject method call the StartWorkload and StopWorkload script to restart the service
func (y *YamlPrjSvr) RestartProject() (error, string) {
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
		out, err := ExecCommand(stopWorkload)
		if err != nil {
			return fmt.Errorf("failed to exec %s, err: %v", stopWorkload, err), ""
		}
		log.Debug(string(out))
		scripts = append(scripts, stopWorkload)

		log.Debugf("start workload script is: %s", startWorkload)
		out, err = ExecCommand(startWorkload)
		if err != nil {
			return fmt.Errorf("failed to exec %s, err: %v", startWorkload, err), ""
		}
		log.Debug(string(out))

		scripts = append(scripts, startWorkload)
	}

	return nil, strings.Join(scripts, ",")
}

// MergeProject two yaml project to one object
func (y *YamlPrjSvr) MergeProject(prj *YamlPrjSvr) error {
	for _, obj := range prj.Object {
		y.Object = append(y.Object, obj)
	}
	return nil
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
	cmd := exec.Command("sh", "-c", script)
	return cmd.CombinedOutput()
}
