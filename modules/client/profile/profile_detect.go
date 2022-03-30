/*
 * Copyright (c) 2020 Huawei Technologies Co., Ltd.
 * A-Tune is licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Create: 2020-09-30
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

var detectCommand = cli.Command{
	Name:      "detect",
	Usage:     "detect the misclassified data",
	UsageText: "atune-adm detect OPTIONS",
	Flags: []cli.Flag{
		cli.StringFlag{
			Name:  "app_name,n",
			Usage: "the name actual running workload",
			Value: "",
		},
		cli.StringFlag{
			Name:  "detect_file, f",
			Usage: "specify the file to be detect",
			Value: "",
		},
	},
	Description: func() string {
		desc := `
	 detect the error of misclassified data. you have to input the actual type
	 and application name of the workload.
		 example: atune-adm detect --app_name=mysql
	 you can also specify the file you want to detect.
		 example: atune-adm detect --app_name=mysql --detect_file=test-1011`
		return desc
	}(),
	Action: detect,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.detect",
		Desc:    "opt profile system",
		NewInst: newDetectCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load collection service : %s\n", err)
		return
	}
}

func newDetectCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return detectCommand, nil
}

func Contains(slice []string, s string) int {
	for index, value := range slice {
		if value == s {
			return index
		}
	}
	return -1
}

func checkDetectCtx(ctx *cli.Context) error {
    var app_names = []string{"ceph", "default", "hadoop_hdd", "hpc", "kvm", "mariadb", "mariadb_docker", "mariadb_kvm",
    "mysql", "nginx_http_long", "nginx_https_long", "nginx_http_sort", "nginx_https_short", "redis", "speccpu", "specjbb"}
	appName := ctx.String("app_name")
	if appName == "" {
		_ = cli.ShowCommandHelp(ctx, "detect")
		return fmt.Errorf("error: app_name must be specified")
	}
	r := Contains(app_names, appName)
	if r==-1 {
		return fmt.Errorf("input:%s is invalid", appName)
	}

	return nil
}

func detect(ctx *cli.Context) error {
	if err := checkDetectCtx(ctx); err != nil {
		return err
	}

	appName := ctx.String("app_name")
	detectPath := ctx.String("detect_file")

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Detecting(CTX.Background(), &PB.DetectMessage{AppName: appName, DetectPath: detectPath})
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
	fmt.Println("the app name :", appName)
	return nil
}
