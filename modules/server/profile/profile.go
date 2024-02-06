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
	"bufio"
	"bytes"
	"context"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"mime/multipart"
	HTTP "net/http"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/go-ini/ini"
	"github.com/mitchellh/mapstructure"
	"github.com/urfave/cli"
	"google.golang.org/grpc"

	PB "gitee.com/openeuler/A-Tune/api/profile"
	_ "gitee.com/openeuler/A-Tune/common/checker"
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/http"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/models"
	"gitee.com/openeuler/A-Tune/common/profile"
	"gitee.com/openeuler/A-Tune/common/registry"
	"gitee.com/openeuler/A-Tune/common/schedule"
	SVC "gitee.com/openeuler/A-Tune/common/service"
	"gitee.com/openeuler/A-Tune/common/sqlstore"
	"gitee.com/openeuler/A-Tune/common/tuning"
	"gitee.com/openeuler/A-Tune/common/utils"
)

// Monitor : the body send to monitor service
type Monitor struct {
	Module  string `json:"module"`
	Purpose string `json:"purpose"`
	Field   string `json:"field"`
}

// CollectorPost : the body send to collection service
type CollectorPost struct {
	Monitors  []Monitor `json:"monitors"`
	SampleNum int       `json:"sample_num"`
	Pipe      string    `json:"pipe"`
	File      string    `json:"file"`
	DataType  string    `json:"data_type"`
}

// RespCollectorPost : the response of collection servie
type RespCollectorPost struct {
	Path string                 `json:"path"`
	Data map[string]interface{} `json:"data"`
}

// ClassifyPostBody : the body send to classify service
type ClassifyPostBody struct {
	Data      string `json:"data"`
	ModelPath string `json:"modelpath,omitempty"`
	Model     string `json:"model,omitempty"`
}

// RespClassify : the response of classify model
type RespClassify struct {
	Bottleneck int  `json:"bottleneck_binary"`
	ResourceLimit string  `json:"resource_limit"`
	WorkloadType  string  `json:"workload_type"`
	Percentage    float32 `json:"percentage"`
}

// ProfileServer : the type impletent the grpc server
type ProfileServer struct {
	utils.MutexLock
	ConfPath   string
	ScriptPath string
	Raw        *ini.File
}

func init() {
	svc := SVC.ProfileService{
		Name:    "opt.profile",
		Desc:    "opt profile module",
		NewInst: NewProfileServer,
	}
	if err := SVC.AddService(&svc); err != nil {
		fmt.Printf("Failed to load service project : %s\n", err)
		return
	}

	log.Info("load profile service successfully\n")
}

// NewProfileServer method new a instance of the grpc server
func NewProfileServer(ctx *cli.Context, opts ...interface{}) (interface{}, error) {
	defaultConfigFile := path.Join(config.DefaultConfPath, "atuned.cnf")

	exist, err := utils.PathExist(defaultConfigFile)
	if err != nil {
		return nil, err
	}
	if !exist {
		return nil, fmt.Errorf("could not find default config file")
	}

	cfg, err := ini.Load(defaultConfigFile)
	if err != nil {
		return nil, fmt.Errorf("failed to parse %s, %v", defaultConfigFile, err)
	}

	return &ProfileServer{
		Raw: cfg,
	}, nil
}

// RegisterServer method register the grpc service
func (s *ProfileServer) RegisterServer(server *grpc.Server) error {
	PB.RegisterProfileMgrServer(server, s)
	return nil
}

// Healthy method, implement SvrService interface
func (s *ProfileServer) Healthy(opts ...interface{}) error {
	return nil
}

// Post method send POST to start analysis the workload type
func (p *ClassifyPostBody) Post() (*RespClassify, error) {
	url := config.GetURL(config.ClassificationURI)
	response, err := http.Post(url, p)
	if err != nil {
		return nil, err
	}

	defer response.Body.Close()
	if response.StatusCode != 200 {
		return nil, fmt.Errorf("online learning failed")
	}
	resBody, err := ioutil.ReadAll(response.Body)
	if err != nil {
		return nil, err
	}

	resPostIns := new(RespClassify)
	err = json.Unmarshal(resBody, resPostIns)
	if err != nil {
		return nil, err
	}

	return resPostIns, nil
}

// Post method send POST to start collection data
func (c *CollectorPost) Post() (*RespCollectorPost, error) {
	url := config.GetURL(config.CollectorURI)
	response, err := http.Post(url, c)
	if err != nil {
		return nil, err
	}

	defer response.Body.Close()
	if response.StatusCode != 200 {
		return nil, fmt.Errorf("collect data failed")
	}
	resBody, err := ioutil.ReadAll(response.Body)
	if err != nil {
		return nil, err
	}

	resPostIns := new(RespCollectorPost)
	err = json.Unmarshal(resBody, resPostIns)
	if err != nil {
		return nil, err
	}
	return resPostIns, nil
}

// Post method send POST to start transfer file
func Post(serviceType, paramName, path string) (string, error) {
	url := config.GetURL(config.TransferURI)
	file, err := os.Open(path)
	if err != nil {
		return "", fmt.Errorf("Path Error")
	}
	defer file.Close()

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, err := writer.CreateFormFile(paramName, filepath.Base(path))
	if err != nil {
		return "", fmt.Errorf("writer error")
	}
	_, err = io.Copy(part, file)
	if err != nil {
		return "", fmt.Errorf("copy error")
	}

	extraParams := map[string]string{
		"service":  serviceType,
		"savepath": "/etc/atuned/" + serviceType + "/" + filepath.Base(path),
	}

	for key, val := range extraParams {
		_ = writer.WriteField(key, val)
	}
	err = writer.Close()
	if err != nil {
		return "", fmt.Errorf("writer close error")
	}

	request, err := HTTP.NewRequest("POST", url, body)
	if err != nil {
		return "", fmt.Errorf("newRequest failed")
	}
	request.Header.Set("Content-Type", writer.FormDataContentType())
	client, err := http.NewhttpClient(url)
	if err != nil {
		return "", err
	}
	resp, err := client.Do(request)
	if err != nil {
		return "", fmt.Errorf("do request error: %v", err)
	} else {
		defer resp.Body.Close()

		body := &bytes.Buffer{}
		_, err := body.ReadFrom(resp.Body)
		if err != nil {
			return "", fmt.Errorf("body read form error")
		}
		res := body.String()
		res = res[1 : len(res)-2]
		return res, nil
	}
}

