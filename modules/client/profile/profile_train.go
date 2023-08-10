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
	"gitee.com/openeuler/A-Tune/common/config"
)

var trainCommand = cli.Command{
	Name:      "train",
	Usage:     "train a new model with self collected data",
	UsageText: "atune-adm train OPTIONS",
	Flags: []cli.Flag{
		cli.StringFlag{
			Name:  "data_path,d",
			Usage: "the path where has data for training",
			Value: "",
		},
		cli.StringFlag{
			Name:  "model_name,m",
			Usage: "the model name of generate model",
			Value: "",
		},
	},
	Description: func() string {
		desc := `
	 training a new model with the self collected data, data_path option specified
	 the path that storage the collected data, the collected data must have more 
	 than two workload type. model_name specified the name of model to be generated
	 the trained model, which must be end with .m.
	     example: atune-adm train --data_path=/home/data --model_name=trained.m`
		return desc
	}(),
	Action: train,
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile.train",
		Desc:    "opt profile system",
		NewInst: newTrainCmd,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load collection service : %s\n", err)
		return
	}
}

func newTrainCmd(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	return trainCommand, nil
}

func checkTrainCtx(ctx *cli.Context) error {
	dataPath := ctx.String("data_path")
	if dataPath == "" {
		_ = cli.ShowCommandHelp(ctx, "train")
		return fmt.Errorf("error: data_path must be specified")
	}
	if !utils.IsInputStringValid(dataPath) {
		return fmt.Errorf("input:%s is invalid", dataPath)
	}

	modelName := ctx.String("model_name")
	if modelName == "" {
		_ = cli.ShowCommandHelp(ctx, "train")
		return fmt.Errorf("error: model_name must be specified")
	}
	if !utils.IsInputStringValid(modelName) {
		return fmt.Errorf("input:%s is invalid", modelName)
	}

	return nil
}

func train(ctx *cli.Context) error {
	if err := checkTrainCtx(ctx); err != nil {
		return err
	}

	dataPath, err := filepath.Abs(ctx.String("data_path"))
	if err != nil {
		return err
	}

	modelName := ctx.String("model_name")

	c, err := client.NewClientFromContext(ctx)
	if err != nil {
		return err
	}
	defer c.Close()

	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Training(CTX.Background(), &PB.TrainMessage{DataPath: dataPath, ModelName: modelName})
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
	modelPath := fmt.Sprintf("%s/models/%s", config.DefaultAnalysisPath, modelName)
	fmt.Println("the model generate path:", modelPath)
	return nil
}
