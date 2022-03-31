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

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var profileRollbackCommand = cli.Command{
	Name:      "rollback",
	Usage:     "rollback to the system init state",
	UsageText: "atune-adm rollback",
	Description: func() string {
		desc := `rollback the system config to the init state`
		return desc
	}(),
	Action: profileRollback,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.rollback",
		Desc:    "opt profile system",
		NewInst: newProfileRollbackCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile rollback service : %s\n", err)
		return
	}
}

func newProfileRollbackCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileRollbackCommand, nil
}

func profileRollbackCheck(ctx *cli.Context) error {
	if err := utils.CheckArgs(ctx, 0, utils.ConstExactArgs); err != nil {
		return err
	}

	return nil
}

func profileRollback(ctx *cli.Context) error {
	if err := profileRollbackCheck(ctx); err != nil {
		return err
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.ProfileRollback(CTX.Background(), &PB.ProfileInfo{})
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

	return nil
}
