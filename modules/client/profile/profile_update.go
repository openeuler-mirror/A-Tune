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
	"io/ioutil"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
)

var profileUpdateCommand = cli.Command{
	Name:      "update",
	Usage:     "update the optimization content of the specified workload type and profile name",
	ArgsUsage: "WORKLOAD_TYPE PROFILE_NAME PROFILE_FILE",
	Description: func() string {
		desc := `
	 update the optimization content of the specified workload type and profile name,
	     example: atune-adm update idle default ./update.conf
	`
		return desc
	}(),
	Action: profileUpdate,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.update",
		Desc:    "opt profile system",
		NewInst: newProfileUpdate,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile service : %s\n", err)
		return
	}
}

func newProfileUpdate(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileUpdateCommand, nil
}

func profileUpdateCheck(ctx *cli.Context) error {
	if err := utils.CheckArgs(ctx, 3, utils.ConstExactArgs); err != nil {
		return err
	}

	file := ctx.Args().Get(2)
	exist, err := utils.PathExist(file)
	if err != nil {
		return err
	}
	if !exist {
		return fmt.Errorf("file %s is not exist", file)
	}

	return nil
}

func profileUpdate(ctx *cli.Context) error {
	if err := profileUpdateCheck(ctx); err != nil {
		return err
	}
	workloadType := ctx.Args().Get(0)
	profileName := ctx.Args().Get(1)

	data, err := ioutil.ReadFile(ctx.Args().Get(2))
	if err != nil {
		return err
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	reply, err := svc.Update(CTX.Background(), &PB.DefineMessage{
		WorkloadType: workloadType,
		ProfileName:  profileName,
		Content:      data})
	if err != nil {
		return err
	}
	if reply.GetStatus() != "OK" {
		fmt.Println(reply.GetStatus())
		return nil
	}

	fmt.Println("update workload type success")
	return nil
}
