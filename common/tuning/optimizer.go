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

package tuning

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"math"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/http"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/models"
	"gitee.com/openeuler/A-Tune/common/project"
	"gitee.com/openeuler/A-Tune/common/utils"
)

// Optimizer : the type implement the bayes serch service
type Optimizer struct {
	Prj                 *project.YamlPrjSvr
	Content             []byte
	Iter                int
	MaxIter             int32
	FeatureFilterIters  int32
	FeatureFilterCount  int32
	SplitCount          int32
	EvalFluctuation     float64
	RandomStarts        int32
	OptimizerPutURL     string
	FinalEval           string
	Engine              string
	FeatureFilterEngine string
	TuningFile          string
	Evaluations         string
	MinEvalSum          float64
	EvalMinArray        string
	EvalBase            string
	RespPutIns          *models.RespPutBody
	StartIterTime       string
	InitConfig          string
	TotalTime           float64
	Percentage          float64
	BackupFlag          bool
	FeatureFilter       bool
	Restart             bool
	TuningParams        utils.SortedPair
	EvalStatistics      []float64
	FeatureSelector     string
	PrjId               string
}

// object set type
type ObjectSet struct {
	Objects []*project.YamlPrjObj
}

// InitTuned method for iniit tuning
func (o *Optimizer) InitTuned(ch chan *PB.TuningMessage, stopCh chan int) error {
	o.FeatureFilter = false
	clientIter, err := strconv.Atoi(string(o.Content))
	if err != nil {
		return err
	}

	log.Infof("begin to dynamic optimizer search, client ask iterations:%d", clientIter)

	//dynamic profle setting
	o.MaxIter = int32(clientIter)
	if o.MaxIter > o.Prj.Maxiterations {
		o.MaxIter = o.Prj.Maxiterations
		log.Infof("project:%s max iterations:%d", o.Prj.Project, o.Prj.Maxiterations)
		ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(fmt.Sprintf("server project %s max iterations %d\n",
			o.Prj.Project, o.Prj.Maxiterations))}

	}

	if len(o.TuningParams) > 0 {
		for _, item := range o.Prj.Object {
			item.Info.Skip = true
			for _, para := range o.TuningParams {
				if para.Name == item.Name {
					item.Info.Skip = false
					break
				}
			}
		}
	}

	if !o.BackupFlag {
		err = o.Backup(ch)
		if err != nil {
			return err
		}
	}
	if err := o.createOptimizerTask(ch, o.MaxIter, o.Engine); err != nil {
		return err
	}

	o.Content = nil
	if err := o.DynamicTuned(ch, stopCh); err != nil {
		return err
	}
	return nil
}

