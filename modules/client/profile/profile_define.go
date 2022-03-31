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
	"io/ioutil"

	"github.com/go-ini/ini"
	"github.com/urfave/cli"
	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/utils"
)

var profileDefineCommand = cli.Command{
	Name:      "define",
	Usage:     "create a new application profile",
	ArgsUsage: "[service_type] [application_name] [scenario_name] [profile_path]",
	Description: func() string {
		desc := `
	 create a new application profile which can not be already exist, for example
	 below, create a new service_type with test_service, application_name with
	 test_app, scenario_name with test_scenario, profile_path with ./example.conf.
	      example: atune-adm define test_service test_app test_scenario ./example.conf
	`
		return desc
	}(),
	Action: profileDefined,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.define",
		Desc:    "opt profile system",
		NewInst: newProfileDefine,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load profile service : %s\n", err)
		return
	}
}

func newProfileDefine(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return profileDefineCommand, nil
}

func profileDefineCheck(ctx *cli.Context) error {
	if err := utils.CheckArgs(ctx, 4, utils.ConstExactArgs); err != nil {
		return err
	}

	file := ctx.Args().Get(3)
	if !utils.IsInputStringValid(file) {
		return fmt.Errorf("input:%s is invalid", file)
	}

	exist, err := utils.PathExist(file)
	if err != nil {
		return err
	}
	if !exist {
		return fmt.Errorf("file %s is not exist", file)
	}

	_, err = ini.Load(file)
	if err != nil {
		return fmt.Errorf("load profile failed, file format may be not correct")
	}

	return nil
}

func profileDefined(ctx *cli.Context) error {
	if err := profileDefineCheck(ctx); err != nil {
		return err
	}
	serviceType := ctx.Args().Get(0)
	if !utils.IsInputStringValid(serviceType) {
		return fmt.Errorf("input:%s is invalid", serviceType)
	}
	applicationName := ctx.Args().Get(1)
	if !utils.IsInputStringValid(applicationName) {
		return fmt.Errorf("input:%s is invalid", applicationName)
	}
	scenarioName := ctx.Args().Get(2)
	if !utils.IsInputStringValid(scenarioName) {
		return fmt.Errorf("input:%s is invalid", scenarioName)
	}

	data, err := ioutil.ReadFile(ctx.Args().Get(3))
	if err != nil {
		return err
	}

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	reply, err := svc.Define(CTX.Background(), &PB.DefineMessage{
		ServiceType:     serviceType,
		ApplicationName: applicationName,
		ScenarioName:    scenarioName,
		Content:         data})
	if err != nil {
		return err
	}
	if reply.GetStatus() != "OK" {
		fmt.Println(reply.GetStatus())
		return nil
	}
	fmt.Println("define a new application profile success")
	return nil
}
