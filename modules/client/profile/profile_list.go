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

	"github.com/bndr/gotabulate"
	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var profileListCommand = cli.Command{
	Name:      "list",
	Usage:     "list support workload type",
	UsageText: "atune-adm list",
	Description: func() string {
		desc := "\n   list current support profiles\n"
		return desc
	}(),
	Action: profileList,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.list",
		Desc:    "opt profile system",
		NewInst: newProfileListCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile list service : %s\n", err)
		return
	}
}

func newProfileListCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileListCommand, nil
}

func profileListCheck(ctx *cli.Context) error {
	if err := utils.CheckArgs(ctx, 0, utils.ConstExactArgs); err != nil {
		return err
	}

	return nil
}

func profileList(ctx *cli.Context) error {
	if err := profileListCheck(ctx); err != nil {
		return err
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.ListWorkload(CTX.Background(), &PB.ProfileInfo{})
	if err != nil {
		return err
	}

	table := make([][]string, 0)
	fmt.Println("\nSupport profiles:")
	for {
		reply, err := stream.Recv()

		if err == io.EOF {
			break
		}

		if err != nil {
			return err
		}
		row := make([]string, 0)
		row = append(row, reply.ProfileNames)
		row = append(row, reply.Active)

		table = append(table, row)
	}

	tabulate := gotabulate.Create(table)
	tabulate.SetHeaders([]string{"ProfileName", "Active"})
	tabulate.SetAlign("left")
	tabulate.SetMaxCellSize(60)
	tabulate.SetWrapStrings(true)
	fmt.Println(tabulate.Render("grid"))

	return nil
}
