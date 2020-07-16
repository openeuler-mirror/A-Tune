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
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/go-ini/ini"
	"github.com/urfave/cli"
	"google.golang.org/grpc"
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
}

// RespCollectorPost : the response of collection servie
type RespCollectorPost struct {
	Path string `json:"path"`
}

// ClassifyPostBody : the body send to classify service
type ClassifyPostBody struct {
	Data      [][]string `json:"data"`
	ModelPath string     `json:"modelpath,omitempty"`
	Model     string     `json:"model,omitempty"`
}

// RespClassify : the response of classify model
type RespClassify struct {
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

// Profile method set the workload type to effective manual
func (s *ProfileServer) Profile(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_ProfileServer) error {
	profileNamesStr := profileInfo.GetName()
	profileNames := strings.Split(profileNamesStr, ",")
	profile, ok := profile.Load(profileNames)

	if !ok {
		fmt.Println("Failure Load ", profileInfo.GetName())
		return fmt.Errorf("load profile %s Faild", profileInfo.GetName())
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
			return fmt.Errorf("inquery workload type table faild %v", err)
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

// Analysis method analysis the system traffic load
func (s *ProfileServer) Analysis(message *PB.AnalysisMessage, stream PB.ProfileMgr_AnalysisServer) error {
	if !s.TryLock() {
		return fmt.Errorf("dynamic optimizer search or analysis has been in running")
	}
	defer s.Unlock()

	_ = stream.Send(&PB.AckCheck{Name: "1. Analysis system runtime information: CPU Memory IO and Network..."})

	npipe, err := utils.CreateNamedPipe()
	if err != nil {
		return fmt.Errorf("create named pipe failed")
	}

	defer os.Remove(npipe)

	go func() {
		file, _ := os.OpenFile(npipe, os.O_RDONLY, os.ModeNamedPipe)
		reader := bufio.NewReader(file)

		scanner := bufio.NewScanner(reader)

		for scanner.Scan() {
			line := scanner.Text()
			_ = stream.Send(&PB.AckCheck{Name: line, Status: utils.INFO})
		}
	}()

	//1. get the dimension structure of the system data to be collected
	collections, err := sqlstore.GetCollections()
	if err != nil {
		log.Errorf("inquery collection tables error: %v", err)
		return err
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
				if !s.Raw.Section("system").Haskey(match[1]) {
					return fmt.Errorf("%s is not exist in the system section", match[1])
				}
				value := s.Raw.Section("system").Key(match[1]).Value()
				collection.Metrics = re.ReplaceAllString(collection.Metrics, value)
			}
		}

		monitor := Monitor{Module: collection.Module, Purpose: collection.Purpose, Field: collection.Metrics}
		monitors = append(monitors, monitor)
	}

	sampleNum := s.Raw.Section("server").Key("sample_num").MustInt(20)
	collectorBody := new(CollectorPost)
	collectorBody.SampleNum = sampleNum
	collectorBody.Monitors = monitors
	collectorBody.Pipe = npipe

	respCollectPost, err := collectorBody.Post()
	if err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}

	data, err := utils.ReadCSV(respCollectPost.Path)
	if err != nil {
		log.Errorf("Failed to read data from CSV: %v", err)
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}

	//2. send the collected data to the model for completion type identification
	body := new(ClassifyPostBody)
	body.Data = data
	body.ModelPath = path.Join(config.DefaultAnalysisPath, "models")

	if message.GetModel() != "" {
		body.Model = message.GetModel()
	}
	respPostIns, err := body.Post()

	if err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}

	workloadType := respPostIns.WorkloadType
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n 2. Current System Workload Characterization is %s", workloadType)})

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
	log.Infof("workload %s support app: %s", workloadType, apps)
	log.Infof("workload %s resource limit: %s, cluster result resource limit: %s",
		workloadType, apps, respPostIns.ResourceLimit)

	_ = stream.Send(&PB.AckCheck{Name: "\n 3. Build the best resource model..."})

	//5. get the profile type depend on the workload type
	profileType := classProfile.Result[0].ProfileType
	profileNames := strings.Split(profileType, ",")
	if len(profileNames) == 0 {
		log.Errorf("No profile or invaild profiles were specified.")
		return fmt.Errorf("no profile or invaild profiles were specified")
	}

	//6. get the profile info depend on the profile type
	log.Infof("the resource model of the profile type is %s", profileType)
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n 4. Match profile: %s", profileType)})
	pro, _ := profile.Load(profileNames)
	pro.SetWorkloadType(workloadType)

	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n 5. bengin to set static profile")})
	log.Infof("bengin to set static profile")

	//static profile setting
	ch := make(chan *PB.AckCheck)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	_ = pro.RollbackActive(ch)

	rules := &sqlstore.GetRuleTuned{Class: workloadType}
	if err := sqlstore.GetRuleTuneds(rules); err != nil {
		return err
	}

	if len(rules.Result) < 1 {
		_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("Completed optimization, please restart application!")})
		log.Info("no rules to tuned")
		return nil
	}

	log.Info("begin to dynamic tuning depending on rules")
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n 6. bengin to set dynamic profile")})
	if err := tuning.RuleTuned(workloadType); err != nil {
		return err
	}

	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("Completed optimization, please restart application!")})
	return nil
}