// Profile method set the workload type to effective manual
func (s *ProfileServer) Profile(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_ProfileServer) error {
	profileNamesStr := profileInfo.GetName()
	profileNames := strings.Split(profileNamesStr, ",")
	profile, errMsg := profile.Load(profileNames)

	if errMsg != "" {
		fmt.Println("Failed to load profile:", profileInfo.GetName())
		return fmt.Errorf("load profile %s failed: %s", profileInfo.GetName(), errMsg)
	}
	ch := make(chan *PB.AckCheck)
	ctx, cancel := context.WithCancel(context.Background())
	defer close(ch)
	defer cancel()

	go func(ctx context.Context) {
		for {
			select {
			case value := <-ch:
				_ = stream.Send(value)
			case <-ctx.Done():
				return
			}
		}
	}(ctx)

	if err := profile.RollbackActive(ch); err != nil {
		return err
	}

	time.Sleep(1 * time.Second)
	return nil
}

// ListWorkload method list support workload
func (s *ProfileServer) ListWorkload(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_ListWorkloadServer) error {
	log.Debug("Begin to inquire all workloads\n")
	profileLogs, err := sqlstore.GetProfileLogs()
	if err != nil {
		return err
	}

	var activeName string
	if len(profileLogs) > 0 {
		activeName = profileLogs[0].ProfileID
	}

	if activeName != "" {
		classProfile := &sqlstore.GetClass{Class: activeName}
		err = sqlstore.GetClasses(classProfile)
		if err != nil {
			return fmt.Errorf("inquery workload type table failed %v", err)
		}
		if len(classProfile.Result) > 0 {
			activeName = classProfile.Result[0].ProfileType
		}
	}
	log.Debugf("active name is %s", activeName)

	err = filepath.Walk(config.DefaultProfilePath, func(absPath string, info os.FileInfo, err error) error {
		if info.Name() == "include" {
			return filepath.SkipDir
		}
		if !info.IsDir() {
			if !strings.HasSuffix(info.Name(), ".conf") {
				return nil
			}

			absFilename := absPath[len(config.DefaultProfilePath)+1:]
			filenameOnly := strings.TrimSuffix(strings.ReplaceAll(absFilename, "/", "-"),
				path.Ext(info.Name()))

			var active bool
			if filenameOnly == activeName {
				active = true
			}
			_ = stream.Send(&PB.ListMessage{
				ProfileNames: filenameOnly,
				Active:       strconv.FormatBool(active)})

		}
		return nil
	})

	if err != nil {
		return err
	}

	return nil
}

// CheckInitProfile method check the system init information
// like BIOS version, memory balanced...
func (s *ProfileServer) CheckInitProfile(profileInfo *PB.ProfileInfo,
	stream PB.ProfileMgr_CheckInitProfileServer) error {
	ch := make(chan *PB.AckCheck)
	defer close(ch)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	services := registry.GetCheckerServices()

	for _, service := range services {
		log.Infof("initializing checker service: %s", service.Name)
		if err := service.Instance.Init(); err != nil {
			return fmt.Errorf("service init failed: %v", err)
		}
	}

	// running checker service
	for _, srv := range services {
		service := srv
		checkerService, ok := service.Instance.(registry.CheckService)
		if !ok {
			continue
		}

		if registry.IsCheckDisabled(service.Instance) {
			continue
		}
		err := checkerService.Check(ch)
		if err != nil {
			log.Errorf("service %s running failed, reason: %v", service.Name, err)
			continue
		}
	}

	return nil
}

func handleCsv(curPath string, storePath string) error {
	if storePath == "" {
		return nil
	}
	fs, err := os.Open(curPath)
	if err != nil {
		return fmt.Errorf("can not get file, err is %+v", err)
	}
	defer fs.Close()
	r := csv.NewReader(fs)
	content, err := r.ReadAll()
	if err != nil {
		return fmt.Errorf("can not get file, err is %+v", err)
	}

	tempFile, err := os.OpenFile(storePath, os.O_RDWR|os.O_APPEND, 0640)
	if err != nil {
		return fmt.Errorf("can not get file, err is %+v", err)
	}
	defer tempFile.Close()

	w := csv.NewWriter(tempFile)
	if err := w.WriteAll(content[1:]); err != nil {
		return fmt.Errorf("can not write to file, err is %+v", err)
	}

	if err := os.Rename(storePath, curPath); err != nil {
		return fmt.Errorf("can not rename the path, err is %+v", err)
	}

	return nil
}

var collectStatus = make(map[string]string)

