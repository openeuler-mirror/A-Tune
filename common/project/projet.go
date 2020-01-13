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
	Project     string     `yaml:"project"`
	Iterations  int        `yaml:"iterations"`
	Benchmark   string     `yaml:"benchmark"`
	Evaluations []Evaluate `yaml:"evaluations"`
}

// YamlPrjSvr :store the server yaml project
type YamlPrjSvr struct {
	Project       string       `yaml:"project"`
	Object        []YamlPrjObj `yaml:"object"`
	Maxiterations int          `yaml:"maxiterations"`
	Startworkload string       `yaml:"startworkload"`
	Stopworkload  string       `yaml:"stopworkload"`
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
	Name string  `yaml:"name"`
	Info YamlObj `yaml:"info"`
}

// LoadProject method load the tuning yaml
func LoadProject(path string) (*YamlPrjSvr, error) {
	exist, err := utils.PathExist(path)
	if err != nil {
		return nil, err
	}

	if !exist {
		return nil, fmt.Errorf("the path %s doesn't exist", path)
	}

	return newProject(path)
}

func newProject(path string) (*YamlPrjSvr, error) {
	info, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, err
	}

	prj := new(YamlPrjSvr)
	if err := yaml.Unmarshal(info, prj); err != nil {
		return nil, fmt.Errorf("parse %s failed : %s", path, err)
	}

	return prj, nil
}

// BenchMark method call the benchmark script
func (y *YamlPrjCli) BenchMark() (string, error) {
	benchStr := make([]string, 0)

	cmd := exec.Command("sh", "-c", y.Benchmark)
	benchOutByte, err := cmd.CombinedOutput()

	if err != nil {
		return "", fmt.Errorf("failed to run benchmark, err: %v", err)
	}
	for _, evaluation := range y.Evaluations {
		newScript := strings.Replace(evaluation.Info.Get, "$out", string(benchOutByte), -1)
		cmd := exec.Command("sh", "-c", newScript)
		bout, err := cmd.Output()
		if err != nil {
			log.Error(err)
			return strings.Join(benchStr, ","), err
		}
		floatout, err := strconv.ParseFloat(strings.Replace(string(bout), "\n", "", -1), 64)
		if err != nil {
			log.Error(err)
			return strings.Join(benchStr, ","), err
		}

		out := strconv.FormatFloat((floatout * float64(evaluation.Info.Weight) / 100), 'E', -1, 64)
		if evaluation.Info.Type == "negative" {
			out = "-" + out
		}
		benchStr = append(benchStr, evaluation.Name+"="+out)
	}

	return strings.Join(benchStr, ","), nil
}

// RunSet method call the set script to set the value
func (y *YamlPrjSvr) RunSet(optStr string) error {
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
		out, err := ExecCommand(obj.Info.GetScript)
		if err != nil {
			return err
		}

		if strings.TrimSpace(string(out)) == paraMap[obj.Name] {
			log.Infof("%s need not be set, value is %s", obj.Name, paraMap[obj.Name])
			continue
		}
		script := obj.Info.SetScript
		newScript := strings.Replace(script, "$value", paraMap[obj.Name], -1)
		log.Info("set script:", newScript)
		_, err = ExecCommand(newScript)
		if err != nil {
			return err
		}
	}
	return nil
}

// RestartProject method call the StartWorkload and StopWorkload script to restart the service
func (y *YamlPrjSvr) RestartProject() error {
	startWorkload := y.Startworkload
	stopWorkload := y.Stopworkload

	needRestart := false

	for _, obj := range y.Object {
		if obj.Info.Needrestart == "true" {
			needRestart = true
			break
		}
	}
	if needRestart {
		out, err := ExecCommand(stopWorkload)
		if err != nil {
			return err
		}
		log.Debug(string(out))

		out, err = ExecCommand(startWorkload)
		if err != nil {
			return err
		}
		log.Debug(string(out))
	}

	return nil
}

//exec command and get result
func ExecCommand(script string) ([]byte, error) {
	cmd := exec.Command("sh", "-c", script)
	out, err := cmd.CombinedOutput()
	return out, err
}
