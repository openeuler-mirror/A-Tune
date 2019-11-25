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
	SVC "atune/common/service"
	"atune/common/utils"
	"fmt"
	"io"
	"math/rand"
	"strings"
	"time"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
)

var profileCommand = cli.Command{
	Name:      "profile",
	Usage:     "active the specified workload type and check the actived workload type",
	UsageText: "atune-adm profile [OPTIONS] [WORKLOAD_TYPE]",
	Flags: []cli.Flag{
		cli.BoolFlag{
			Name:   "check,c",
			Usage:  "check the actived workload type",
			Hidden: false,
		},
	},
	Description: func() string {
		desc := `
	 1. active the specified workload_type,for example,avtive the idle workload type.
	     example: atune-adm profile idle
	 2. check the actived workload type.
	     example: atune-adm profile --check`
		return desc
	}(),
	Action: profile,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile",
		Desc:    "opt profile system",
		NewInst: newProfileCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile service : %s\n", err)
		return
	}
}

func newProfileCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileCommand, nil
}

func profileCmdCheck(ctx *cli.Context) error {
	if ctx.NArg() > 1 {
		cli.ShowCommandHelp(ctx, "profile")
		return fmt.Errorf("only one workloadload type can be set")
	}

	if ctx.NArg() < 1 &&  !ctx.Bool("check") {
		cli.ShowCommandHelp(ctx, "profile")
		return fmt.Errorf("profile command can be active one workload type, or with --check")
	}

	if ctx.NArg() == 1 &&  ctx.Bool("check") {
		cli.ShowCommandHelp(ctx, "profile")
		return fmt.Errorf("profile args and --check can not be set at the same time")
	}

	return nil
}

func profile(ctx *cli.Context) error {
	if err := profileCmdCheck(ctx); err != nil {
		return err
	}

	if ctx.Bool("check") {
		return profileActiveCheck(ctx)
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Profile(CTX.Background(), &PB.ProfileInfo{Name: strings.Join(ctx.Args(), " ")})
	if err != nil {
		fmt.Println(err)
		return err
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
		num := rand.Intn(3)
		time.Sleep(time.Duration(num+1) * time.Second)
	}

	return nil
}

func profileActiveCheck(ctx *cli.Context) error {
	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())

	stream, err := svc.CheckActiveProfile(CTX.Background(), &PB.ProfileInfo{})
	for {
		reply, err := stream.Recv()

		if err == io.EOF {
			break
		}

		if err != nil {
			return err
		}
		utils.Print(reply)
		num := rand.Intn(3)
		time.Sleep(time.Duration(num+1) * time.Second)
	}

	return nil
}
