/*
 * Copyright (c) 2020 Huawei Technologies Co., Ltd.
 * A-Tune is licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Create: 2020-07-23
 */

package profile

import (
	"fmt"
	"io"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var profileGenerateCommand = cli.Command{
	Name:      "generate",
	Usage:     "generate the tuning yaml profile based on the rules",
	UsageText: "atune-adm generate OPTIONS",
	Flags: []cli.Flag{
		cli.StringFlag{
			Name:  "project,p",
			Usage: "the filename and project name to be generated",
			Value: "default",
		},
	},
	Description: func() string {
		desc := "generate the tuning yaml profile depend on the rules"
		return desc
	}(),
	Action: profileGenerate,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.generate",
		Desc:    "opt profile generate",
		NewInst: newProfileGenerate,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile generate service : %s\n", err)
		return
	}
}

func newProfileGenerate(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileGenerateCommand, nil
}

func profileGenerate(ctx *cli.Context) error {
	if err := utils.CheckArgs(ctx, 0, utils.ConstExactArgs); err != nil {
		return err
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Generate(CTX.Background(), &PB.ProfileInfo{Name: ctx.String("project")})
	if err != nil {
		fmt.Println(err)
		return nil
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
	}

	return nil
}
