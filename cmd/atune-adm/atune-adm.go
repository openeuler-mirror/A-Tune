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

package main

import (
	"fmt"
	"os"
	"sort"

	"github.com/urfave/cli"
	
	"gitee.com/openeuler/A-Tune/common/config"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

const (
	usageInfo = `atune-adm is a command line client for atuned AI tuning system`
)

func doBeforeJob(ctx *cli.Context) error {
	return nil
}

func main() {
	app := cli.NewApp()
	app.Name = "atune-adm"
	app.Usage = usageInfo
	app.Version = config.Version

	app.Flags = []cli.Flag{
		cli.StringFlag{
			Name:  "address, a",
			Usage: "atuned address",
			Value: config.DefaultTgtAddr,
		},
		cli.StringFlag{
			Name:  "port, p",
			Usage: "atuned port",
			Value: config.DefaultTgtPort,
		},
	}

	/*
	 * for limitaion of cli, have to fix module load path
	 */

	err := SVC.WalkServices(func(nm string, svc *SVC.ProfileService) error {
		ins, err := svc.NewInst(nil)
		if err != nil {
			return err
		}
		cmd, ok := ins.(cli.Command)
		if !ok {
			fmt.Printf("service %s doesn't implement cli.Command\n", nm)
			return fmt.Errorf("service %s doesn't implement cli.Command", nm)
		}

		app.Commands = append(app.Commands, cmd)

		return nil
	})

	if err != nil {
		fmt.Printf("services init failed:%v", err)
	}

	sort.Sort(cli.CommandsByName(app.Commands))
	app.Before = doBeforeJob
	if err := app.Run(os.Args); err != nil {
		utils.Fatal(err)
	}
}
