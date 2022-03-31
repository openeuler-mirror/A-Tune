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
	"strings"
	"io"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var profileCheckCommand = cli.Command{
	Name:      "check",
	Usage:     "check system basic information",
	UsageText: "atune-adm check",
	Description: func() string {
		desc := "\n    check system basic information\n"
		return desc
	}(),
	Action: profileCheck,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.check",
		Desc:    "opt profile system",
		NewInst: newProfileCheckCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile check service : %s\n", err)
		return
	}
}

func newProfileCheckCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileCheckCommand, nil
}

func profileCheck(ctx *cli.Context) error {
	var err error
	if err = utils.CheckArgs(ctx, 0, utils.ConstExactArgs); err != nil {
		return err
	}

	var c *client.Client
	c, err = client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.CheckInitProfile(CTX.Background(), &PB.ProfileInfo{})
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
		utils.Print(reply)
	}
	fmt.Println("\nActive profile check:")
	stream, err = svc.CheckActiveProfile(CTX.Background(), &PB.ProfileInfo{})
	if err != nil {
		return err
	}

	for {
		reply, err := stream.Recv()

		if err == io.EOF {
			break
		}

		if err != nil {
			if strings.Contains(err.Error(), "no active profile or more than 1 active profile") {
				fmt.Println("no active profile or more than 1 active profile")
				break
			}
			return err
		}
		utils.Print(reply)
	}

	fmt.Println("\nCheck finished")
	return nil
}