func (o *Optimizer) createOptimizerTask(ch chan *PB.TuningMessage, iters int32, engine string) error {
	if err := utils.CreateDir(config.DefaultTuningLogPath, 0750); err != nil {
		return err
	}

	o.TuningFile = path.Join(config.DefaultTuningLogPath, fmt.Sprintf("%s_%s", o.Prj.Project, config.TuningFile))
	projectName := fmt.Sprintf("project %s %s %d\n", o.Prj.Project, o.Engine, o.MaxIter)
	if err := utils.WriteFile(o.TuningFile, projectName, utils.FilePerm,
		os.O_WRONLY|os.O_CREATE|os.O_APPEND); err != nil {
		log.Error(err)
		return err
	}

	optimizerBody := new(models.OptimizerPostBody)
	if o.Restart {
		if err := o.readTuningLog(optimizerBody); err != nil {
			return err
		}
	}
	if o.Restart && iters <= int32(len(optimizerBody.Xref)) && (engine != "gridsearch") && (engine != "abtest") {
		return fmt.Errorf("create task failed for client ask iters less than tuning history")
	}
	optimizerBody.MaxEval = iters
	optimizerBody.Engine = engine
	optimizerBody.RandomStarts = o.RandomStarts
	optimizerBody.FeatureFilter = o.FeatureFilter
	optimizerBody.FeatureSelector = o.FeatureSelector
	optimizerBody.SelFeature = config.SelFeature
	optimizerBody.SplitCount = o.SplitCount
	optimizerBody.Noise = config.Noise
	optimizerBody.Knobs = make([]models.Knob, 0)
	optimizerBody.PrjName = o.Prj.Project
	defaultValues := strings.Split(o.InitConfig, ",")
	for i, item := range o.Prj.Object {
		if item.Info.Skip {
			continue
		}
		knob := new(models.Knob)
		knob.Dtype = item.Info.Dtype
		knob.Name = item.Name
		knob.Type = item.Info.Type
		if len(item.Info.Ref) == 0 {
			knob.Ref = strings.Split(defaultValues[i], "=")[1]
		} else {
			knob.Ref = item.Info.Ref
		}
		knob.Range = item.Info.Scope
		knob.Items = item.Info.Items
		knob.Step = item.Info.Step
		knob.Options = item.Info.Options
		optimizerBody.Knobs = append(optimizerBody.Knobs, *knob)
	}

	log.Infof("optimizer post body is: %+v", optimizerBody)
	respPostIns, err := optimizerBody.Post()
	if err != nil {
		return err
	}
	log.Infof("create optimizer task response body is: %+v", respPostIns)
	if respPostIns.Status != "OK" {
		err := fmt.Errorf("create task failed: %s", respPostIns.Status)
		log.Errorf(err.Error())
		return err
	}

	ch <- &PB.TuningMessage{
		State:         PB.TuningMessage_JobInit,
		FeatureFilter: o.FeatureFilter,
		Content:       []byte(strconv.Itoa(respPostIns.Iters)),
		TuningLog: &PB.TuningHistory{
			BaseEval:  o.EvalBase,
			MinEval:   o.EvalMinArray,
			SumEval:   fmt.Sprintf("%.2f", o.MinEvalSum),
			TotalTime: int64(o.TotalTime),
			Starts:    int32(o.Iter) + 1,
		},
	}
	url := config.GetURL(config.OptimizerURI)
	o.OptimizerPutURL = fmt.Sprintf("%s/%s", url, respPostIns.TaskID)
	log.Infof("optimizer put url is: %s", o.OptimizerPutURL)

	optPutBody := new(models.OptimizerPutBody)
	optPutBody.Iterations = -1
	optPutBody.Value = ""
	optPutBody.Line = projectName
	optPutBody.PrjName = o.Prj.Project + "-" + o.PrjId
	optPutBody.MaxIter = respPostIns.Iters
	log.Infof("optimizer put body is: %+v", optPutBody)
	_, err = optPutBody.Put(o.OptimizerPutURL)
	if err != nil {
		log.Errorf("get setting parameter error: %v", err)
		return err
	}

	return nil
}

func (o *Optimizer) readTuningLog(body *models.OptimizerPostBody) error {
	file, err := os.Open(o.TuningFile)
	if err != nil {
		return err
	}
	defer file.Close()

	var startTime time.Time
	var endTime time.Time
	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	xrefMap := make(map[int][]string)
	yrefMap := make(map[int]float64)
	evalArray := make(map[int]string)
	for scanner.Scan() {
		line := scanner.Text()
		items := strings.Split(line, "|")
		if len(items) != 6 {
			continue
		}
		if o.Iter, err = strconv.Atoi(items[0]); err != nil {
			return err
		}

		yFloat, err := utils.CalculateBenchMark(items[3])
		if err != nil {
			return err
		}

		if o.Iter == 0 {
			o.EvalBase = items[4]
			o.MinEvalSum = yFloat
			o.EvalMinArray = items[4]
			continue
		}

		if startTime, err = time.Parse(config.DefaultTimeFormat, items[1]); err != nil {
			return err
		}

		if endTime, err = time.Parse(config.DefaultTimeFormat, items[2]); err != nil {
			return err
		}
		o.TotalTime = o.TotalTime + endTime.Sub(startTime).Seconds()

		evalArray[o.Iter] = items[4]
		xPara := strings.Split(items[5], ",")
		xValue := make([]string, 0)
		for _, para := range xPara {
			if !o.active(strings.Split(para, "=")[0]) {
				continue
			}
			xValue = append(xValue, para)
		}

		xrefMap[o.Iter] = xValue
		yrefMap[o.Iter] = yFloat
	}

	for i := 1; i <= o.Iter; i++ {
		if yrefMap[i] < o.MinEvalSum {
			o.MinEvalSum = yrefMap[i]
			o.EvalMinArray = evalArray[i]
		}
		body.Xref = append(body.Xref, xrefMap[i])
		body.Yref = append(body.Yref, strconv.FormatFloat(yrefMap[i], 'f', -1, 64))
	}

	o.FinalEval = o.EvalMinArray

	return nil
}