// Analysis method analysis the system traffic load
func (s *ProfileServer) Analysis(message *PB.AnalysisMessage, stream PB.ProfileMgr_AnalysisServer) error {
	id := message.GetId()
	if message.GetFlag() == "end" {
		collectStatus[id] = "end"
		return nil
	}
	if message.GetFlag() == "start" {
		collectStatus[id] = "run"
	}

	if !message.Characterization {
		if !s.TryLock() {
			return fmt.Errorf("dynamic optimizer search or analysis has been in running")
		}
		defer s.Unlock()
	}
	_ = stream.Send(&PB.AckCheck{Name: "1. Analysis system runtime information: CPU Memory IO and Network..."})

	npipe, err := utils.CreateNamedPipe()
	if err != nil {
		return fmt.Errorf("create named pipe failed")
	}

	defer os.Remove(npipe)

	subProcess := true
	collectionId := -1
	go func() {
		for {
			file, err := os.OpenFile(npipe, os.O_RDONLY, os.ModeNamedPipe)
			if err != nil {
				log.Errorf("failed to open pipe, err: %v", err)
				return
			}
			reader := bufio.NewReader(file)

			scanner := bufio.NewScanner(reader)

			for scanner.Scan() {
				line := strings.TrimRight(scanner.Text(), "\n")
				pairs := strings.Split(line, " ")
				screen := ""
				for _, ele := range pairs {
					if len(strings.Split(ele, ":")) == 2 {
						screen += strings.Split(ele, ":")[1] + " "
					}
				}
				_ = stream.Send(&PB.AckCheck{Name: screen, Status: utils.INFO})
				retId, err := models.InitTransfer("csv", "running", line, "", collectionId)
				if err != nil {
					_ = stream.Send(&PB.AckCheck{Name: err.Error()})
					log.Errorf("collect system data error: transfer data %v", err)
					return
				}
				collectionId = retId
			}

			if !subProcess {
				_, err := models.InitTransfer("csv", "finished", "", "", collectionId)
				if err != nil {
					_ = stream.Send(&PB.AckCheck{Name: err.Error()})
					log.Errorf("collect system data error: transfer data %v", err)
					return
				}
				break
			}
		}
	}()

	var respCollectPost *RespCollectorPost
	tempFile := ""
	for {
		respCollectPost, err = s.collection(npipe, message.GetTime())
		if err != nil {
			_ = stream.Send(&PB.AckCheck{Name: err.Error()})
			log.Errorf("collection system data error: %v", err)
			return err
		}

		err = handleCsv(respCollectPost.Path, tempFile)
		if err != nil {
			return err
		}

		if collectStatus[id] == "end" {
			delete(collectStatus, id)
			break
		}
		if message.GetFlag() == "" {
			break
		}
	}

	subProcess = false

	bottleneck, workloadType, resourceLimit, err := s.classify(respCollectPost.Path, message.GetModel())
	if err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}
	_, err = models.InitTransfer("csv", "finished", "", workloadType, collectionId)
	if err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}

	//3. judge the workload type is exist in the database
	classProfile := &sqlstore.GetClass{Class: workloadType}
	if err = sqlstore.GetClasses(classProfile); err != nil {
		log.Errorf("inquery workload type table failed %v", err)
		return fmt.Errorf("inquery workload type table failed %v", err)
	}
	if len(classProfile.Result) == 0 {
		log.Errorf("%s is not exist in the table", workloadType)
		return fmt.Errorf("%s is not exist in the table", workloadType)
	}

	// the workload type is already actived
	if classProfile.Result[0].Active {
		log.Infof("analysis result %s is the same with current active workload type", workloadType)
		return nil
	}

	//4. inquery the support app of the workload type
	classApps := &sqlstore.GetClassApp{Class: workloadType}
	err = sqlstore.GetClassApps(classApps)
	if err != nil {
		log.Errorf("inquery support app depend on class error: %v", err)
		return err
	}
	if len(classApps.Result) == 0 {
		return fmt.Errorf("class %s is not exist in the tables", workloadType)
	}
	apps := classApps.Result[0].Apps
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n 2. Current System Workload Characterization is %s", apps)})

	logFile, err := utils.GetLogFilePath(config.DefaultCollectionPath)
	if err != nil {
		return fmt.Errorf("get log file path failed: %v", err)
	}
	file, err := os.OpenFile(logFile, os.O_APPEND|os.O_WRONLY, 0640)
	if err != nil {
		return fmt.Errorf("open file failed: %v", err)
	}
	defer file.Close()
	_, err = io.WriteString(file, apps+"\n")
	if err != nil {
		log.Errorf("write workload type to log failed: %v", err)
	}

	log.Infof("workload %s support app: %s", workloadType, apps)
	log.Infof("workload %s resource limit: %s, cluster result resource limit: %s",
		workloadType, apps, resourceLimit)	

	var step int = 3
	cpuExist := bottleneck&16 > 0
	memExist := bottleneck&8 > 0
	netQualityExist := bottleneck&4 > 0
	netIOExist := bottleneck&2 > 0
	diskIOExist := bottleneck&1 > 0

	if message.Bottleneck {
		if bottleneck == 0 {
			 _ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n %d. Current System does not detected the five bottlenecks of Computing, Memory, Network, Network I/O and disk I/O", step)})
			log.Infof("Current System does not detected the five bottlenecks of Computing, Memory, Network, Network I/O and disk I/O")
		} else {
			bottleneckTypes := []string{"Computing", "Memory", "Network", "Network I/O", "disk I/O"}
			bottlenecks := []string{}
			boolValues := []bool{cpuExist, memExist, netQualityExist, netIOExist, diskIOExist}
			
			for i, exist := range boolValues {
				if exist {
					bottlenecks = append(bottlenecks, bottleneckTypes[i])
				}
			}
			bottlenecksStr := strings.Join(bottlenecks, ", ")
			_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n %d. Current System bottlenecks: %s", step, bottlenecksStr)})
			log.Infof("Current System bottlenecks: %s", bottlenecksStr)
		}
		step++
	}

	if message.Characterization {
		return nil
	}
	
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n %d. Build the best resource model...", step)})
	step++

	//5. get the profile type depend on the workload type
	profileType := classProfile.Result[0].ProfileType
	profileNames := strings.Split(profileType, ",")
	if len(profileNames) == 0 {
		log.Errorf("No profile or invalid profiles were specified.")
		return fmt.Errorf("no profile or invalid profiles were specified")
	}

	if message.Bottleneck {
		bottleneck_profiles := []struct {
			bottleneck bool
			profile    string
		}{
			{cpuExist, "include-compute-intensive"},
			{memExist, "include-memory-intensive"},
			{netQualityExist, "include-network-intensive"},
			{netIOExist, "include-network-intensive"},
			{diskIOExist, "include-io-intensive"},
		}
		for _, c := range bottleneck_profiles {
			if c.bottleneck {
				exists := false
				for _, existingProfile := range profileNames {
					if existingProfile == c.profile {
						exists = true
						break
					}
				}
				if !exists {
					profileNames = append(profileNames, c.profile)
				}
			}
		}
	}

	//6. get the profile info depend on the profile type
	log.Infof("the resource model of the profile type is %s", strings.Join(profileNames, ", "))
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n %d. Match profile: %s", step, strings.Join(profileNames, ", "))})
	step++
	pro, _ := profile.Load(profileNames)
	pro.SetWorkloadType(workloadType)
	pro.SetCollectionId(collectionId)
	
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n %d. begin to set static profile", step)})
	step++
	log.Infof("begin to set static profile")

	//static profile setting
	ch := make(chan *PB.AckCheck)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	_ = pro.RollbackActive(ch)

	logPath, err := utils.GetLogFilePath(config.DefaultCollectionPath)
	if err != nil {
		return fmt.Errorf("get log file path failed: %v", err)
	}
	defer os.Remove(logPath)
	_, err = Post("classification", "file", logPath)
	if err != nil {
		return fmt.Errorf("Failed transfer file log file to server: %v", err)
	}

	rules := &sqlstore.GetRuleTuned{Class: workloadType}
	if err := sqlstore.GetRuleTuneds(rules); err != nil {
		return err
	}

	if len(rules.Result) < 1 {
		_ = stream.Send(&PB.AckCheck{Name: "Completed optimization, please restart application!"})
		log.Info("no rules to tuned")
		return nil
	}

	log.Info("begin to dynamic tuning depending on rules")
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n %d. begin to set dynamic profile", step)})
	step++
	if err := tuning.RuleTuned(workloadType); err != nil {
		return err
	}

	_ = stream.Send(&PB.AckCheck{Name: "Completed optimization, please restart application!"})
	return nil
}

