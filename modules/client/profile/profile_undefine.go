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

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
)

var profileDeleteCommand = cli.Command{
	Name:      "undefine",
	Usage:     "delete the specified workload type",
	ArgsUsage: "WORKLOAD_TYPE",
	Description: func() string {
		desc := "\n   delete the specified workload type, only self defined workload type can be delete.\n"
		return desc
	}(),
	Action: profileDelete,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.undefine",
		Desc:    "opt profile system",
		NewInst: newProfileDelete,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile service : %s\n", err)
		return
	}
}

func newProfileDelete(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileDeleteCommand, nil
}

func profileDeleteCheck(ctx *cli.Context) error {
	if err := utils.CheckArgs(ctx, 1, utils.ConstExactArgs); err != nil {
		return err
	}

	return nil
}

func profileDelete(ctx *cli.Context) error {
	if err := profileDeleteCheck(ctx); err != nil {
		return err
	}
	workloadType := ctx.Args().Get(0)

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	reply, err := svc.Delete(CTX.Background(), &PB.DefineMessage{WorkloadType: workloadType})
	if err != nil {
		fmt.Println(err)
		return err
	}
	if reply.GetStatus() != "OK" {
		fmt.Println(reply.GetStatus())
		return nil
	}
	fmt.Println("delete workload type success")
	return nil
}
