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

package tuning

import (
	PB "atune/api/profile"
	"atune/common/client"
	"atune/common/config"
	"atune/common/http"
	"atune/common/log"
	"atune/common/models"
	"atune/common/project"
	"atune/common/utils"
	"fmt"
	"golang.org/x/net/context"
	"io"
	"io/ioutil"
	"os"
	"path"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// Optimizer : the type implement the bayes serch service
type Optimizer struct {
	Prj             *project.YamlPrjSvr
	Content         []byte
	Iter            int
	MaxIter         int
	OptimizerPutURL string
	FinalEval       string
	MinEvalSum      float64
	RespPutIns      *models.RespPutBody
	StartIterTime   string
}

// InitTuned method for init tuning
func (o *Optimizer) InitTuned(ch chan *PB.AckCheck) error {
	clientIter, err := strconv.Atoi(string(o.Content))
	if err != nil {
		return err
	}

	log.Infof("begin to dynamic optimizer search, client ask iterations:%d", clientIter)
	ch <- &PB.AckCheck{Name: fmt.Sprintf("begin to dynamic optimizer search")}

	//dynamic profle setting
	o.MaxIter = clientIter
	if o.MaxIter > o.Prj.Maxiterations {
		log.Infof("project:%s max iterations:%d", o.Prj.Project, o.Prj.Maxiterations)
		ch <- &PB.AckCheck{Name: fmt.Sprintf("server project %s max iterations %d\n",
			o.Prj.Project, o.Prj.Maxiterations)}
	}

	if err := utils.CreateDir(config.DefaultTempPath, 0750); err != nil {
		return err
	}

	projectName := fmt.Sprintf("project %s\n", o.Prj.Project)
	err = utils.WriteFile(config.TuningFile, projectName, config.FilePerm,
		os.O_WRONLY|os.O_CREATE|os.O_TRUNC)
	if err != nil {
		log.Error(err)
		return err
	}

	initConfigure := make([]string, 0)
	optimizerBody := new(models.OptimizerPostBody)
	optimizerBody.MaxEval = o.MaxIter
	optimizerBody.Knobs = make([]models.Knob, 0)
	for _, item := range o.Prj.Object {
		knob := new(models.Knob)
		knob.Dtype = item.Info.Dtype
		knob.Name = item.Name
		knob.Type = item.Info.Type
		knob.Ref = item.Info.Ref
		knob.Range = item.Info.Scope
		knob.Items = item.Info.Items
		knob.Step = item.Info.Step
		knob.Options = item.Info.Options
		optimizerBody.Knobs = append(optimizerBody.Knobs, *knob)

		out, err := project.ExecCommand(item.Info.GetScript)
		if err != nil {
			return fmt.Errorf("faild to exec %s, err: %v", item.Info.GetScript, err)
		}
		initConfigure = append(initConfigure, strings.TrimSpace(knob.Name+"="+string(out)))
	}

	err = utils.WriteFile(path.Join(config.DefaultTempPath,
		o.Prj.Project+config.TuningRestoreConfig), strings.Join(initConfigure, ","),
		config.FilePerm, os.O_WRONLY|os.O_CREATE|os.O_TRUNC)
	if err != nil {
		log.Error(err)
		return err
	}

	respPostIns, err := optimizerBody.Post()
	if err != nil {
		return err
	}
	if respPostIns.Status != "OK" {
		err := fmt.Errorf("create task failed: %s", respPostIns.Status)
		log.Errorf(err.Error())
		return err
	}

	url := config.GetURL(config.OptimizerURI)
	o.OptimizerPutURL = fmt.Sprintf("%s/%s", url, respPostIns.TaskID)
	log.Infof("optimizer put url is: %s", o.OptimizerPutURL)

	o.Content = nil
	if err := o.DynamicTuned(ch); err != nil {
		return err
	}

	return nil
}

/*
DynamicTuned method using bayes algorithm to search the best performance parameters
*/
func (o *Optimizer) DynamicTuned(ch chan *PB.AckCheck) error {
	var evalValue string
	var err error
	if o.Content != nil {
		evalValue, err = o.evalParsing(ch)
		if err != nil {
			return err
		}
	}

	os.Setenv("ITERATION", strconv.Itoa(o.Iter))

	optPutBody := new(models.OptimizerPutBody)
	optPutBody.Iterations = o.Iter
	optPutBody.Value = evalValue
	o.RespPutIns, err = optPutBody.Put(o.OptimizerPutURL)
	if err != nil {
		log.Errorf("get setting parameter error: %v", err)
		return err
	}

	log.Infof("setting params is: %s", o.RespPutIns.Param)
	err, scripts := o.Prj.RunSet(o.RespPutIns.Param)
	if err != nil {
		log.Error(err)
		return err
	}
	log.Info("set the parameter success")

	err = syncConfigToOthers(scripts)
	if err != nil {
		return err
	}

	err, scripts = o.Prj.RestartProject()
	if err != nil {
		log.Error(err)
		return err
	}
	log.Info("restart project success")

	err = syncConfigToOthers(scripts)
	if err != nil {
		return err
	}

	o.StartIterTime = time.Now().Format(config.DefaultTimeFormat)

	if o.Iter == o.MaxIter {
		finalEval := strings.Replace(o.FinalEval, "=-", "=", -1)
		optimizationTerm := fmt.Sprintf("\n The final optimization result is: %s\n"+
			" The final evaluation value is: %s", o.RespPutIns.Param, finalEval)
		log.Info(optimizationTerm)
		ch <- &PB.AckCheck{Name: optimizationTerm}

		if err = deleteTask(o.OptimizerPutURL); err != nil {
			log.Error(err)
		}
	}

	o.Iter++
	ch <- &PB.AckCheck{Status: utils.SUCCESS}

	return nil
}

//restore tuning config
func (o *Optimizer) RestoreConfigTuned(ch chan *PB.AckCheck) error {
	tuningRestoreConf := path.Join(config.DefaultTempPath, o.Prj.Project+config.TuningRestoreConfig)
	exist, err := utils.PathExist(tuningRestoreConf)
	if err != nil {
		return err
	}
	if !exist {
		err := fmt.Errorf("%s project has not been executed "+
			"the dynamic optimizer search", o.Prj.Project)
		log.Errorf(err.Error())
		return err
	}

	content, err := ioutil.ReadFile(tuningRestoreConf)
	if err != nil {
		log.Error(err)
		return err
	}

	log.Infof("restoring params is: %s", string(content))
	err, scripts := o.Prj.RunSet(string(content))
	if err != nil {
		log.Error(err)
		return err
	}

	if err := syncConfigToOthers(scripts); err != nil {
		return err
	}

	result := fmt.Sprintf("restore %s project params success", o.Prj.Project)
	ch <- &PB.AckCheck{Name: result, Status: utils.SUCCESS}
	log.Infof(result)
	return nil
}

func (o *Optimizer) evalParsing(ch chan *PB.AckCheck) (string, error) {
	eval := string(o.Content)
	positiveEval := strings.Replace(eval, "=-", "=", -1)
	optimizationTerm := fmt.Sprintf("The %dth optimization result is: %s\n"+
		" The %dth evaluation value is: %s", o.Iter, o.RespPutIns.Param, o.Iter, positiveEval)
	ch <- &PB.AckCheck{Name: optimizationTerm}
	log.Info(optimizationTerm)

	endIterTime := time.Now().Format(config.DefaultTimeFormat)
	iterInfo := make([]string, 0)
	iterInfo = append(iterInfo, strconv.Itoa(o.Iter), o.StartIterTime, endIterTime,
		positiveEval, o.RespPutIns.Param)
	output := strings.Join(iterInfo, "|")
	err := utils.WriteFile(config.TuningFile, output+"\n", config.FilePerm,
		os.O_APPEND|os.O_WRONLY)
	if err != nil {
		log.Error(err)
		return "", err
	}

	evalValue := make([]string, 0)
	evalSum := 0.0
	for _, benchStr := range strings.Split(eval, ",") {
		kvs := strings.Split(benchStr, "=")
		if len(kvs) < 2 {
			continue
		}

		floatEval, err := strconv.ParseFloat(kvs[1], 64)
		if err != nil {
			log.Error(err)
			return "", err
		}

		evalSum += floatEval
		evalValue = append(evalValue, kvs[1])
	}

	if o.Iter == 1 || evalSum < o.MinEvalSum {
		o.MinEvalSum = evalSum
		o.FinalEval = eval
	}
	return strings.Join(evalValue, ","), nil
}

func deleteTask(url string) error {
	resp, err := http.Delete(url)
	if err != nil {
		log.Error("delete task faild:", err)
		return err
	}
	defer resp.Body.Close()
	return nil
}

//check server prj
func CheckServerPrj(data string, optimizer *Optimizer) error {
	var prjs []*project.YamlPrjSvr
	err := filepath.Walk(config.DefaultTuningPath, func(path string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			prj := new(project.YamlPrjSvr)
			if err := utils.ParseFile(path, "yaml", &prj); err != nil {
				return fmt.Errorf("load %s faild, err: %v", path, err)
			}
			log.Infof("project:%s load %s success", prj.Project, path)
			prjs = append(prjs, prj)
		}
		return nil
	})

	if err != nil {
		return err
	}

	for _, prj := range prjs {
		if data == prj.Project {
			log.Infof("find Project:%s", prj.Project)
			optimizer.Prj = prj
			return nil
		}
	}

	return fmt.Errorf("project:%s not found", data)
}