// Tuning method calling the bayes search method to tuned parameters
func (s *ProfileServer) Tuning(stream PB.ProfileMgr_TuningServer) error {
	if !s.TryLock() {
		return fmt.Errorf("dynamic optimizer search or analysis has been in running")
	}
	defer s.Unlock()

	ch := make(chan *PB.TuningMessage)
	defer close(ch)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	var optimizer = tuning.Optimizer{}
	defer func() {
		if err := optimizer.DeleteTask(); err != nil {
			log.Errorf("delete optimizer task failed, error: %v", err)
		}
	}()

	stopCh := make(chan int, 1)
	defer close(stopCh)
	var cycles int32 = 0
	var message string
	var step int32 = 1

	for {
		select {
		case stop := <-stopCh:
			if cycles > 0 {
				if stop == 2 {
					cycles = 1
				}
				_ = stream.Send(&PB.TuningMessage{State: PB.TuningMessage_JobRestart})
			} else {
				_ = stream.Send(&PB.TuningMessage{State: PB.TuningMessage_Ending})
			}
			cycles--
		default:
		}
		if cycles < 0 {
			break
		}
		reply, err := stream.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}

		state := reply.GetState()
		switch state {
		case PB.TuningMessage_SyncConfig:
			optimizer.Content = reply.GetContent()
			err = optimizer.SyncTunedNode(ch)
			if err != nil {
				return err
			}
		case PB.TuningMessage_GetInitialConfig:
			optimizer.Content = reply.GetContent()
			err = optimizer.GetNodeInitialConfig(ch)
			if err != nil {
				return err
			}
		case PB.TuningMessage_JobRestart:
			log.Infof("restart cycles is: %d", cycles)
			optimizer.Content = reply.GetContent()
			if cycles > 0 {
				optimizer.EvalStatistics = make([]float64, 0)
				message = fmt.Sprintf("%d、Starting the next cycle of parameter selection......", step)
				step += 1
				ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}
				if err = optimizer.InitFeatureSel(ch, stopCh); err != nil {
					return err
				}
			} else {
				message = fmt.Sprintf("%d、Start to tuning the system......", step)
				step += 1
				ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}
				if err = optimizer.InitTuned(ch, stopCh); err != nil {
					return err
				}
			}
		case PB.TuningMessage_JobInit:
			project := reply.GetName()
			if len(strings.TrimSpace(project)) == 0 {
				if err != nil {
					return err
				}
				message = fmt.Sprintf("%d.Begin to Analysis the system......", step)
				step += 1
				ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}
				project, err = s.Getworkload()
				if err != nil {
					return err
				}
				message = fmt.Sprintf("%d.Current running application is: %s", step, project)
				step += 1
				ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}
			}

			message = fmt.Sprintf("%d.Loading its corresponding tuning project: %s", step, project)
			step += 1
			ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}

			if err = tuning.CheckServerPrj(project, &optimizer); err != nil {
				return err
			}

			optimizer.Engine = reply.GetEngine()
			optimizer.Content = reply.GetContent()
			optimizer.Restart = reply.GetRestart()
			optimizer.RandomStarts = reply.GetRandomStarts()
			optimizer.HistoryPath=reply.GetHistoryPath()
			optimizer.FeatureFilterEngine = reply.GetFeatureFilterEngine()
			optimizer.FeatureFilterIters = reply.GetFeatureFilterIters()
			optimizer.SplitCount = reply.GetSplitCount()
			optimizer.PrjId = strconv.FormatInt(time.Now().UnixNano()/1e6, 10)
			cycles = reply.GetFeatureFilterCycle()
			optimizer.FeatureFilterCount = reply.GetFeatureFilterCount()
			optimizer.EvalFluctuation = reply.GetEvalFluctuation()
			optimizer.FeatureSelector = reply.GetFeatureSelector()
			ch <- &PB.TuningMessage{State: PB.TuningMessage_JobCreate}
		case PB.TuningMessage_JobCreate:
			optimizer.EvalBase = reply.GetTuningLog().GetBaseEval()
			optimizer.Evaluations = reply.GetTuningLog().GetSumEval()
			optimizer.TuningParams = make(utils.SortedPair, 0)
			if cycles == 0 {
				if optimizer.Restart {
					message = fmt.Sprintf("%d.Continue to tuning the system......", step)
				} else {
					message = fmt.Sprintf("%d.Start to tuning the system......", step)
				}
				ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}
				step += 1
				if err = optimizer.InitTuned(ch, stopCh); err != nil {
					return err
				}
			} else {
				optimizer.EvalStatistics = make([]float64, 0)
				message = fmt.Sprintf("%d.Starting to select the important parameters......", step)
				ch <- &PB.TuningMessage{State: PB.TuningMessage_Display, Content: []byte(message)}
				step += 1
				if err = optimizer.InitFeatureSel(ch, stopCh); err != nil {
					return err
				}
			}
		case PB.TuningMessage_Restore:
			project := reply.GetName()
			log.Infof("begin to restore project: %s", project)
			if err := tuning.CheckServerPrj(project, &optimizer); err != nil {
				return err
			}
			if err := optimizer.RestoreConfigTuned(ch); err != nil {
				return err
			}
			log.Infof("restore project %s success", project)
			return nil
		case PB.TuningMessage_BenchMark:
			optimizer.Content = reply.GetContent()
			optimizer.Evaluations = reply.GetTuningLog().GetSumEval()
			err := optimizer.DynamicTuned(ch, stopCh)
			if err != nil {
				return err
			}

		}
	}

	return nil
}

