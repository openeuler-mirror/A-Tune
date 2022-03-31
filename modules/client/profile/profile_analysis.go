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

package profile

import (
	"fmt"
	"io"
	"os"
	"syscall"
	"os/exec"
	"time"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var profileAnalysisCommand = cli.Command{
	Name:      "analysis",
	Usage:     "analysis system workload type",
	ArgsUsage: "[APP_NAME]",
	Flags: []cli.Flag{
		cli.StringFlag{
			Name:  "model, m",
			Usage: "specified the self trained model to analysis",
			Value: "",
		},
		cli.BoolFlag{
			Name:  "characterization, c",
			Usage: "only analysis the workload type",
		},
		cli.StringFlag{
			Name:  "times, t",
			Usage: "specify the collection times",
			Value: "",
		},
		cli.StringFlag{
			Name:  "script, s",
			Usage: "specify the script to be executed",
			Value: "",
		},
	},
	Description: func() string {
		desc := `
	 analysis the system's workload type and optimization performance.
	 you can specified the app name, but it's just for reference only.
	     example: atune-adm analysis mysql
	 you can specify the self trained model to analysis, which only
	 can be end with .m.
	     example: atune-adm analysis --model ./self_trained.m
	 you can only analysis the workload type.
	     example: atune-adm analysis --characterization
	you can specify the collecting times.
	     example: atune-adm analysis -t 5
	 you can specify the script to be executed.
	     example: atune-adm analysis -s script.sh`
		return desc
	}(),
	Action: profileAnalysis,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.analysis",
		Desc:    "opt profile system",
		NewInst: newProfileAnalysisCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile analysis service : %s\n", err)
		return
	}
}

func newProfileAnalysisCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileAnalysisCommand, nil
}

func profileAnalysis(ctx *cli.Context) error {
	appname := ""
	if ctx.NArg() > 2 {
		return fmt.Errorf("only one or zero argument required")
	}
	if ctx.NArg() == 1 {
		appname = ctx.Args().Get(0)
		if !utils.IsInputStringValid(appname) {
			return fmt.Errorf("input:%s is invalid", appname)
		}
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	modelFile := ctx.String("model")
	if modelFile != "" && !utils.IsInputStringValid(modelFile) {
		return fmt.Errorf("input:%s is invalid", modelFile)
	}

	times := ctx.String("times")
	if times != "" && !utils.IsInputStringValid(times) {
		return fmt.Errorf("input:%s is invalid", times)
	}

	var pid int
	id := string(time.Now().Unix())
	cmd := ctx.String("script")
	svc := PB.NewProfileMgrClient(c.Connection())
	flag := ""
	if cmd != "" {
		cmdline := "sh " + cmd + ">> log.txt"
		ch := make(chan int)
		go ExecScript(cmdline, ch)
		pid = <-ch
		times = "1"
		flag = "start"
	}
	stream, _ := svc.Analysis(CTX.Background(), &PB.AnalysisMessage{Name: appname, Model: modelFile, 
		Characterization: ctx.Bool("characterization"), Times: times, Flag: flag, Id:id})

	endCollect := false
	for {
		reply, err := stream.Recv()

		if err == io.EOF {
			break
		}

		if err != nil {
			return err
		}
		utils.Print(reply)
		if cmd != "" && !checkPid(pid) && !endCollect {
			svcend := PB.NewProfileMgrClient(c.Connection())
			endCollect = true
			_, _ = svcend.Analysis(CTX.Background(), &PB.AnalysisMessage{Name: appname, Model: modelFile,
				Characterization: ctx.Bool("characterization"), Times: times, Flag: "end", Id:id})
		}
	}

	return nil
}

func checkPid(pid int) bool {
	process, err := os.FindProcess(pid)
	if err != nil {
		return false
	}

	err = process.Signal(syscall.Signal(0))
	if err != nil {
		return false
	}
	return true
}

func ExecScript(cmdline string, ch chan int) {
	cmd := exec.Command("/bin/bash", "-c", cmdline)
	cmd.Stdout = os.Stdout
	err := cmd.Start()
	if err != nil {
		return 
	}
	ch <- cmd.Process.Pid
	err = cmd.Wait()
	if err != nil {
		return
	}
}
