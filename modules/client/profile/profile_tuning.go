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
	PB "atune/api/profile"
	"atune/common/client"
	"atune/common/project"
	SVC "atune/common/service"
	"atune/common/utils"
	"fmt"
	"io"
	"strconv"
	"strings"

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
		cli.StringFlag{
			Name:  "project,p",
			Usage: "the project name of the yaml file",
			Value: "",
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

	prj := project.YamlPrjCli{}
	if err := utils.ParseFile(yamlPath, "yaml", &prj); err != nil {
		return err
	}
	if err := checkTuningPrjYaml(prj); err != nil {
		return err
	}

	err := runTuningRPC(ctx, func(stream PB.ProfileMgr_TuningClient) error {
		content := &PB.ProfileInfo{Name: prj.Project, Content: []byte(strconv.Itoa(prj.Iterations))}
		if err := stream.Send(content); err != nil {
			return fmt.Errorf("client sends failure, error: %v", err)
		}

		iter := 0
		for {
			reply, err := stream.Recv()
			if err == io.EOF {
				break
			}
			if err != nil {
				return err
			}
			if reply.Status != utils.SUCCESS {
				utils.Print(reply)
				continue
			}
			if iter >= prj.Iterations {
				break
			}

			benchmarkByte, err := prj.BenchMark()
			if err != nil {
				return err
			}
			if err := stream.Send(&PB.ProfileInfo{Content: []byte(benchmarkByte)}); err != nil {
				return fmt.Errorf("client sends failure, error: %v", err)
			}
			iter++
		}
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
		content := &PB.ProfileInfo{Name: ctx.String("project")}
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
			utils.Print(reply)

			if reply.Status == utils.SUCCESS {
				break
			}
		}
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

	if prj.Iterations < 11 {
		return fmt.Errorf("error: iterations must be greater than 10 "+
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