/*
UpgradeProfile method update the db file
*/
func (s *ProfileServer) UpgradeProfile(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_UpgradeProfileServer) error {
	if config.TransProtocol == "tcp" {
		return fmt.Errorf("the upgrade command cannot be executed through TCP connections.")
	}

	isLocalAddr, err := SVC.CheckRpcIsLocalAddr(stream.Context())
	if err != nil {
		return err
	}
	if !isLocalAddr {
		return fmt.Errorf("the upgrade command can not be remotely operated")
	}

	log.Debug("Begin to upgrade profiles\n")
	currenDbPath := path.Join(config.DatabasePath, config.DatabaseName)
	newDbPath := profileInfo.GetName()

	exist, err := utils.PathExist(config.DefaultTempPath)
	if err != nil {
		return err
	}
	if !exist {
		if err = os.MkdirAll(config.DefaultTempPath, 0750); err != nil {
			return err
		}
	}
	timeUnix := strconv.FormatInt(time.Now().Unix(), 10) + ".db"
	tempFile := path.Join(config.DefaultTempPath, timeUnix)

	if err := utils.CopyFile(tempFile, currenDbPath); err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error(), Status: utils.FAILD})
		return nil
	}

	if err := utils.CopyFile(currenDbPath, newDbPath); err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error(), Status: utils.FAILD})
		return nil
	}

	if err := sqlstore.Reload(currenDbPath); err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error(), Status: utils.FAILD})
		return nil
	}

	_ = stream.Send(&PB.AckCheck{Name: "upgrade success", Status: utils.SUCCESS})
	return nil
}

/*
InfoProfile method display the content of the specified workload type
*/
func (s *ProfileServer) InfoProfile(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_InfoProfileServer) error {
	var context string
	profileName := profileInfo.GetName()
	err := filepath.Walk(config.DefaultProfilePath, func(absPath string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			absFilename := absPath[len(config.DefaultProfilePath)+1:]
			filenameOnly := strings.TrimSuffix(strings.ReplaceAll(absFilename, "/", "-"),
				path.Ext(info.Name()))
			if filenameOnly == profileName {
				data, err := ioutil.ReadFile(absPath)
				if err != nil {
					return err
				}
				context = "\n*** " + profileName + ":\n" + string(data)
				_ = stream.Send(&PB.ProfileInfo{Name: context})
				return nil
			}
		}
		return nil
	})

	if err != nil {
		return err
	}

	if context == "" {
		log.Errorf("profile %s is not exist", profileName)
		return fmt.Errorf("profile %s is not exist", profileName)
	}

	return nil
}

/*
CheckActiveProfile method check current active profile is effective
*/
func (s *ProfileServer) CheckActiveProfile(profileInfo *PB.ProfileInfo,
	stream PB.ProfileMgr_CheckActiveProfileServer) error {
	log.Debug("Begin to check active profiles\n")

	profileLogs, err := sqlstore.GetProfileLogs()
	if err != nil {
		return err
	}

	var activeName string
	if len(profileLogs) > 0 {
		activeName = profileLogs[0].ProfileID
	}

	if activeName == "" {
		return fmt.Errorf("no active profile or more than 1 active profile")
	}
	classProfile := &sqlstore.GetClass{Class: activeName}
	err = sqlstore.GetClasses(classProfile)
	if err != nil {
		return fmt.Errorf("inquery workload type table failed %v", err)
	}
	if len(classProfile.Result) > 0 {
		activeName = classProfile.Result[0].ProfileType
	}
	log.Debugf("active name is %s", activeName)

	profile, ok := profile.LoadFromProfile(activeName)

	if !ok {
		log.WithField("profile", activeName).Errorf("Load profile %s failed", activeName)
		return fmt.Errorf("load profile %s Failed", activeName)
	}

	ch := make(chan *PB.AckCheck)
	defer close(ch)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	if err := profile.Check(ch); err != nil {
		return err
	}

	return nil
}

// ProfileRollback method rollback the profile to init state
func (s *ProfileServer) ProfileRollback(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_ProfileRollbackServer) error {
	profileLogs, err := sqlstore.GetProfileLogs()
	if err != nil {
		return err
	}

	if len(profileLogs) < 1 {
		_ = stream.Send(&PB.AckCheck{Name: "no profile need to rollback"})
		return nil
	}

	sort.Slice(profileLogs, func(i, j int) bool {
		return profileLogs[i].ID > profileLogs[j].ID
	})

	//static profile setting
	ch := make(chan *PB.AckCheck)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	for _, pro := range profileLogs {
		log.Infof("begin to restore profile id: %d", pro.ID)
		profileInfo := profile.HistoryProfile{}
		_ = profileInfo.Load(pro.Context)
		_ = profileInfo.Resume(ch)

		// delete profile log after restored
		if err := sqlstore.DelProfileLogByID(pro.ID); err != nil {
			return err
		}
		//delete backup dir
		if err := os.RemoveAll(pro.BackupPath); err != nil {
			return err
		}

		// update active profile after restored
		if err := sqlstore.ActiveProfile(pro.ProfileID); err != nil {
			return nil
		}
	}

	if err := sqlstore.InActiveProfile(); err != nil {
		return nil
	}

	return nil
}