func (o *Optimizer) active(paraName string) bool {
	active := false
	for _, item := range o.Prj.Object {
		if strings.TrimSpace(paraName) != item.Name {
			continue
		}
		if item.Info.Skip {
			break
		}
		active = true
		break
	}
	return active
}

/*
DynamicTuned method using bayes algorithm to search the best performance parameters
*/
func (o *Optimizer) DynamicTuned(ch chan *PB.TuningMessage, stopCh chan int) error {
	var evalValue string
	var err error
	var message string
	lines, evalValue, err := o.evalParsing(ch)
	if err != nil {
		return err
	}

	err = os.Setenv("ITERATION", strconv.Itoa(o.Iter))
	if err != nil {
		return err
	}

	optPutStartTime := time.Now()

	optPutBody := new(models.OptimizerPutBody)
	optPutBody.Iterations = o.Iter
	optPutBody.Value = evalValue
	optPutBody.Line = lines
	optPutBody.PrjName = o.Prj.Project + "-" + o.PrjId
	optPutBody.MaxIter = int(o.MaxIter)
	log.Infof("optimizer put body is: %+v", optPutBody)
	o.RespPutIns, err = optPutBody.Put(o.OptimizerPutURL)
	if err != nil {
		log.Errorf("get setting parameter error: %v", err)
		return err
	}

	log.Infof("optimizer put response body: %+v", o.RespPutIns)

	if !o.matchRelations(o.RespPutIns.Param) && !o.RespPutIns.Finished {
		ch <- &PB.TuningMessage{State: PB.TuningMessage_Threshold}
		return nil
	}

	err, scripts := o.Prj.RunSet(o.RespPutIns.Param)
	if err != nil {
		log.Error(err)
		return err
	}
	log.Info("set the parameter success")

	err = o.syncConfigToOthers(scripts)
	if err != nil {
		return err
	}

	err, scripts = o.Prj.RestartProject()
	if err != nil {
		log.Error(err)
		return err
	}
	log.Info("restart project success")
	err = o.syncConfigToOthers(scripts)
	if err != nil {
		return err
	}

	o.StartIterTime = time.Now().Format(config.DefaultTimeFormat)
	log.Infof("optimizer put time is: %v", time.Since(optPutStartTime).Milliseconds())

	if o.RespPutIns.Finished {
		remainParams, err := o.filterParams()
		if err != nil {
			return err
		}

		if !o.FeatureFilter {
			finalEval := strings.Replace(o.FinalEval, "=-", "=", -1)
			message = fmt.Sprintf("\n The final optimization result is: %s\n"+
				" The final evaluation value is: %s\n", o.RespPutIns.Param, finalEval)
			if o.RespPutIns.Rank != "" {
				ranks := strings.Split(o.RespPutIns.Rank, ",")
				paraSort := make([]string, 0)
				for _, rank := range ranks {
					if !strings.Contains(rank, ":") {
						continue
					}
					paraSort = append(paraSort, strings.TrimSpace(strings.Split(rank, ":")[0]))
				}
				message = message + fmt.Sprintf(" The feature importances of current evaluation are: %s\n",
					strings.Join(paraSort, ","))
			}
			log.Info(message)
			ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}
		} else {
			message = fmt.Sprintf("\n Parameters reduced from %d to %d.",
				len(strings.Split(o.RespPutIns.Param, ",")), len(strings.Split(remainParams, ",")))
			ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}
			tuningParams := make([]string, 0)
			for _, para := range o.TuningParams {
				tuningParams = append(tuningParams, para.Name)
			}
			message = fmt.Sprintf("The selected most important parameters is:\n %s\n"+
				" Next optional parameters is:\n %s\n", tuningParams, remainParams)
			ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}
		}

		if len(o.Prj.Object)-len(o.TuningParams) < int(o.FeatureFilterCount) ||
			len(strings.Split(o.RespPutIns.Param, ",")) == len(strings.Split(remainParams, ",")) {
			stopCh <- 2
		} else {
			stopCh <- 1
		}
		o.Iter = 0
		if err = deleteTask(o.OptimizerPutURL); err != nil {
			return err
		}
		return nil
	}

	o.Iter++
	log.Infof("send back to client to start benchmark")
	ch <- &PB.TuningMessage{State: PB.TuningMessage_BenchMark,
		Content:       []byte(o.RespPutIns.Param),
		FeatureFilter: o.FeatureFilter,
	}
	return nil
}

