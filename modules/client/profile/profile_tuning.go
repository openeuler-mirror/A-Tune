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
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	"gitee.com/openeuler/A-Tune/common/project"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
	"io"
	"math"
	"strconv"
	"strings"
	"time"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
)

var profileTunningCommand = cli.Command{
	Name:      "tuning",
	Usage:     "dynamic bayes search optimal parameter sets",
	ArgsUsage: "PROJECT_YAML",
	Flags: []cli.Flag{
		cli.BoolFlag{
			Name:  "restore,r",
			Usage: "restore pre-optimized initial configuration",
		},
		cli.BoolFlag{
			Name:   "restart,c",
			Hidden: false,
			Usage:  "restart the tuning base on the history",
		},
		cli.StringFlag{
			Name:  "project,p",
			Usage: "the project name of the yaml file",
			Value: "",
		},
		cli.BoolFlag{
			Name:   "detail,d",
			Hidden: false,
			Usage:  "display the detail info of tuning message",
		},
	},
	Description: func() string {
		desc := `
	 tuning command usning bayes method dynamic search optimal parameter sets,
	 the PROJECT_YAML which you can refer to Documentation example.yaml.
	     example: atune-adm tuning ./example.yaml
	`
		return desc
	}(),
	Action: profileTunning,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.tuning",
		Desc:    "opt profile system",
		NewInst: newProfileTuningCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile analysis service : %s\n", err)
		return
	}
}

func newProfileTuningCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileTunningCommand, nil
}

func profileTunning(ctx *cli.Context) error {
	if ctx.Bool("restore") {
		return checkRestoreConfig(ctx)
	}

	if err := utils.CheckArgs(ctx, 1, utils.ConstExactArgs); err != nil {
		return err
	}

	yamlPath := ctx.Args().Get(0)
	if !strings.HasSuffix(yamlPath, ".yaml") && !strings.HasSuffix(yamlPath, ".yml") {
		return fmt.Errorf("error: %s is not ends with yaml or yml", yamlPath)
	}

	prj := project.YamlPrjCli{StartsTime: time.Now(), StartIters: 1}
	if err := utils.ParseFile(yamlPath, "yaml", &prj); err != nil {
		return err
	}
	if err := checkTuningPrjYaml(prj); err != nil {
		return err
	}
	err := runTuningRPC(ctx, func(stream PB.ProfileMgr_TuningClient) error {
		finished := make(chan bool)
		errors := make(chan error)
		var init bool = false
		go func() {
			if !ctx.Bool("restart") {
				fmt.Println("Start to benchmark baseline...")
				benchmarkByte, err := prj.BenchMark(true)
				if err != nil {
					fmt.Println("benchmark result:", benchmarkByte)
					errors <- err
				}
				finished <- true
				return
			}
			finished <- true
		}()
		var state PB.TuningMessageStatus = PB.TuningMessage_JobInit
		content := &PB.TuningMessage{
			Name:                ctx.String("project"),
			Restart:             ctx.Bool("restart"),
			RandomStarts:        prj.RandomStarts,
			Engine:              prj.Engine,
			State:               state,
			Content:             []byte(strconv.Itoa(int(prj.Iterations))),
			FeatureFilterEngine: prj.FeatureFilterEngine,
			FeatureFilterCycle:  prj.FeatureFilterCycle,
			FeatureFilterIters:  prj.FeatureFilterIters,
		}
		if err := stream.Send(content); err != nil {
			return fmt.Errorf("client sends failure, error: %v", err)
		}

		for {
			reply, err := stream.Recv()
			if err == io.EOF {
				break
			}
			if err != nil {
				return err
			}
			state := reply.GetState()
			switch state {
			case PB.TuningMessage_JobInit:
				prj.StartIters = 1
				if err := stream.Send(&PB.TuningMessage{State: PB.TuningMessage_JobRestart, Content: []byte(strconv.Itoa(int(prj.Iterations)))}); err != nil {
					return fmt.Errorf("client sends failure, error: %v", err)
				}
			case PB.TuningMessage_BenchMark:
				if !init {
					select {
					case err := <-errors:
						return err
					case <-finished:
						break
					}
					init = true
				}
				if ctx.Bool("restart") {
					prj.SetHistoryEvalBase(reply.GetTuningLog())
				}
				prj.Params = string(reply.GetContent())
				benchmarkByte, err := prj.BenchMark(reply.GetFeatureFilter())
				if err != nil {
					fmt.Println("benchmark result:", benchmarkByte)
					return err
				}

				currentTime := time.Now()
				if reply.GetFeatureFilter() {
					fmt.Printf(" Used time: %s, Total Time: %s, Current Progress......(%d/%d)\n",
						currentTime.Sub(prj.StartsTime).Round(time.Second).String(),
						time.Duration(int64(currentTime.Sub(prj.StartsTime).Round(time.Second).Seconds())+prj.TotalTime)*time.Second,
						prj.StartIters, prj.FeatureFilterIters)
				} else {
					fmt.Printf(" Used time: %s, Total Time: %s, Best Performance: %.2f, Performance Improvement Rate: %s%%\n",
						currentTime.Sub(prj.StartsTime).Round(time.Second).String(),
						time.Duration(int64(currentTime.Sub(prj.StartsTime).Round(time.Second).Seconds())+prj.TotalTime)*time.Second,
						math.Abs(prj.EvalMin), prj.ImproveRateString(prj.EvalMin))
				}
				if ctx.Bool("detail") && !reply.GetFeatureFilter() {
					fmt.Printf(" The %dth recommand parameters is: %s\n"+
						" The %dth evaluation value: %s(%s%%)\n", prj.StartIters, prj.Params, prj.StartIters, strings.Replace(benchmarkByte, "-", "", -1), prj.ImproveRateString(prj.EvalCurrent))
				}
				prj.StartIters++
				if err := stream.Send(&PB.TuningMessage{State: PB.TuningMessage_BenchMark, Content: []byte(benchmarkByte)}); err != nil {
					return fmt.Errorf("client sends failure, error: %v", err)
				}
			case PB.TuningMessage_Threshold:
				benchmarkByte, err := prj.Threshold()
				if err != nil {
					fmt.Println("benchmark result:", benchmarkByte)
					return err
				}
				if err := stream.Send(&PB.TuningMessage{State: PB.TuningMessage_BenchMark, Content: []byte(benchmarkByte)}); err != nil {
					return fmt.Errorf("client sends failure, error: %v", err)
				}
			case PB.TuningMessage_Display:
				fmt.Printf(" %s\n", string(reply.GetContent()))
			case PB.TuningMessage_Detail:
				if ctx.Bool("detail") {
					fmt.Printf(" %s\n", string(reply.GetContent()))
				}
			case PB.TuningMessage_Ending:
				fmt.Printf(" Baseline Performance is: %.2f\n", math.Abs(prj.EvalBase))
				fmt.Printf(" %s\n", string(reply.GetContent()))
				fmt.Printf(" tuning finished\n")
				goto End
			}

		}
	End:
		return nil
	})

	if err != nil {
		return err
	}
	return nil
}