/*
Collection method call collection script to collect system data.
*/
func (s *ProfileServer) Collection(message *PB.CollectFlag, stream PB.ProfileMgr_CollectionServer) error {
	isLocalAddr, err := SVC.CheckRpcIsLocalAddr(stream.Context())
	if err != nil {
		return err
	}
	if !isLocalAddr {
		return fmt.Errorf("the collection command can not be remotely operated")
	}

	if valid := utils.IsInputStringValid(message.GetWorkload()); !valid {
		return fmt.Errorf("input:%s is invalid", message.GetWorkload())
	}

	if valid, _ := regexp.MatchString("^[a-zA-Z]+(_[a-zA-Z0-9]+)*$", message.GetOutputDir()); !valid {
		return fmt.Errorf("output dir:%s is invalid", message.GetOutputDir())
	}

	if valid := utils.IsInputStringValid(message.GetType()); !valid {
		return fmt.Errorf("input:%s is invalid", message.GetType())
	}

	if valid := utils.IsInputStringValid(message.GetBlock()); !valid {
		return fmt.Errorf("input:%s is invalid", message.GetBlock())
	}

	if valid := utils.IsInputStringValid(message.GetNetwork()); !valid {
		return fmt.Errorf("input:%s is invalid", message.GetNetwork())
	}

	classProfile := &sqlstore.GetClass{Class: message.GetType()}
	if err = sqlstore.GetClasses(classProfile); err != nil {
		return err
	}
	if len(classProfile.Result) == 0 {
		return fmt.Errorf("app type %s is not exist, use define command first", message.GetType())
	}

	profileType := classProfile.Result[0].ProfileType
	include, err := profile.GetProfileInclude(profileType)
	if err != nil {
		return err
	}

	outputDir := path.Join(config.DefaultCollectionPath, message.GetOutputDir())
	exist, err := utils.PathExist(message.GetOutputDir())
	if err != nil {
		return err
	}
	if !exist {
		_ = os.MkdirAll(outputDir, 0755)
	}

	if err = utils.InterfaceByName(message.GetNetwork()); err != nil {
		return err
	}

	if err = utils.DiskByName(message.GetBlock()); err != nil {
		return err
	}

	collections, err := sqlstore.GetCollections()
	if err != nil {
		log.Errorf("inquery collection tables error: %v", err)
		return err
	}

	monitors := make([]Monitor, 0)
	for _, collection := range collections {
		re := regexp.MustCompile(`\{([^}]+)\}`)
		matches := re.FindAllStringSubmatch(collection.Metrics, -1)
		if len(matches) > 0 {
			for _, match := range matches {
				if len(match) < 2 {
					continue
				}

				var value string
				if match[1] == "disk" {
					value = message.GetBlock()
				} else if match[1] == "network" {
					value = message.GetNetwork()
				} else if match[1] == "interval" {
					value = strconv.FormatInt(message.GetInterval(), 10)
				} else {
					log.Warnf("%s is not recognized", match[1])
					continue
				}
				re = regexp.MustCompile(`\{(` + match[1] + `)\}`)
				collection.Metrics = re.ReplaceAllString(collection.Metrics, value)
			}
		}

		monitor := Monitor{Module: collection.Module, Purpose: collection.Purpose, Field: collection.Metrics}
		monitors = append(monitors, monitor)
	}

	collectorBody := new(CollectorPost)
	collectorBody.SampleNum = int(message.GetDuration() / message.GetInterval())
	collectorBody.Monitors = monitors
	nowTime := time.Now().Format("20060702-150405")
	fileName := fmt.Sprintf("%s-%s.csv", message.GetWorkload(), nowTime)
	collectorBody.File = path.Join(outputDir, fileName)
	if include == "" {
		include = "default"
	}
	collectorBody.DataType = fmt.Sprintf("%s:%s", include, message.GetType())

	_ = stream.Send(&PB.AckCheck{Name: "start to collect data"})

	_, err = collectorBody.Post()
	if err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}

	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("generate %s successfully", collectorBody.File)})
	return nil
}

/*
Training method train the collected data to generate the model
*/
func (s *ProfileServer) Training(message *PB.TrainMessage, stream PB.ProfileMgr_TrainingServer) error {
	isLocalAddr, err := SVC.CheckRpcIsLocalAddr(stream.Context())
	if err != nil {
		return err
	}
	if !isLocalAddr {
		return fmt.Errorf("the train command can not be remotely operated")
	}

	DataPath := message.GetDataPath()
	ModelName := message.GetModelName()

	compressPath, err := utils.CreateCompressFile(DataPath)
	if err != nil {
		log.Debugf("Failed to compress %s: %v", DataPath, err)
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}
	defer os.Remove(compressPath)

	trainPath, err := Post("training", "file", compressPath)
	if err != nil {
		log.Debugf("Failed to transfer file: %v", err)
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}

	trainBody := new(models.Training)
	trainBody.DataPath = trainPath
	trainBody.ModelName = ModelName
	trainBody.ModelPath = path.Join(config.DefaultAnalysisPath, "models")

	success, err := trainBody.Post()
	if err != nil {
		return err
	}
	if success {
		_ = stream.Send(&PB.AckCheck{Name: "training the self collect data success"})
		return nil
	}

	_ = stream.Send(&PB.AckCheck{Name: "training the self collect data failed"})
	return nil
}

// Detecting method detect the misclassified data
func (s *ProfileServer) Detecting(message *PB.DetectMessage, stream PB.ProfileMgr_DetectingServer) error {
	AppName := message.GetAppName()
	DetectPath := message.GetDetectPath()
	_ = stream.Send(&PB.AckCheck{Name: "Detecting the misclassified data"})

	detectBody := new(models.Detecting)
	detectBody.AppName = AppName
	detectBody.DetectPath = DetectPath

	success, detecterr, result := detectBody.Get()

	if detecterr != nil {
		return detecterr
	}

	if success {
		_ = stream.Send(&PB.AckCheck{Name: "Detecting misclassified data success\n"})
		s := strings.Split(result[1:(len(result)-2)], "@")
		for _, str := range s {
			_ = stream.Send(&PB.AckCheck{Name: str})
		}
		return nil
	}

	_ = stream.Send(&PB.AckCheck{Name: "Detecting misclassified data failed"})
	return nil
}