func (o *Optimizer) matchRelations(optStr string) bool {
	return o.Prj.MatchRelations(optStr)
}

func (o *Optimizer) filterParams() (string, error) {
	log.Infof("params importance weight is: %s", o.RespPutIns.Rank)
	if strings.TrimSpace(o.RespPutIns.Rank) == "" {
		return "", nil
	}
	sortedParams := make(utils.SortedPair, 0)
	paramList := strings.Split(o.RespPutIns.Rank, ",")

	if len(paramList) == 0 {
		return "", nil
	}

	for _, param := range paramList {
		paramPair := strings.Split(param, ":")
		if len(paramPair) != 2 {
			continue
		}
		name := strings.TrimSpace(paramPair[0])
		score, err := strconv.ParseFloat(strings.TrimSpace(paramPair[1]), 64)
		if err != nil {
			return "", err
		}
		sortedParams = append(sortedParams, utils.Pair{Name: name, Score: score})
	}
	sort.Sort(sortedParams)
	log.Infof("sorted params: %+v", sortedParams)

	skipIndex := o.FeatureFilterCount
	mean := utils.Mean(o.EvalStatistics)
	sd := utils.StandardDeviation(o.EvalStatistics)
	log.Infof("Eval statistics: %v, mean: %v, sd: %v", o.EvalStatistics, mean, sd)
	if sd/math.Abs(mean) < o.EvalFluctuation {
		skipIndex = 0
	}

	skipParams := sortedParams[:skipIndex]
	remaindParams := sortedParams[skipIndex:]

	skipMap := make(map[string]struct{})
	for _, param := range skipParams {
		skipMap[param.Name] = struct{}{}
		o.TuningParams = append(o.TuningParams, utils.Pair{Name: param.Name, Score: param.Score})
	}
	for _, item := range o.Prj.Object {
		if _, ok := skipMap[item.Name]; ok {
			item.Info.Skip = true
		}
	}
	tuningParams := make([]string, 0)
	for _, param := range remaindParams {
		tuningParams = append(tuningParams, fmt.Sprintf("%s:%.2f", param.Name, param.Score))
	}
	return strings.Join(tuningParams, ","), nil
}

//restore tuning config
func (o *Optimizer) RestoreConfigTuned(ch chan *PB.TuningMessage) error {
	tuningRestoreConf := path.Join(config.DefaultTuningLogPath, o.Prj.Project+config.TuningRestoreConfig)
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

	if err := o.syncConfigToOthers(scripts); err != nil {
		return err
	}

	result := fmt.Sprintf("restore %s project params success", o.Prj.Project)
	ch <- &PB.TuningMessage{State: PB.TuningMessage_Ending, Content: []byte(result)}
	log.Infof(result)
	return nil
}

