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

package main

import (
	PB "atune/api/profile"
	_ "atune/common/checker"
	"atune/common/config"
	"atune/common/http"
	"atune/common/log"
	"atune/common/models"
	"atune/common/profile"
	"atune/common/project"
	"atune/common/registry"
	"atune/common/schedule"
	SVC "atune/common/service"
	"atune/common/sqlstore"
	"atune/common/tuning"
	"atune/common/utils"
	"bufio"
	"context"
	"encoding/json"
	"fmt"
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
	Data      string `json:"data"`
	ModelPath string `json:"modelpath,omitempty"`
	Model     string `json:"model,omitempty"`
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
		return nil, fmt.Errorf("faild to parse %s, %v", defaultConfigFile, err)
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
		return nil, fmt.Errorf("online learning faild")
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
		return nil, fmt.Errorf("collect data faild")
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
	profileNames := profileInfo.GetName()

	profile, ok := profile.LoadFromWorkloadType(profileNames)

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
	workloads := &sqlstore.GetClass{}
	err := sqlstore.GetClasses(workloads)
	if err != nil {
		return err
	}

	for _, classProfile := range workloads.Result {
		_ = stream.Send(&PB.ListMessage{WorkloadType: classProfile.Class,
			ProfileNames: classProfile.ProfileType,
			Active:       strconv.FormatBool(classProfile.Active)})
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
			return fmt.Errorf("service init faild: %v", err)
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
			log.Errorf("service %s running faild, reason: %v", service.Name, err)
			continue
		}
	}

	return nil
}