// Define method user define workload type and profile
func (s *ProfileServer) Define(ctx context.Context, message *PB.DefineMessage) (*PB.Ack, error) {
	isLocalAddr, err := SVC.CheckRpcIsLocalAddr(ctx)
	if err != nil {
		return &PB.Ack{}, err
	}
	if !isLocalAddr {
		return &PB.Ack{}, fmt.Errorf("the define command can not be remotely operated")
	}

	serviceType := message.GetServiceType()
	applicationName := message.GetApplicationName()
	scenarioName := message.GetScenarioName()
	content := string(message.GetContent())

	detectRule := `[./].*`
	detectPathchar := regexp.MustCompile(detectRule)

	if detectPathchar.MatchString(serviceType) {
		return &PB.Ack{}, fmt.Errorf("serviceType:%s cannot contain special path characters '/' or '.' ", serviceType)
	}
	if !utils.IsInputStringValid(serviceType) {
		return &PB.Ack{}, fmt.Errorf("input:%s is invalid", serviceType)
	}

	if detectPathchar.MatchString(applicationName) {
                return &PB.Ack{}, fmt.Errorf("applicationName:%s cannot contain special path characters '/' or '.' ", applicationName)
        }
	if !utils.IsInputStringValid(applicationName) {
		return &PB.Ack{}, fmt.Errorf("input:%s is invalid", applicationName)
	}

	if detectPathchar.MatchString(scenarioName) {
                return &PB.Ack{}, fmt.Errorf("scenarioName:%s cannot contain special path characters '/' or '.' ", scenarioName)
        }
	if !utils.IsInputStringValid(scenarioName) {
		return &PB.Ack{}, fmt.Errorf("input:%s is invalid", scenarioName)
	}

	profileName := serviceType + "-" + applicationName + "-" + scenarioName
	workloadTypeExist, err := sqlstore.ExistWorkloadType(profileName)
	if err != nil {
		return &PB.Ack{}, err
	}
	if !workloadTypeExist {
		if err = sqlstore.InsertClassApps(&sqlstore.ClassApps{
			Class:     profileName,
			Apps:      profileName,
			Deletable: true}); err != nil {
			return &PB.Ack{}, err
		}
	}

	profileNameExist, err := sqlstore.ExistProfileName(profileName)
	if err != nil {
		return &PB.Ack{}, err
	}
	if !profileNameExist {
		if err = sqlstore.InsertClassProfile(&sqlstore.ClassProfile{
			Class:       profileName,
			ProfileType: profileName,
			Active:      false}); err != nil {
			return &PB.Ack{}, err
		}
	}

	profileExist, err := profile.ExistProfile(profileName)
	if err != nil {
		return &PB.Ack{}, err
	}

	if profileExist {
		return &PB.Ack{Status: fmt.Sprintf("%s is already exist", profileName)}, nil
	}

	dstPath := path.Join(config.DefaultProfilePath, serviceType, applicationName)
	err = utils.CreateDir(dstPath, utils.FilePerm)
	if err != nil {
		return &PB.Ack{}, err
	}

	dstFile := path.Join(dstPath, fmt.Sprintf("%s.conf", scenarioName))
	err = utils.WriteFile(dstFile, content, utils.FilePerm, os.O_WRONLY|os.O_CREATE)
	if err != nil {
		log.Error(err)
		return &PB.Ack{}, err
	}

	return &PB.Ack{Status: "OK"}, nil
}

// Delete method delete the self define workload type from database
func (s *ProfileServer) Delete(ctx context.Context, message *PB.ProfileInfo) (*PB.Ack, error) {
	isLocalAddr, err := SVC.CheckRpcIsLocalAddr(ctx)
	if err != nil {
		return &PB.Ack{}, err
	}
	if !isLocalAddr {
		return &PB.Ack{}, fmt.Errorf("the undefine command can not be remotely operated")
	}

	profileName := message.GetName()

	classApps := &sqlstore.GetClassApp{Class: profileName}
	if err = sqlstore.GetClassApps(classApps); err != nil {
		return &PB.Ack{}, err
	}

	if len(classApps.Result) != 1 || !classApps.Result[0].Deletable {
		return &PB.Ack{Status: "only self defined type can be deleted"}, nil
	}

	if err = sqlstore.DeleteClassApps(profileName); err != nil {
		return &PB.Ack{}, err
	}

	profileNameExist, err := sqlstore.ExistProfileName(profileName)
	if err != nil {
		return &PB.Ack{}, err
	}
	if profileNameExist {
		if err := sqlstore.DeleteClassProfile(profileName); err != nil {
			log.Errorf("delete item from class_profile table failed %v ", err)
		}
	}

	if err := profile.DeleteProfile(profileName); err != nil {
		log.Errorf("delete item from profile table failed %v", err)
	}

	return &PB.Ack{Status: "OK"}, nil
}

// Update method update the content of the specified workload type from database
func (s *ProfileServer) Update(ctx context.Context, message *PB.ProfileInfo) (*PB.Ack, error) {
	isLocalAddr, err := SVC.CheckRpcIsLocalAddr(ctx)
	if err != nil {
		return &PB.Ack{}, err
	}
	if !isLocalAddr {
		return &PB.Ack{}, fmt.Errorf("the update command can not be remotely operated")
	}

	profileName := message.GetName()
	content := string(message.GetContent())

	profileExist, err := profile.ExistProfile(profileName)
	if err != nil {
		return &PB.Ack{}, err
	}

	if !profileExist {
		return &PB.Ack{}, fmt.Errorf("profile name %s is exist", profileName)
	}

	err = profile.UpdateProfile(profileName, content)
	if err != nil {
		return &PB.Ack{}, err
	}
	return &PB.Ack{Status: "OK"}, nil
}

// Schedule cpu/irq/numa ...
func (s *ProfileServer) Schedule(message *PB.ScheduleMessage,
	stream PB.ProfileMgr_ScheduleServer) error {
	pids := message.GetApp()
	Strategy := message.GetStrategy()

	scheduler := schedule.GetScheduler()

	ch := make(chan *PB.AckCheck)
	defer close(ch)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	err := scheduler.Schedule(pids, Strategy, true, ch)

	if err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error(), Status: utils.FAILD})
		return err
	}

	_ = stream.Send(&PB.AckCheck{Name: "schedule finished"})
	return nil
}

