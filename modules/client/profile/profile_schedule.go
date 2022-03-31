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

var scheduleCommand = cli.Command{
	Name:  "schedule",
	Usage: "schedule",
	Flags: []cli.Flag{
		cli.StringFlag{
			Name:  "pid,t",
			Usage: "--pid=<pid1>,<pid2>...",
		},
		cli.StringFlag{
			Name:  "strategy,s",
			Usage: "--strategy=<listed in atune-adm schedule --list>",
		},
	},
	ArgsUsage: "[arguments...]",
	Description: func() string {
		desc := "\n    schedule: schedule resource for instrances\n"
		return desc
	}(),
	Action: schedule,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.schedule",
		Desc:    "opt profile system",
		NewInst: newScheduleCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load schedule service : %s\n", err)
		return
	}
}

func newScheduleCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return scheduleCommand, nil
}

func schedule(ctx *cli.Context) error {
	appname := ctx.String("pid")
	strategy := ctx.String("strategy")

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Schedule(CTX.Background(), &PB.ScheduleMessage{App: appname, Type: "", Strategy: strategy})
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
