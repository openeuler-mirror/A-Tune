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

	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var collectionCommand = cli.Command{
	Name:      "collection",
	Usage:     "collect the system data for training",
	UsageText: "atune-adm collection OPTIONS",
	Flags: []cli.Flag{
		cli.StringFlag{
			Name:  "filename,f",
			Usage: "filename of the generated data file",
			Value: "",
		},
		cli.IntFlag{
			Name:  "interval,i",
			Usage: "time interval for collecting data",
			Value: 5,
		},
		cli.IntFlag{
			Name:  "duration,d",
			Usage: "the duration for collecting data",
			Value: 1200,
		},
		cli.StringFlag{
			Name:  "output_path,o",
			Usage: "the output path of the collecting data",
			Value: "",
		},
		cli.StringFlag{
			Name:  "disk,b",
			Usage: "the disk to be collected",
			Value: "",
		},
		cli.StringFlag{
			Name:  "network,n",
			Usage: "the network to be collected",
			Value: "",
		},
		cli.StringFlag{
			Name:  "app_type,t",
			Usage: "the app type of the collected data",
			Value: "",
		},
	},
	Description: func() string {
		desc := `
	 collect data for train machine learning model, you must set the command options
	 which has no default value, the output_path must be a absolute path.
	     example: atune-adm collection -f mysql -i 5 -d 1200 -o /home -b sda -n eth0 -t mysql`
		return desc
	}(),
	Action: collection,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.collection",
		Desc:    "opt profile system",
		NewInst: newCollectionCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load collection service : %s\n", err)
		return
	}
}

func newCollectionCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return collectionCommand, nil
}

func checkCollectionCtx(ctx *cli.Context) error {
	if ctx.String("filename") == "" {
		_ = cli.ShowCommandHelp(ctx, "collection")
		return fmt.Errorf("error: filename must be specified")
	}

	if len(ctx.String("filename")) > 128 {
		return fmt.Errorf("error: filename length is longer than 128 charaters")
	}

	if ctx.String("disk") == "" {
		_ = cli.ShowCommandHelp(ctx, "collection")
		return fmt.Errorf("error: disk block must be specified")
	}
	if ctx.String("network") == "" {
		_ = cli.ShowCommandHelp(ctx, "collection")
		return fmt.Errorf("error: network must be specified")
	}

	if ctx.String("app_type") == "" {
		_ = cli.ShowCommandHelp(ctx, "collection")
		return fmt.Errorf("error: app type must be specified")
	}

	if ctx.String("output_path") == "" {
		_ = cli.ShowCommandHelp(ctx, "collection")
		return fmt.Errorf("error: output_path must be specified")
	}

	if ctx.Int64("interval") < 1 || ctx.Int64("interval") > 60 {
		return fmt.Errorf("error: collection interval value must be between 1 and 60 seconds")
	}

	if ctx.Int64("duration") < ctx.Int64("interval")*10 {
		return fmt.Errorf("error: collection duration value must be bigger than interval*10")
	}

	if !filepath.IsAbs(ctx.String("output_path")) {
		return fmt.Errorf("error: output path must be absolute path")
	}

	return nil
}

func collection(ctx *cli.Context) error {
	if err := checkCollectionCtx(ctx); err != nil {
		return err
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	outputPath := ctx.String("output_path")
	outputPath, err = filepath.Abs(outputPath)
	if err != nil {
		return err
	}
	message := PB.CollectFlag{
		Interval:   ctx.Int64("interval"),
		Duration:   ctx.Int64("duration"),
		Workload:   ctx.String("filename"),
		OutputPath: outputPath,
		Block:      ctx.String("disk"),
		Network:    ctx.String("network"),
		Type:       ctx.String("app_type"),
	}

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Collection(CTX.Background(), &message)
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
			return err
		}
		utils.Print(reply)
	}

	return nil
}