func (o *Optimizer) evalParsing(ch chan *PB.TuningMessage) (string, string, error) {
	if o.Restart && o.Content == nil {
		return "", "", nil
	}

	eval := o.EvalBase
	if o.Content != nil {
		eval = string(o.Content)
	}
	configs := o.InitConfig
	if o.RespPutIns != nil {
		configs = o.RespPutIns.Param
	}

	endIterTime := time.Now().Format(config.DefaultTimeFormat)
	iterInfo := make([]string, 0)
	iterInfo = append(iterInfo, strconv.Itoa(o.Iter), o.StartIterTime, endIterTime,
		o.Evaluations, eval, configs)
	output := strings.Join(iterInfo, "|")
	err := utils.WriteFile(o.TuningFile, output+"\n", utils.FilePerm,
		os.O_APPEND|os.O_WRONLY)
	if err != nil {
		log.Error(err)
		return "", "", err
	}

	kvs := strings.Split(o.Evaluations, "=")
	if len(kvs) != 2 {
		return "", "", fmt.Errorf("get evaluation error")
	}
	evalSum, err := strconv.ParseFloat(kvs[1], 64)
	if err != nil {
		log.Error(err)
		return "", "", err
	}

	if o.Iter == 1 || evalSum < o.MinEvalSum {
		o.MinEvalSum = evalSum
		o.FinalEval = eval
	}

	if o.FeatureFilter && o.Iter != 0 {
		o.EvalStatistics = append(o.EvalStatistics, evalSum)
	}

	return output, kvs[1], nil
}

func deleteTask(url string) error {
	resp, err := http.Delete(url)
	if err != nil {
		log.Error("delete task failed:", err)
		return err
	}
	resp.Body.Close()
	return nil
}

// CheckServerPrj: check server prj
func CheckServerPrj(data string, optimizer *Optimizer) error {
	projects := strings.Split(data, ",")

	log.Infof("client ask project: %s", data)
	exceptProject := make(map[string]struct{})
	for _, projectStr := range projects {
		exceptProject[strings.TrimSpace(projectStr)] = struct{}{}
	}

	var prjs []*project.YamlPrjSvr
	var yamlPaths []string
	err := filepath.Walk(config.DefaultTuningPath, func(path string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			prj := new(project.YamlPrjSvr)
			if err := utils.ParseFile(path, "yaml", &prj); err != nil {
				return fmt.Errorf("load %s failed, err: %v", path, err)
			}
			log.Infof("project:%s load %s success", prj.Project, path)
			prjs = append(prjs, prj)
			yamlPaths = append(yamlPaths, path)
		}
		return nil
	})

	if err != nil {
		return err
	}

	for idx, prj := range prjs {
		if _, ok := exceptProject[prj.Project]; !ok {
			continue
		}

		log.Infof("find Project:%s from %s", prj.Project, yamlPaths[idx])

		objectSet := new(ObjectSet)
		objectSet.Objects = append(objectSet.Objects, prj.Object...)
		prj.Object = CheckObjectReplace(prj.Object)
		objectSet.CheckObjectDuplicate()
		prj.Object = objectSet.Objects

		if optimizer.Prj == nil {
			optimizer.Prj = prj
			continue
		}
		optimizer.Prj.MergeProject(prj)
	}

	if optimizer.Prj == nil {
		return fmt.Errorf("project:%s not found", data)
	}

	log.Debugf("optimizer objects: %+v", optimizer.Prj)
	optimizer.Percentage = config.Percent
	return nil
}

// Check if object contains {disk} or {network}
func CheckObjectReplace(objects []*project.YamlPrjObj) []*project.YamlPrjObj {
	for ind := 0; ind < len(objects); ind++ {
		if strings.Contains(objects[ind].Info.GetScript, "{disk}") {
			param := config.Disk
			objects = ReplaceObject("{disk}", param, objects, ind)
		}
		if strings.Contains(objects[ind].Info.GetScript, "{network}") {
			param := config.Network
			objects = ReplaceObject("{network}", param, objects, ind)
		}
	}
	return objects
}

