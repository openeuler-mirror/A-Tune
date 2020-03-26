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
	SVC "atune/common/service"
	"atune/common/utils"
	"fmt"
	"io"
	"strings"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
)

var profileInfoCommand = cli.Command{
	Name:      "info",
	Usage:     "display profile info corresponding to specified workload type",
	ArgsUsage: "WORKLOAD_TYPE",
	Description: func() string {
		desc := "\n   display profile info corresponding to WORKLOAD_TYPE\n"
		return desc
	}(),
	Action: profileInfo,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.info",
		Desc:    "opt profile system",
		NewInst: newProfileInfoCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile list service : %s\n", err)
		return
	}
}

func newProfileInfoCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileInfoCommand, nil
}

func profileInfoCheck(ctx *cli.Context) error {
	if err := utils.CheckArgs(ctx, 1, utils.ConstExactArgs); err != nil {
		return err
	}

	return nil
}

func profileInfo(ctx *cli.Context) error {
	if err := profileInfoCheck(ctx); err != nil {
		return err
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())

	stream, err := svc.InfoProfile(CTX.Background(), &PB.ProfileInfo{Name: strings.Join(ctx.Args(), " ")})
	if err != nil {
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

		fmt.Print(reply.Name)
	}

	return nil
}