// Tuning method calling the bayes search method to tuned parameters
func (s *ProfileServer) Tuning(stream PB.ProfileMgr_TuningServer) error {
	if !s.TryLock() {
		return fmt.Errorf("dynamic optimizer search or analysis has been in running")
	}
	defer s.Unlock()

	ch := make(chan *PB.AckCheck)
	defer close(ch)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	var optimizer = tuning.Optimizer{}
	for {
		reply, err := stream.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}

		data := reply.Name
		content := reply.Content

		//sync config with other server
		if data == "sync-config" {
			optimizer.Content = content
			if err = optimizer.SyncTunedNode(ch); err != nil {
				return err
			}
			continue
		}

		// data == "" means in tuning process
		if data == "" {
			optimizer.Content = content
			if err = optimizer.DynamicTuned(ch); err != nil {
				return err
			}
			continue
		}

		if err = tuning.CheckServerPrj(data, &optimizer); err != nil {
			return err
		}

		//content == nil means in restore config
		if content == nil {
			if err = optimizer.RestoreConfigTuned(ch); err != nil {
				return err
			}
			continue
		}

		optimizer.Content = content
		if err = optimizer.InitTuned(ch); err != nil {
			return err
		}
	}

	return nil
}

/*
UpgradeProfile method update the db file
*/
func (s *ProfileServer) UpgradeProfile(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_UpgradeProfileServer) error {
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

	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("upgrade success"), Status: utils.SUCCESS})
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
		return fmt.Errorf("inquery workload type table faild %v", err)
	}
	if len(classProfile.Result) > 0 {
		activeName = classProfile.Result[0].ProfileType
	}
	log.Debugf("active name is %s", activeName)

	profile, ok := profile.LoadFromProfile(activeName)

	if !ok {
		log.WithField("profile", activeName).Errorf("Load profile %s Faild", activeName)
		return fmt.Errorf("load profile %s Faild", activeName)
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

	if valid := utils.IsInputStringValid(message.GetOutputPath()); !valid {
		return fmt.Errorf("input:%s is invalid", message.GetOutputPath())
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

	classApps := &sqlstore.GetClassApp{Class: message.GetType()}
	if err = sqlstore.GetClassApps(classApps); err != nil {
		return err
	}
	if len(classApps.Result) == 0 {
		return fmt.Errorf("workload type %s is not exist, please use define command first", message.GetType())
	}

	exist, err := utils.PathExist(message.GetOutputPath())
	if err != nil {
		return err
	}
	if !exist {
		return fmt.Errorf("output_path %s is not exist", message.GetOutputPath())
	}

	if err = utils.InterfaceByName(message.GetNetwork()); err != nil {
		return err
	}

	if err = utils.DiskByName(message.GetBlock()); err != nil {
		return err
	}

	collector := path.Join(config.DefaultCollectorPath, "collect_training_data.sh")
	script := make([]string, 0)

	script = append(script, collector)
	script = append(script, message.GetWorkload())
	script = append(script, strconv.FormatInt(message.GetDuration(), 10))
	script = append(script, strconv.FormatInt(message.GetInterval(), 10))
	script = append(script, message.GetOutputPath())
	script = append(script, message.GetBlock())
	script = append(script, message.GetNetwork())
	script = append(script, message.GetType())

	newScript := strings.Join(script, " ")
	cmd := exec.Command("sh", "-c", newScript)
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}

	stdout, _ := cmd.StdoutPipe()
	stderr, _ := cmd.StderrPipe()

	ctx := stream.Context()
	go func() {
		for range ctx.Done() {
			_ = syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL)
			return
		}
	}()

	go func() {
		scanner := bufio.NewScanner(stdout)
		for scanner.Scan() {
			line := scanner.Text()
			_ = stream.Send(&PB.AckCheck{Name: line})
		}
	}()

	go func() {
		scanner := bufio.NewScanner(stderr)
		for scanner.Scan() {
			line := scanner.Text()
			_ = stream.Send(&PB.AckCheck{Name: line})
		}
	}()

	err = cmd.Start()
	if err != nil {
		log.Error(err)
		return err
	}

	err = cmd.Wait()

	if err != nil {
		log.Error(err)
		return err
	}

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
	OutputPath := message.GetOutputPath()

	trainBody := new(models.Training)
	trainBody.DataPath = DataPath
	trainBody.OutputPath = OutputPath
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