// replace {disk} {network} string in object
func ReplaceObject(replace string, param string, objects []*project.YamlPrjObj, ind int) []*project.YamlPrjObj {
	params := strings.Split(param, ",")
	if len(params) > 1 {
		for i := 1; i < len(params); i++ {
			newObj := &project.YamlPrjObj{
				Name:      objects[ind].Name,
				Info:      objects[ind].Info,
				Relations: objects[ind].Relations,
			}
			newObj.Name = newObj.Name + "-" + params[i]
			newObj.Info.GetScript = strings.Replace(newObj.Info.GetScript, replace, params[i], -1)
			newObj.Info.SetScript = strings.Replace(newObj.Info.SetScript, replace, params[i], -1)
			objects = append(objects, newObj)
		}
		objects[ind].Name = objects[ind].Name + "-" + params[0]
	}
	objects[ind].Info.GetScript = strings.Replace(objects[ind].Info.GetScript, replace, params[0], -1)
	objects[ind].Info.SetScript = strings.Replace(objects[ind].Info.SetScript, replace, params[0], -1)
	return objects
}

// Check the address value in atuned.cnf
func (obj *ObjectSet) CheckObjectDuplicate() {
	if strings.TrimSpace(config.Connect) == "" {
		return
	}
	var ips []string
	var ipGroups [][]string
	ips = strings.Split(strings.TrimSpace(config.Connect), "-")
	for i := 0; i < len(ips); i++ {
		ipSameGroup := strings.Split(strings.TrimSpace(ips[i]), ",")
		ipGroups = append(ipGroups, ipSameGroup)
	}
	objLen := len(obj.Objects)
	for ind := 0; ind < objLen; ind++ {
		if obj.Objects[ind].Clusters != nil {
			continue
		}
		obj.WriteObject(ind, ipGroups)
	}
}

func (obj *ObjectSet) WriteObject(ind int, groups [][]string) {
	var exceptsIps []interface{}
	exceptsIp := strings.Split(strings.TrimSpace(obj.Objects[ind].Info.Except), ",")
	for _, exceptIp := range exceptsIp {
		exceptsIps = append(exceptsIps, exceptIp)
	}
	if len(groups) == 1 {
		obj.Objects[ind].Name = obj.Objects[ind].Name + "-0"
		for i := 0; i < len(groups[0]); i++ {
			if !utils.InArray(exceptsIps, groups[0][i]) {
				obj.Objects[ind].Clusters = append(obj.Objects[ind].Clusters, groups[0][i])
			}
		}
		return
	}
	obj.AppendObject(ind, groups)
	obj.Objects[ind].Name = obj.Objects[ind].Name + "-0"
	for i := 0; i < len(groups[0]); i++ {
		if !utils.InArray(exceptsIps, groups[0][i]) {
			obj.Objects[ind].Clusters = append(obj.Objects[ind].Clusters, groups[0][i])
		}
	}
}

// append new params in object
func (obj *ObjectSet) AppendObject(ind int, ipGroups [][]string) {
	var exceptsIps []interface{}
	exceptsIp := strings.Split(strings.TrimSpace(obj.Objects[ind].Info.Except), ",")
	for _, exceptIp := range exceptsIp {
		exceptsIps = append(exceptsIps, exceptIp)
	}
	for i := 1; i < len(ipGroups); i++ {
		if len(ipGroups[i]) == 0 {
			continue
		}
		newObj := &project.YamlPrjObj{
			Name:      obj.Objects[ind].Name,
			Info:      obj.Objects[ind].Info,
			Relations: obj.Objects[ind].Relations,
		}
		for j := 0; j < len(ipGroups[i]); j++ {
			if !utils.InArray(exceptsIps, ipGroups[i][j]) {
				newObj.Clusters = append(newObj.Clusters, ipGroups[i][j])
			}
		}
		newObj.Name = newObj.Name + "-" + strconv.Itoa(i)
		obj.Objects = append(obj.Objects, newObj)
	}
}

