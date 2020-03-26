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
	"fmt"
	"io"
	"strings"

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
)

var scheduleCommand = cli.Command{
	Name:  "schedule",
	Usage: "schedule",
	Flags: []cli.Flag{
		cli.StringFlag{
			Name:  "type,t",
			Usage: "--type=[cpu|irq|all]",
			Value: "all",
		},
		cli.StringFlag{
			Name:  "strategy,s",
			Usage: "--strategy=[performance|powersave|auto]",
			Value: "auto",
		},
	},
	ArgsUsage: "[arguments...]",
	Description: func() string {
		desc := "\n    schedule: schedule all available resource into system \n"
		return desc
	}(),
	Action: schedule,
}

func newScheduleCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return scheduleCommand, nil
}

func checkScheduleCtx(ctx *cli.Context) error {
	typename := ctx.String("type")
	if !((typename == "cpu") || (typename == "irq") || (typename == "all")) {
		return fmt.Errorf("type have error exist")
	}

	strategy := ctx.String("strategy")
	if !((strategy == "performance") || (strategy == "powersave") || (strategy == "auto")) {
		return fmt.Errorf("strategy have error exist")
	}

	return nil
}

func schedule(ctx *cli.Context) error {
	if err := checkScheduleCtx(ctx); err != nil {
		return err
	}

	appname := strings.Join(ctx.Args(), ",")
	typename := ctx.String("type")
	strategy := ctx.String("strategy")

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Schedule(CTX.Background(), &PB.ScheduleMessage{App: appname, Type: typename, Strategy: strategy})
	if err != nil {
		return err
	}

	for {
		_, err := stream.Recv()
		if err == io.EOF {
			break
		}

		if err != nil {
			return err
		}
	}

	return nil
}
