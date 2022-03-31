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
	"path/filepath"
	"strings"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var profileUpgradeCommand = cli.Command{
	Name:      "upgrade",
	Usage:     "upgrade the database",
	ArgsUsage: "DB_PATH",
	Description: func() string {
		desc := "\n   upgrade the database with the specified db file\n"
		return desc
	}(),
	Action: profileUpgrade,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "atune.upgrade",
		Desc:    "atune upgrade system",
		NewInst: newProfileUpgradeCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile upgrade service : %s\n", err)
		return
	}
}

func newProfileUpgradeCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileUpgradeCommand, nil
}

func profileUpgrade(ctx *cli.Context) error {
	if err := utils.CheckArgs(ctx, 1, utils.ConstExactArgs); err != nil {
		return err
	}

	dbPath := ctx.Args().Get(0)
	if !utils.IsInputStringValid(dbPath) {
		return fmt.Errorf("input:%s is invalid", dbPath)
	}

	exist, err := utils.PathExist(dbPath)
	if err != nil {
		return err
	}

	if !exist {
		return fmt.Errorf("%s is not exist", dbPath)
	}

	if !strings.HasSuffix(dbPath, ".db") {
		return fmt.Errorf("database format is not correct")
	}

	absPath, _ := filepath.Abs(dbPath)

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())

	stream, err := svc.UpgradeProfile(CTX.Background(), &PB.ProfileInfo{Name: absPath})
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