func checkRestoreConfig(ctx *cli.Context) error {
	if err := checkTuningCtx(ctx); err != nil {
		return err
	}

	err := runTuningRPC(ctx, func(stream PB.ProfileMgr_TuningClient) error {
		content := &PB.TuningMessage{Name: ctx.String("project"), State: PB.TuningMessage_Restore}
		if err := stream.Send(content); err != nil {
			return fmt.Errorf("client sends failure, error: %v", err)
		}

		for {
			reply, err := stream.Recv()
			if err == io.EOF {
				break
			}
			if err != nil {
				return err
			}
			state := reply.GetState()
			switch state {
			case PB.TuningMessage_Display:
				fmt.Printf(" %s\n", string(reply.GetContent()))
			case PB.TuningMessage_Ending:
				fmt.Printf("tuning finished\n")
				goto End
			}
		}
	End:
		return nil
	})

	if err != nil {
		return err
	}

	return nil
}

func checkTuningCtx(ctx *cli.Context) error {
	if ctx.String("project") == "" {
		_ = cli.ShowCommandHelp(ctx, "tuning")
		return fmt.Errorf("error: project name must be specified")
	}

	if len(ctx.String("project")) > 128 {
		return fmt.Errorf("error: project name length is longer than 128 charaters")
	}

	return nil
}

func checkTuningPrjYaml(prj project.YamlPrjCli) error {
	if len(prj.Project) < 1 || len(prj.Project) > 128 {
		return fmt.Errorf("error: project name must be no less than 1 " +
			"and no greater than 128 in yaml or yml")
	}

	if len(prj.Benchmark) < 1 {
		return fmt.Errorf("error: benchmark must be specified in yaml or yml")
	}

	if len(prj.Evaluations) > 10 {
		return fmt.Errorf("error: evaluations must be no greater than 10 "+
			"in project %s", prj.Project)
	}

	if prj.RandomStarts < 0 {
		return fmt.Errorf("error: random_starts must be >= 0 "+
			"in project %s", prj.Project)
	}

	if prj.Iterations < prj.RandomStarts {
		return fmt.Errorf("error: iterations must be greater than random_starts "+
			"in project %s", prj.Project)
	}

	if prj.FeatureFilterCycle < 0 {
		return fmt.Errorf("error: feature_filter_cycle must be >= 0 "+
			"in project %s", prj.Project)
	}
	if prj.FeatureFilterCycle > 0 && prj.FeatureFilterIters < 0 {
		return fmt.Errorf("error: feature_filter_iters must be > 0 "+
			"in project %s", prj.Project)
	}
	return nil
}

func runTuningRPC(ctx *cli.Context, sendTask func(stream PB.ProfileMgr_TuningClient) error) error {
	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}

	defer c.Close()
	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Tuning(CTX.Background())
	if err != nil {
		return err
	}

	if err := sendTask(stream); err != nil {
		return err
	}

	if err := stream.CloseSend(); err != nil {
		return fmt.Errorf("failed to close stream, error: %v", err)
	}

	return nil
}