// Charaterization method will be deprecate in the future
func (s *ProfileServer) Charaterization(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_CharaterizationServer) error {
	_ = stream.Send(&PB.AckCheck{Name: "1. Analysis system runtime information: CPU Memory IO and Network..."})

	npipe, err := utils.CreateNamedPipe()
	if err != nil {
		return fmt.Errorf("create named pipe failed")
	}

	defer os.Remove(npipe)

	go func() {
		file, _ := os.OpenFile(npipe, os.O_RDONLY, os.ModeNamedPipe)
		reader := bufio.NewReader(file)

		scanner := bufio.NewScanner(reader)

		for scanner.Scan() {
			line := scanner.Text()
			_ = stream.Send(&PB.AckCheck{Name: line, Status: utils.INFO})
		}
	}()

	//1. get the dimension structure of the system data to be collected
	collections, err := sqlstore.GetCollections()
	if err != nil {
		log.Errorf("inquery collection tables error: %v", err)
		return err
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
				if !s.Raw.Section("system").Haskey(match[1]) {
					return fmt.Errorf("%s is not exist in the system section", match[1])
				}
				value := s.Raw.Section("system").Key(match[1]).Value()
				collection.Metrics = re.ReplaceAllString(collection.Metrics, value)
			}
		}

		monitor := Monitor{Module: collection.Module, Purpose: collection.Purpose, Field: collection.Metrics}
		monitors = append(monitors, monitor)
	}

	sampleNum := s.Raw.Section("server").Key("sample_num").MustInt(20)
	collectorBody := new(CollectorPost)
	collectorBody.SampleNum = sampleNum
	collectorBody.Monitors = monitors
	collectorBody.Pipe = npipe

	respCollectPost, err := collectorBody.Post()
	if err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}

	data, err := utils.ReadCSV(respCollectPost.Path)
	if err != nil {
		log.Errorf("Failed to read data from CSV: %v", err)
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}

	//2. send the collected data to the model for completion type identification
	body := new(ClassifyPostBody)
	body.Data = data
	body.ModelPath = path.Join(config.DefaultAnalysisPath, "models")

	respPostIns, err := body.Post()

	if err != nil {
		_ = stream.Send(&PB.AckCheck{Name: err.Error()})
		return err
	}

	workloadType := respPostIns.WorkloadType
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("\n 2. Current System Workload Characterization is %s", workloadType)})
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
	profileName := serviceType + "-" + applicationName + "-" + scenarioName

	workloadTypeExist, err := sqlstore.ExistWorkloadType(profileName)
	if err != nil {
		return &PB.Ack{}, err
	}
	if !workloadTypeExist {
		if err = sqlstore.InsertClassApps(&sqlstore.ClassApps{
			Class:     profileName,
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