//sync tuned node
func (o *Optimizer) SyncTunedNode(ch chan *PB.AckCheck) error {
	log.Infof("setting params is: %s", string(o.Content))
	commands := strings.Split(string(o.Content), ",")
	for _, command := range commands {
		_, err := project.ExecCommand(command)
		if err != nil {
			return fmt.Errorf("failed to exec %s, err: %v", command, err)
		}
	}

	log.Info("set the parameter success")
	ch <- &PB.AckCheck{Status: utils.SUCCESS}

	return nil
}

//sync config to other nodes in cluster mode
func syncConfigToOthers(scripts string) error {
	if config.TransProtocol != "tcp" || scripts == "" {
		return nil
	}

	otherServers := strings.Split(strings.TrimSpace(config.Connect), ",")
	log.Infof("sync other nodes: %s", otherServers)

	for _, server := range otherServers {
		if server == config.Address || server == "" {
			continue
		}
		if err := syncConfigToNode(server, scripts); err != nil {
			log.Errorf("server %s failed to sync config, err: %v", server, err)
			return err
		}
	}
	return nil
}

//sync config to server node
func syncConfigToNode(server string, scripts string) error {
	c, err := client.NewClient(server, config.Port)
	if err != nil {
		return err
	}

	defer c.Close()
	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Tuning(context.Background())
	if err != nil {
		return err
	}

	defer stream.CloseSend()
	content := &PB.ProfileInfo{Name: "sync-config", Content: []byte(scripts)}
	if err := stream.Send(content); err != nil {
		return fmt.Errorf("sends failure, error: %v", err)
	}

	for {
		reply, err := stream.Recv()
		if err == io.EOF {
			break
		}

		if err != nil {
			return err
		}

		if reply.Status == utils.SUCCESS {
			log.Infof("server %s reply status success", server)
			break
		}
	}

	return nil
}