func (s *ProfileServer) collection(npipe string, time string) (*RespCollectorPost, error) {
	//1. get the dimension structure of the system data to be collected
	collections, err := sqlstore.GetCollections()
	if err != nil {
		log.Errorf("inquery collection tables error: %v", err)
		return nil, err
	}

	// 1.1 send the collect data command to the monitor service
	monitors := make([]Monitor, 0)
	for _, collection := range collections {
		re := regexp.MustCompile(`\{([^}]+)\}`)
		matches := re.FindAllStringSubmatch(collection.Metrics, -1)
		if len(matches) > 0 {
			for _, match := range matches {
				if len(match) < 2 {
					continue
				}
				var value string
				if s.Raw.Section("system").Haskey(match[1]) {
					value = s.Raw.Section("system").Key(match[1]).Value()
				} else if s.Raw.Section("server").Haskey(match[1]) {
					value = s.Raw.Section("server").Key(match[1]).Value()
				} else {
					return nil, fmt.Errorf("%s is not exist in the system or server section", match[1])
				}
				re = regexp.MustCompile(`\{(` + match[1] + `)\}`)
				collection.Metrics = re.ReplaceAllString(collection.Metrics, value)
			}
		}

		monitor := Monitor{Module: collection.Module, Purpose: collection.Purpose, Field: collection.Metrics}
		monitors = append(monitors, monitor)
	}

	sampleNum := s.Raw.Section("server").Key("sample_num").MustInt(20)
	if sampleNum == 0 {
		sampleNum = 20
	}

	if time != "" {
		sampleNum, err = strconv.Atoi(time)
		if err != nil {
			return nil, err
		}
	}

	collectorBody := new(CollectorPost)
	collectorBody.SampleNum = sampleNum
	collectorBody.Monitors = monitors
	collectorBody.File = path.Join(config.DefaultCollectionPath, "test.csv")
	if npipe != "" {
		collectorBody.Pipe = npipe
	}

	log.Infof("tuning collector body is %v", collectorBody)
	respCollectPost, err := collectorBody.Post()
	if err != nil {
		return nil, err
	}
	return respCollectPost, nil
}

func (s *ProfileServer) classify(dataPath string, customeModel string) (int, string, string, error) {
	//2. send the collected data to the model for completion type identification
	var resourceLimit string
	var workloadType string
	var bottleneck int
	localPath, timestamp, err := utils.ChangeFileName(dataPath)
	if err != nil {
		log.Errorf("Failed to change file name: %v", localPath)
		return bottleneck, workloadType, resourceLimit, err
	}
	defer os.Remove(localPath)

	absPath, _ := filepath.Split(localPath)
	logPath := absPath + "test-" + timestamp + ".log"
	log.Infof("log file path: %s", logPath)
	_, err = os.OpenFile(logPath, os.O_WRONLY|os.O_CREATE, 0640)
	if err != nil {
		log.Errorf("Failed to create log file: %v", err)
		return bottleneck, workloadType, resourceLimit, err
	}

	dataPath, err = Post("classification", "file", localPath)
	if err != nil {
		log.Errorf("Failed transfer file to server: %v", err)
		return bottleneck, workloadType, resourceLimit, err
	}

	body := new(ClassifyPostBody)
	body.Data = dataPath
	body.ModelPath = path.Join(config.DefaultAnalysisPath, "models")

	if customeModel != "" {
		body.Model = customeModel
	}
	respPostIns, err := body.Post()
	if err != nil {
		return bottleneck, workloadType, resourceLimit, err
	}

	log.Infof("workload: %s, cluster result resource limit: %s",
		respPostIns.WorkloadType, respPostIns.ResourceLimit)
	resourceLimit = respPostIns.ResourceLimit
	workloadType = respPostIns.WorkloadType
	bottleneck = respPostIns.Bottleneck
	return bottleneck, workloadType, resourceLimit, nil
}

func (s *ProfileServer) Getworkload() (string, error) {
	var npipe string
	var customeModel string
	respCollectPost, err := s.collection(npipe, "")
	if err != nil {
		return "", err
	}

	_, workload, _, err := s.classify(respCollectPost.Path, customeModel)
	if err != nil {
		return "", err
	}
	if len(workload) == 0 {
		return "", fmt.Errorf("workload is empty")
	}
	return workload, nil
}

// Generate method generate the yaml file for tuning
func (s *ProfileServer) Generate(message *PB.ProfileInfo, stream PB.ProfileMgr_GenerateServer) error {
	ch := make(chan *PB.AckCheck)
	defer close(ch)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	_ = stream.Send(&PB.AckCheck{Name: "1.Start to analysis the system bottleneck"})
	var npipe string
	respCollectPost, err := s.collection(npipe, "")
	if err != nil {
		return err
	}
	log.Infof("collect data response body is: %+v", respCollectPost)
	collectData := respCollectPost.Data
	projectName := message.GetName()

	_ = stream.Send(&PB.AckCheck{Name: "2.Finding potential tuning parameters"})

	var tuningData tuning.TuningData
	err = mapstructure.Decode(collectData, &tuningData)
	if err != nil {
		return err
	}
	log.Infof("decode to structure is: %+v", tuningData)

	ruleFile := path.Join(config.DefaultRulePath, config.TuningRuleFile)
	engine := tuning.NewRuleEngine(ruleFile)
	if engine == nil {
		return fmt.Errorf("create rules engine failed")
	}

	tuningFile := tuning.NewTuningFile(projectName, ch)
	err = tuningFile.Load()
	if err != nil {
		return err
	}
	err = engine.AddContext("TuningData", &tuningData)
	if err != nil {
		return err
	}

	err = engine.AddContext("TuningFile", tuningFile)
	if err != nil {
		return err
	}

	err = engine.Execute()
	if err != nil {
		return err
	}

	if len(tuningFile.PrjSrv.Object) <= 0 {
		_ = stream.Send(&PB.AckCheck{Name: "   No tuning parameters founed"})
		return nil
	}
	dstFile := path.Join(config.DefaultTuningPath, fmt.Sprintf("%s.yaml", projectName))
	log.Infof("generate tuning file: %s", dstFile)

	err = tuningFile.Save(dstFile)
	if err != nil {
		return err
	}
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("3. Generate tuning project: %s\n    project name: %s", dstFile, projectName)})

	return nil
}
