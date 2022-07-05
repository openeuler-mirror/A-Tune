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
	"errors"
	"io"
	"math/rand"
	"strings"
	"time"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var profileCommand = cli.Command{
	Name:      "profile",
	Usage:     "active the specified profile and check the actived profile",
	UsageText: "atune-adm profile [profile]",
	Description: func() string {
		desc := `
	 1. active the specified profile,for example,avtive the idle profile.
	     example: atune-adm profile idle `
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
	if ctx.NArg() != 1 {
		_ = cli.ShowCommandHelp(ctx, "profile")
		return fmt.Errorf("only one workloadload type can be set")
	}

	return nil
}

func profile(ctx *cli.Context) error {
	if err := profileCmdCheck(ctx); err != nil {
		return err
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
			var errStr = err.Error()
			if strings.Contains(errStr, "desc = ") {
				errStr = strings.Split(errStr, "desc = ")[1]
			}
			return errors.New(errStr)
		}

		utils.Print(reply)
		num := rand.Intn(3)
		time.Sleep(time.Duration(num+1) * time.Second)
	}

	return nil
}
