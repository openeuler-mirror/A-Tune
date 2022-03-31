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

package pyservice

import (
	"bufio"
	"io"
	"os"
	"os/exec"
	"os/signal"
	"path"
	"strings"
	"syscall"
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/registry"
)

func init() {
	registry.RegisterDaemonService("pyengine", &PyEngine{})
}

// PyEngine : the struct store the pyEngine conf
type PyEngine struct {
	Cfg *config.Cfg
}

// Init method init the PyEngine service
func (p *PyEngine) Init() error {
	return nil
}

// Set the config of the monitor
func (p *PyEngine) Set(cfg *config.Cfg) {
	p.Cfg = cfg
}

// Run method start the python service
func (p *PyEngine) Run() error {
	cmdSlice := make([]string, 0)
	cmdSlice = append(cmdSlice, "python3")
	cmdSlice = append(cmdSlice, path.Join(config.DefaultAnalysisPath, "app_rest.py"))
	cmdSlice = append(cmdSlice, path.Join(config.DefaultConfPath, "atuned.cnf"))

	cmdStr := strings.Join(cmdSlice, " ")
	log.Debugf("start pyservice: %s", cmdStr)
	cmd := exec.Command("sh", "-c", cmdStr)
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}

	stdout, _ := cmd.StdoutPipe()
	stderr, _ := cmd.StderrPipe()

	go listenToSystemSignals(cmd)
	go logStdout(stdout)
	go logStdout(stderr)

	err := cmd.Start()
	if err != nil {
		log.Errorf("cmd.Start() analysis service failed: %v", err)
		os.Exit(-1)
	}

	err = cmd.Wait()

	if err != nil {
		log.Errorf("cmd.Run() analysis failed with: %v", err)
		os.Exit(-1)
	}

	return nil
}

func logStdout(stdout io.ReadCloser) {
	scanner := bufio.NewScanner(stdout)
	for scanner.Scan() {
		line := scanner.Text()
		log.Debug(line)
	}
}

func listenToSystemSignals(cmd *exec.Cmd) {
	signalChan := make(chan os.Signal, 1)

	signal.Notify(signalChan, os.Interrupt, syscall.SIGTERM)
	<-signalChan
	_ = syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL)
	os.Exit(100)
}
