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

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var profileDeleteCommand = cli.Command{
	Name:      "undefine",
	Usage:     "delete the specified profile",
	ArgsUsage: "[profile]",
	Description: func() string {
		desc := "\n   delete the specified profile.\n"
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
	profileName := ctx.Args().Get(0)
	if !utils.IsInputStringValid(profileName) {
		return fmt.Errorf("input:%s is invalid", profileName)
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	reply, err := svc.Delete(CTX.Background(), &PB.ProfileInfo{Name: profileName})
	if err != nil {
		return err
	}
	if reply.GetStatus() != "OK" {
		fmt.Println(reply.GetStatus())
		return nil
	}
	fmt.Println("delete application profile success")
	return nil
}
