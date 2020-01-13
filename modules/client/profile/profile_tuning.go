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

package profile

import (
	PB "atune/api/profile"
	"atune/common/client"
	"atune/common/project"
	SVC "atune/common/service"
	"atune/common/utils"
	"fmt"
	"io"
	"io/ioutil"
	"strconv"
	"strings"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	yaml "gopkg.in/yaml.v2"
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
	exist, err := utils.PathExist(yamlPath)
	if err != nil {
		return err
	}

	if !exist {
		return fmt.Errorf("project file %s is not exist", yamlPath)
	}

	if !strings.HasSuffix(yamlPath, ".yaml") && !strings.HasSuffix(yamlPath, ".yml") {
		return fmt.Errorf("project file is not ends with yaml or yml")
	}

	data, err := ioutil.ReadFile(yamlPath)
	if err != nil {
		return err
	}
	prj := project.YamlPrjCli{}
	if err := yaml.Unmarshal(data, &prj); err != nil {
		return err
	}

	if len(prj.Project) < 1 || len(prj.Project) > 128 {
		return fmt.Errorf("project name must be no less than 1 and no greater than 128 in yaml or yml")
	}

	if len(prj.Benchmark) < 1 {
		return fmt.Errorf("benchmark must be specified in yaml or yml")
	}

	if len(prj.Evaluations) > 10 {
		return fmt.Errorf("evaluations must be no greater than 10 in project %s", prj.Project)
	}

	_, err = runTuningRPC(ctx, &PB.ProfileInfo{Name: prj.Project, Content: []byte(strconv.Itoa(prj.Iterations))})
	if err != nil {
		return err
	}

	iter := 0
	for iter < prj.Iterations {
		benchmarkByte, err := prj.BenchMark()
		if err != nil {
			return err
		}

		var status string
		status, err = runTuningRPC(ctx, &PB.ProfileInfo{Content: []byte(benchmarkByte)})
		if err != nil {
			return err
		}

		if status == utils.SUCCESS {
			break
		}

		iter++
	}
	return nil
}

func runTuningRPC(ctx *cli.Context, info *PB.ProfileInfo) (string, error) {
	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return "", err
	}

	defer c.Close()
	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Tuning(CTX.Background(), info)
	if err != nil {
		return "", err
	}

	for {
		reply, err := stream.Recv()

		if err == io.EOF {
			break
		}

		if err != nil {
			return "", err
		}

		utils.Print(reply)

		if reply.Status == utils.SUCCESS {
			return reply.Status, nil
		}
	}

	return "", nil
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

func checkRestoreConfig(ctx *cli.Context) error {
	err := checkTuningCtx(ctx)
	if err != nil {
		return err
	}
	_, err = runTuningRPC(ctx, &PB.ProfileInfo{Name: ctx.String("project")})
	if err != nil {
		return err
	}
	return nil
}