// Analysis method analysis the system traffic load
func (s *ProfileServer) Analysis(message *PB.AnalysisMessage, stream PB.ProfileMgr_AnalysisServer) error {
	if !s.TryLock() {
		return fmt.Errorf("analysis has been in running")
	}
	defer s.Unlock()

	_ = stream.Send(&PB.AckCheck{Name: "1. Analysis system runtime information: CPU Memory IO and Network..."})

	npipe, err := utils.CreateNamedPipe()
	if err != nil {
		return fmt.Errorf("create named pipe faild")
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

	//2. send the collected data to the model for completion type identification
	body := new(ClassifyPostBody)
	body.Data = respCollectPost.Path
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
	if err := sqlstore.GetClasses(classProfile); err != nil {
		log.Errorf("inquery workload type table faild %v", err)
		return fmt.Errorf("inquery workload type table faild %v", err)
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
func (s *ProfileServer) Tuning(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_TuningServer) error {
	//dynamic profle setting
	data := profileInfo.GetName()
	content := profileInfo.GetContent()

	ch := make(chan *PB.AckCheck)
	go func() {
		for value := range ch {
			_ = stream.Send(value)
		}
	}()

	// data == "" means in tuning process
	if data == "" {
		benchmark := tuning.BenchMark{Content: content}
		err := benchmark.DynamicTuned(ch)
		if err != nil {
			return err
		}
		return nil
	}

	prjfound := false
	var prjs []*project.YamlPrjSvr
	err := filepath.Walk(config.DefaultTuningPath, func(path string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			prj, ret := project.LoadProject(path)
			if ret != nil {
				log.Errorf("load %s faild(%s)", path, ret)
				return ret
			}
			log.Infof("project:%s load %s success", prj.Project, path)
			prjs = append(prjs, prj)
		}
		return nil
	})

	if err != nil {
		return err
	}

	var prj *project.YamlPrjSvr
	for _, prj = range prjs {
		if data == prj.Project {
			log.Infof("found Project:%v", prj.Project)
			prjfound = true
			break
		}
	}

	if !prjfound {
		log.Errorf("project:%s not found", data)
		return fmt.Errorf("project:%s not found", data)
	}

	//content == nil means in restore config
	if content == nil {
		optimizer := tuning.Optimizer{Prj: prj}
		err := optimizer.RestoreConfigTuned()
		if err != nil {
			return err
		}
		return nil
	}

	log.Info("begin to dynamic optimizer search")
	_ = stream.Send(&PB.AckCheck{Name: fmt.Sprintf("begin to dynamic optimizer search")})

	optimizer := tuning.Optimizer{Prj: prj}
	iter, _ := strconv.Atoi(string(content))
	log.Infof("client ask iterations:%d", iter)
	err = optimizer.InitTuned(ch, iter)
	if err != nil {
		return err
	}

	return nil
}

/*
UpgradeProfile method update the db file
*/
func (s *ProfileServer) UpgradeProfile(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_UpgradeProfileServer) error {
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
	workloadType := profileInfo.GetName()
	classProfile := &sqlstore.GetClass{Class: workloadType}
	err := sqlstore.GetClasses(classProfile)
	if err != nil {
		log.Errorf("inquery class_profile table faild")
		return fmt.Errorf("inquery class_profile table faild")
	}

	if len(classProfile.Result) == 0 {
		log.Errorf("%s is not exist in the class_profile table", workloadType)
		return fmt.Errorf("%s is not exist in the class_profile table", workloadType)
	}

	profileType := classProfile.Result[0].ProfileType
	profileNames := strings.Split(profileType, ",")
	for _, name := range profileNames {
		name = strings.Trim(name, " ")
		context, _ := sqlstore.GetContext(name)
		context = "\n*** " + name + ":\n" + context
		_ = stream.Send(&PB.ProfileInfo{Name: context})
	}

	return nil
}

/*
CheckActiveProfile method check current active profile is effective
*/
func (s *ProfileServer) CheckActiveProfile(profileInfo *PB.ProfileInfo,
	stream PB.ProfileMgr_CheckActiveProfileServer) error {
	log.Debug("Begin to check active profiles\n")
	profiles := &sqlstore.GetClass{Active: true}
	err := sqlstore.GetClasses(profiles)
	if err != nil {
		return err
	}
	if len(profiles.Result) != 1 {
		return fmt.Errorf("no active profile or more than 1 active profile")
	}

	workloadType := profiles.Result[0].Class
	profile, ok := profile.LoadFromWorkloadType(workloadType)

	if !ok {
		log.WithField("profile", workloadType).Errorf("Load profile %s Faild", workloadType)
		return fmt.Errorf("load workload type %s Faild", workloadType)
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
	err := sqlstore.GetClassApps(classApps)
	if err != nil {
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

	if err := utils.InterfaceByName(message.GetNetwork()); err != nil {
		return err
	}

	if err := utils.DiskByName(message.GetBlock()); err != nil {
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

	_ = stream.Send(&PB.AckCheck{Name: "training the self collect data faild"})
	return nil
}

// Charaterization method will be deprecate in the future
func (s *ProfileServer) Charaterization(profileInfo *PB.ProfileInfo, stream PB.ProfileMgr_CharaterizationServer) error {
	_ = stream.Send(&PB.AckCheck{Name: "1. Analysis system runtime information: CPU Memory IO and Network..."})

	npipe, err := utils.CreateNamedPipe()
	if err != nil {
		return fmt.Errorf("create named pipe faild")
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

	//2. send the collected data to the model for completion type identification
	body := new(ClassifyPostBody)
	body.Data = respCollectPost.Path
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
	workloadType := message.GetWorkloadType()
	profileName := message.GetProfileName()
	content := string(message.GetContent())

	workloadTypeExist, err := sqlstore.ExistWorkloadType(workloadType)
	if err != nil {
		return &PB.Ack{}, err
	}
	if workloadTypeExist {
		return &PB.Ack{Status: fmt.Sprintf("%s is already exist", workloadType)}, nil
	}

	profileExist, err := sqlstore.ExistProfile(profileName)
	if err != nil {
		return &PB.Ack{}, err
	}

	if profileExist {
		return &PB.Ack{Status: fmt.Sprintf("%s is already exist", profileName)}, nil
	}

	if err := sqlstore.InsertClassApps(&sqlstore.ClassApps{
		Class:     workloadType,
		Deletable: true}); err != nil {
		return &PB.Ack{}, err
	}
	if err := sqlstore.InsertClassProfile(&sqlstore.ClassProfile{
		Class:       workloadType,
		ProfileType: profileName,
		Active:      false}); err != nil {
		return &PB.Ack{}, err
	}

	if err := sqlstore.InsertProfile(&sqlstore.Profile{
		ProfileType:        profileName,
		ProfileInformation: content}); err != nil {
		return &PB.Ack{}, err
	}

	return &PB.Ack{Status: "OK"}, nil
}

// Delete method delete the self define workload type from database
func (s *ProfileServer) Delete(ctx context.Context, message *PB.DefineMessage) (*PB.Ack, error) {
	workloadType := message.GetWorkloadType()

	classApps := &sqlstore.GetClassApp{Class: workloadType}
	err := sqlstore.GetClassApps(classApps)
	if err != nil {
		return &PB.Ack{}, err
	}

	log.Infof("the result length: %d, query the classapp table of workload: %s", len(classApps.Result), workloadType)
	if len(classApps.Result) != 1 {
		return &PB.Ack{Status: fmt.Sprintf("workload type %s may be not exist in the table", workloadType)}, nil
	}

	classApp := classApps.Result[0]
	if !classApp.Deletable {
		return &PB.Ack{Status: "only self defined workload type can be deleted"}, nil
	}

	if err := sqlstore.DeleteClassApps(workloadType); err != nil {
		return &PB.Ack{}, err
	}

	// get the profile type from the classprofile table
	classProfile := &sqlstore.GetClass{Class: workloadType}
	if err := sqlstore.GetClasses(classProfile); err != nil {
		log.Errorf("inquery workload type table faild %v", err)
		return &PB.Ack{}, fmt.Errorf("inquery workload type table faild %v", err)
	}
	if len(classProfile.Result) == 0 {
		log.Errorf("%s is not exist in the table", workloadType)
		return &PB.Ack{}, fmt.Errorf("%s is not exist in the table", workloadType)
	}

	profileType := classProfile.Result[0].ProfileType
	profileNames := strings.Split(profileType, ",")
	if len(profileNames) == 0 {
		log.Errorf("No profile or invaild profiles were specified.")
		return &PB.Ack{}, fmt.Errorf("no profile or invaild profiles were specified")
	}

	// delete profile depend the profiletype
	for _, profileName := range profileNames {
		if err := sqlstore.DeleteProfile(profileName); err != nil {
			log.Errorf("delete item from profile table faild %v ", err)
		}
	}

	// delete classprofile depend the workloadType
	if err := sqlstore.DeleteClassProfile(workloadType); err != nil {
		log.Errorf("delete item from classprofile tabble faild.")
		return &PB.Ack{}, err
	}
	return &PB.Ack{Status: "OK"}, nil
}

// Update method update the content of the specified workload type from database
func (s *ProfileServer) Update(ctx context.Context, message *PB.DefineMessage) (*PB.Ack, error) {
	workloadType := message.GetWorkloadType()
	profileName := message.GetProfileName()
	content := string(message.GetContent())

	workloadTypeExist, err := sqlstore.ExistWorkloadType(workloadType)
	if err != nil {
		return &PB.Ack{}, err
	}
	if !workloadTypeExist {
		return &PB.Ack{Status: fmt.Sprintf("workload type %s is not exist in the table", workloadType)}, nil
	}

	// get the profile type from the classprofile table
	classProfile := &sqlstore.GetClass{Class: workloadType}
	if err := sqlstore.GetClasses(classProfile); err != nil {
		log.Errorf("inquery workload type table faild %v", err)
		return &PB.Ack{}, fmt.Errorf("inquery workload type table faild %v", err)
	}
	if len(classProfile.Result) == 0 {
		log.Errorf("%s is not exist in the table", workloadType)
		return &PB.Ack{}, fmt.Errorf("%s is not exist in the table", workloadType)
	}

	profileType := classProfile.Result[0].ProfileType
	profileNames := strings.Split(profileType, ",")
	if len(profileNames) == 0 {
		log.Errorf("No profile or invaild profiles were specified.")
		return &PB.Ack{}, fmt.Errorf("no profile exist corresponding to workload type")
	}

	exist := false
	for _, profile := range profileNames {
		if profileName == strings.TrimSpace(profile) {
			exist = true
			break
		}
	}
	if !exist {
		return &PB.Ack{}, fmt.Errorf("profile name %s is exist corresponding to workload type %s",
			profileName, workloadType)
	}

	if err := sqlstore.UpdateProfile(&sqlstore.Profile{
		ProfileType:        profileName,
		ProfileInformation: content}); err != nil {
		return &PB.Ack{}, err
	}
	return &PB.Ack{Status: "OK"}, nil
}

// Schedule cpu/irq/numa ...
func (s *ProfileServer) Schedule(message *PB.ScheduleMessage,
	stream PB.ProfileMgr_ScheduleServer) error {
	_ = message.GetApp()
	Type := message.GetType()
	Strategy := message.GetStrategy()

	scheduler := schedule.GetScheduler()
	_ = scheduler.Schedule(Type, Strategy, true)

	return nil
}