// SyncTune: sync tuned node
func (o *Optimizer) SyncTunedNode(ch chan *PB.TuningMessage) error {
	log.Infof("setting params is: %s", string(o.Content))
	var commands []string
	err := json.Unmarshal([]byte(string(o.Content)), &commands)
	if err != nil {
		fmt.Errorf("invalid setting params! err: %v", err)
		return err
	}

	for _, command := range commands {
		log.Infof("execute setting command: %s", string(command))
		if command == "no operation" {
			continue
		}
		_, err := project.ExecCommand(command)
		if err != nil {
			return fmt.Errorf("failed to exec %s, err: %v", command, err)
		}
	}

	log.Info("set the parameter success")
	ch <- &PB.TuningMessage{State: PB.TuningMessage_Ending}

	return nil
}

func (o *Optimizer) GetNodeInitialConfig(ch chan *PB.TuningMessage) error {

	log.Infof("start to get the initial config: %s", string(o.Content))
	command := string(o.Content)

	log.Infof("execute getting command: %s", command)
	out, err := project.ExecGetOutput(command)
	if err != nil {
		return fmt.Errorf("failed to exec %s, err: %v", command, err)
	}
	output := string(out)

	log.Info("get the initial config success")
	ch <- &PB.TuningMessage{State: PB.TuningMessage_Ending, InitialConfig: output}

	return nil
}

//sync config to other nodes in cluster mode
func (o *Optimizer) syncConfigToOthers(scripts []string) error {
	if config.TransProtocol != "tcp" || scripts == nil {
		return nil
	}

	var ips []string
	var ipGroups [][]string
	ips = strings.Split(strings.TrimSpace(config.Connect), "-")
	for i := 0; i < len(ips); i++ {
		ipSameGroup := strings.Split(strings.TrimSpace(ips[i]), ",")
		ipGroups = append(ipGroups, ipSameGroup)
	}
	log.Infof("sync other nodes: %v", ipGroups)

	if len(scripts) == 0 {
		log.Infof("no scripts")
		return nil
	}

	objNum := len(scripts) / len(ipGroups)
	for i := 0; i < len(ipGroups); i++ {
		for j := 0; j < len(ipGroups[i]); j++ {
			if ipGroups[i][j] == config.Address || ipGroups[i][j] == "" {
				continue
			}
			var newScripts []string
			if i == 0 {
				for objIndex := 0; objIndex < objNum; objIndex++ {
					if utils.InArray(o.Prj.Object[objIndex].Clusters, ipGroups[i][j]) {
						newScripts = append(newScripts, scripts[objIndex])
					} else {
						newScripts = append(newScripts, "no operation")
					}
				}
			} else {
				for objIndex := 0; objIndex < objNum; objIndex++ {
					scriptIndex := objNum + objIndex*(len(ipGroups)-1) + i - 1
					if utils.InArray(o.Prj.Object[scriptIndex].Clusters, ipGroups[i][j]) {
						newScripts = append(newScripts, scripts[scriptIndex])
					} else {
						newScripts = append(newScripts, "no operation")
					}
				}
			}
			if err := o.syncConfigToNode(ipGroups[i][j], newScripts); err != nil {
				log.Errorf("server %s failed to sync config, err: %v", ipGroups[i][j], err)
				return err
			}
		}
	}
	return nil
}

//sync config to server node
func (o *Optimizer) syncConfigToNode(server string, scripts []string) error {
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

	defer func() {
		if err := stream.CloseSend(); err != nil {
			log.Errorf("close stream failed, error: %v", err)
		}
	}()

	scriptsJson, _ := json.Marshal(scripts)
	content := &PB.TuningMessage{State: PB.TuningMessage_SyncConfig, Content: []byte(scriptsJson)}
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

		state := reply.GetState()
		if state == PB.TuningMessage_Ending {
			log.Infof("server %s reply status success", server)
			break
		}
	}

	return nil
}

// InitFeatureSel method for init feature selection tuning
func (o *Optimizer) InitFeatureSel(ch chan *PB.TuningMessage, stopCh chan int) error {
	o.FeatureFilter = true

	if err := o.Backup(ch); err != nil {
		return err
	}
	if err := o.createOptimizerTask(ch, o.FeatureFilterIters, o.FeatureFilterEngine); err != nil {
		return err
	}

	o.Content = nil
	if err := o.DynamicTuned(ch, stopCh); err != nil {
		return err
	}
	return nil
}

