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

package project

import (
	"atune/common/log"
	"atune/common/utils"
	"fmt"
	"io/ioutil"
	"os/exec"
	"strconv"
	"strings"

	yaml "gopkg.in/yaml.v2"
)

// Evaluate :store the evaluate object
type Evaluate struct {
	Name string   `yaml : "name"`
	Info EvalInfo `yaml : "info"`
}

// EvalInfo :store the evaluation object
type EvalInfo struct {
	Get       string `yaml : "get"`
	Type      string `yaml : "type"`
	Weight    int64  `yaml : "weight"`
	Threshold int64  `yaml : "threshold"`
}

// YamlPrj :store the yaml project
type YamlPrj struct {
	Object        []YamlPrjObj `yaml : "object"`
	Startworkload string       `yaml : "startworkload"`
	Stopworkload  string       `yaml : "stopworkload"`
	Iterations    int          `yaml : "iterations"`
	Benchmark     string       `yaml : "benchmark"`
	Evaluations   []Evaluate   `yaml : "evaluations"`
}

// YamlObj :yaml Object
type YamlObj struct {
	Name        string   `yaml:"name"`
	Desc        string   `yaml:"desc"`
	GetScript   string   `yaml:"get"`
	SetScript   string   `yaml:"set"`
	Needrestart string   `yaml:"needrestart"`
	Type        string   `yaml:"type"`
	Step        int64    `yaml:"step"`
	Items       []int64  `yaml:"items"`
	Options     []string `yaml:"options"`
	Scope       []int64  `yaml:"scope,flow"`
	Dtype       string   `yaml:"dtype"`
	Ref         string   `yaml:"ref"`
}

// YamlPrjObj :store the yaml object
type YamlPrjObj struct {
	Name string  `yaml : "name"`
	Info YamlObj `yaml : "info"`
}

// LoadProject method load the tuning yaml
func LoadProject(path string) (*YamlPrj, error) {
	exist, err := utils.PathExist(path)
	if err != nil {
		return nil, err
	}

	if !exist {
		return nil, fmt.Errorf("The path %s doesn't exist", path)
	}

	return newProject(path)
}

func newProject(path string) (*YamlPrj, error) {
	info, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, err
	}

	prj := new(YamlPrj)
	if err := yaml.Unmarshal(info, prj); err != nil {
		return nil, fmt.Errorf("Parse %s failed : %s", path, err)
	}

	return prj, nil
}

// BenchMark method call the benchmark script
func (y *YamlPrj) BenchMark() ([]byte, error) {
	log.Info("start to benchmark the performance")
	cmd := exec.Command("sudo", "sh", "-c", y.Benchmark)
	benchOutByte, err := cmd.CombinedOutput()

	if err != nil {
		return nil, err
	}
	return benchOutByte, nil
}

// Evaluation method get the evaluation value from the benchmark result
func (y *YamlPrj) Evaluation(benchmarkByte []byte) (string, error) {
	benchmarkOut := string(benchmarkByte)

	benchStr := ""
	for _, evaluation := range y.Evaluations {
		newScript := strings.Replace(evaluation.Info.Get, "$out", benchmarkOut, -1)
		cmd := exec.Command("sudo", "sh", "-c", newScript)
		bout, err := cmd.Output()
		if err != nil {
			log.Error(err)
			return benchStr, err
		}
		floatout, err := strconv.ParseFloat(strings.Replace(string(bout), "\n", "", -1), 64)
		if err != nil {
			log.Error(err)
			return benchStr, err
		}

		out := strconv.FormatFloat((floatout * float64(evaluation.Info.Weight) / 100), 'E', -1, 64)
		if evaluation.Info.Type == "negative" {
			out = "-" + out
		}
		benchStr = benchStr + out + ","
	}
	benchStr = benchStr[:len(benchStr)-1]
	return benchStr, nil
}

// RunSet method call the set script to set set the value
func (y *YamlPrj) RunSet(optStr string) error {
	paraMap := make(map[string]string)
	paraSlice := strings.Split(optStr, ",")
	for _, para := range paraSlice {
		kvs := strings.Split(para, "=")
		paraMap[kvs[0]] = kvs[1]
	}
	for _, obj := range y.Object {
		obj.Info.Ref = paraMap[obj.Name]
	}

	for _, obj := range y.Object {
		script := obj.Info.SetScript
		newScript := strings.Replace(script, "$value", obj.Info.Ref, -1)
		log.Info("set script:", newScript)
		cmd := exec.Command("sudo", "sh", "-c", newScript)
		err := cmd.Run()
		if err != nil {
			return err
		}
	}
	return nil
}

// RestartProject method call the StartWorkload and StopWorkload script to restart the service
func (y *YamlPrj) RestartProject() error {
	startWorkload := y.Startworkload
	stopWorkload := y.Stopworkload

	needRestart := false
	for _, obj := range y.Object {
		if obj.Info.Needrestart == "true" {
			needRestart = true
			break
		}
	}
	if needRestart == true {
		cmd := exec.Command("sudo", "sh", "-c", stopWorkload)
		out, err := cmd.CombinedOutput()
		log.Debug(string(out))

		if err != nil {
			return err
		}

		cmd = exec.Command("sudo", "sh", "-c", startWorkload)
		out, err = cmd.CombinedOutput()
		log.Debug(string(out))

		if err != nil {
			return err
		}
	}

	return nil
}