// Backup method for backup the init config of tuning params
func (o *Optimizer) Backup(ch chan *PB.TuningMessage) error {
	o.BackupFlag = true
	initConfigure := make([]string, 0)
	var ips []string
	var ipGroups [][]string
	ips = strings.Split(strings.TrimSpace(config.Connect), "-")
	for i := 0; i < len(ips); i++ {
		ipSameGroup := strings.Split(strings.TrimSpace(ips[i]), ",")
		ipGroups = append(ipGroups, ipSameGroup)
	}
	var objGroupStr string
	for _, item := range o.Prj.Object {
		objGroupStr = ""
		reg := regexp.MustCompile(`-[0-9]+$`)
		res := reg.FindAllString(item.Name, -1)
		resLen := len(res)
		if resLen == 0 {
			out, err := project.ExecGetOutput(item.Info.GetScript)
			if err != nil {
				return fmt.Errorf("failed to exec %s, err: %v", item.Info.GetScript, err)
			}
			initConfigure = append(initConfigure, strings.TrimSpace(item.Name+"="+strings.TrimSpace(string(out))))
		} else {
			for wordPos := 1; wordPos < len(res[0]); wordPos++ {
				objGroupStr += string(res[0][wordPos])
			}
			objGroup, err := strconv.Atoi(string(objGroupStr))
			if err != nil {
				return err
			}
			if objGroup == 0 {
				out, err := project.ExecGetOutput(item.Info.GetScript)
				if err != nil {
					return fmt.Errorf("failed to exec %s, err: %v", item.Info.GetScript, err)
				}
				initConfigure = append(initConfigure, strings.TrimSpace(item.Name+"="+strings.TrimSpace(string(out))))
			} else {
				result, err := o.ExecGetCommand(ch, ipGroups[objGroup][0], config.Port, item.Info.GetScript)
				if err != nil {
					return err
				}
				initConfigure = append(initConfigure, strings.TrimSpace(item.Name+"="+strings.TrimSpace(string(result))))
			}
		}
	}

	err := utils.WriteFile(path.Join(config.DefaultTuningLogPath,
		o.Prj.Project+config.TuningRestoreConfig), strings.Join(initConfigure, ","),
		utils.FilePerm, os.O_WRONLY|os.O_CREATE|os.O_TRUNC)
	if err != nil {
		log.Error(err)
		return err
	}
	o.InitConfig = strings.Join(initConfigure, ",")
	return nil
}

func (o *Optimizer) ExecGetCommand(ch chan *PB.TuningMessage, ip string, port string, script string) (string, error) {
	c, err := client.NewClient(ip, port)
	if err != nil {
		return "", err
	}

	defer c.Close()
	svc := PB.NewProfileMgrClient(c.Connection())
	stream, err := svc.Tuning(context.Background())
	if err != nil {
		return "", err
	}

	defer func() {
		if err := stream.CloseSend(); err != nil {
			log.Errorf("close stream failed, error: %v", err)
		}
	}()

	content := &PB.TuningMessage{State: PB.TuningMessage_GetInitialConfig, Content: []byte(script)}
	if err := stream.Send(content); err != nil {
		return "", fmt.Errorf("sends failure, error: %v", err)
	}

	for {
		reply, err := stream.Recv()
		if err == io.EOF {
			break
		}

		if err != nil {
			return "", err
		}

		state := reply.GetState()
		result := reply.GetInitialConfig()
		if state == PB.TuningMessage_Ending {
			log.Infof("server %s get initial config success", ip)
			return string(result), nil
		}
	}
	return "", nil
}

// DeleteTask method delete the optimizer task in runing
func (o *Optimizer) DeleteTask() error {
	if o.OptimizerPutURL == "" {
		return nil
	}

	if err := deleteTask(o.OptimizerPutURL); err != nil {
		return err
	}
	log.Infof("delete task %s success!", o.OptimizerPutURL)
	o.OptimizerPutURL = ""
	return nil
}
