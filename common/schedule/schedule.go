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

package schedule

import (
	PB "atune/api/profile"
	"atune/common/config"
	"atune/common/http"
	"atune/common/log"
	"atune/common/registry"
	"atune/common/sched"
	"atune/common/schedule/framework"
	"atune/common/schedule/plugins"
	"atune/common/sqlstore"
	"atune/common/sysload"
	"atune/common/topology"
	"atune/common/utils"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"strconv"
	"strings"

	"github.com/go-ini/ini"
)

func sendChanToAdm(ch chan *PB.AckCheck, item string, status string, description string) {
	if ch == nil {
		return
	}

	ch <- &PB.AckCheck{Name: item, Status: status, Description: description}
}

// ConfigPutBody :body send to CPI service
type ConfigPutBody struct {
	Section string `json:"section"`
	Key     string `json:"key"`
	Value   string `json:"value"`
}

// RespPut ; response of call CPI service
type RespPut struct {
	Status string `json:"status"`
	Value  string `json:"value"`
}

// Put schedule config
func (c *ConfigPutBody) Put() (*RespPut, error) {
	url := config.GetURL(config.ConfiguratorURI)
	res, err := http.Put(url, c)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("connect to configurator service faild")
	}
	resBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respPutIns := new(RespPut)
	err = json.Unmarshal(resBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil
}

// Get schedule config
func (c *ConfigPutBody) Get() (*RespPut, error) {
	url := config.GetURL(config.ConfiguratorURI)
	res, err := http.Get(url, c)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("connect to configurator service faild")
	}
	resBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respPutIns := new(RespPut)
	err = json.Unmarshal(resBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil
}

// Scheduler class
type Scheduler struct {
	schedule []*sqlstore.Schedule
	plugins  map[string]framework.Plugin
	load     *sysload.SystemLoad
}

var instance *Scheduler = nil

// Init schedule table
func (s *Scheduler) Init() error {
	s.schedule = sqlstore.GetSchedule()

	topology.InitTopo()
	s.load = sysload.NewSysload()

	s.plugins = make(map[string]framework.Plugin)

	for name, factory := range plugins.PluginTables() {
		p, err := factory()
		if err != nil {
			return fmt.Errorf("init plugin %s fail:%v", name, err)
		}
		s.plugins[name] = p
	}

	return nil
}

// Schedule :update database and do schedule
func (s *Scheduler) Schedule(pids string, strategy string, save bool, ch chan *PB.AckCheck) error {
	//
	err := s.DoSchedule(pids, strategy, ch)
	return err
}

func setTaskAffinity(tid int, node *topology.TopoNode) error {
	var cpus []uint32

	for cpu := node.Mask().Foreach(-1); cpu != -1; cpu = node.Mask().Foreach(cpu) {
		cpus = append(cpus, uint32(cpu))
	}
	log.Info("bind ", tid, " to cpu ", cpus)
	if err := sched.SetAffinity(uint64(tid), cpus); err != nil {
		return err
	}
	return nil
}

func bindTaskToTopoNode(taskInfo *[]framework.BindTaskInfo) {
	for _, ti := range *taskInfo {
		if err := setTaskAffinity(ti.Pid, ti.Node); err != nil {
			log.Error(err)
		}
	}
}

type updateLoadCallback struct {
	load *sysload.SystemLoad
}

// callback to update cpu load
func (callback *updateLoadCallback) Callback(node *topology.TopoNode) {
	cpu := node.ID()
	load := callback.load.GetCPULoad(cpu)
	node.SetLoad(load)
}

func updateNodeLoad(load *sysload.SystemLoad) {
	var callback updateLoadCallback

	callback.load = load
	topology.ForeachTypeCall(topology.TopoTypeCPU, &callback)
}

// DoSchedule : run schedule plugin and tune
func (s *Scheduler) DoSchedule(pids string, strategy string, ch chan *PB.AckCheck) error {

	log.Infof("do schedule: %s for %s", strategy, pids)
	plugin, ok := s.plugins[strategy]
	var taskinfo []framework.BindTaskInfo

	if !ok {
		return fmt.Errorf("strategy not support : %s", strategy)
	}

	for _, pidstr := range strings.Split(pids, ",") {
		var ti framework.BindTaskInfo
		pid, err := strconv.Atoi(pidstr)
		if err != nil {
			return fmt.Errorf("pids error : %s", err)
		}
		ti.Pid = pid
		ti.Node = topology.DefaultSelectNode()
		taskinfo = append(taskinfo, ti)
	}

	s.load.Update()
	updateNodeLoad(s.load)

	plugin.Preprocessing(&taskinfo)
	sendChanToAdm(ch, "Preprocessing", utils.SUCCESS, "")

	plugin.PickNodesforPids(&taskinfo)
	sendChanToAdm(ch, "PickNodesforPids Results:", utils.SUCCESS, "")

	for _, ti := range taskinfo {
		sendChanToAdm(ch, strconv.Itoa(ti.Pid), utils.INFO, fmt.Sprintf(
			"type:%v id:%v", ti.Node.Type(), ti.Node.ID()))
	}

	bindTaskToTopoNode(&taskinfo)
	sendChanToAdm(ch, "bindTaskToTopoNode finished", utils.SUCCESS, "")

	plugin.Postprocessing(&taskinfo)
	sendChanToAdm(ch, "Postprocessing", utils.SUCCESS, "")

	return nil
}

// Active schedule strategy
func (s *Scheduler) Active(ch chan *PB.AckCheck, itemKeys []string, items map[string]*ini.File) error {
	for _, item := range itemKeys {
		value := items[item]
		if value == nil {
			continue
		}
		for _, section := range value.Sections() {
			if section.Name() == "main" {
				continue
			}
			if section.Name() == "DEFAULT" {
				continue
			}
			if section.Name() == "tip" {
				for _, key := range section.Keys() {
					description := key.Name()
					sendChanToAdm(ch, key.Value(), utils.SUGGEST, description)
				}
				continue
			}
			if section.Name() == "schedule" {
				for _, key := range section.Keys() {
					_ = s.Schedule(key.Name(), key.Value(), false, ch)
				}
				continue
			}

			if section.Name() == "check" {
				if !section.HasKey("check_environment") {
					continue
				}
				if section.Key("check_environment").Value() != "on" {
					continue
				}

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

					if !registry.IsCheckDisabled(service.Instance) {
						continue
					}
					err := checkerService.Check(ch)
					if err != nil {
						log.Errorf("service %s running faild, reason: %v", service.Name, err)
						continue
					}
				}
				continue
			}

			var statusStr string = "OK"
			message := make([]string, 0)
			for _, key := range section.Keys() {
				scriptKey := key.Name()
				value := key.Value()
				body := &ConfigPutBody{
					Section: section.Name(),
					Key:     scriptKey,
					Value:   value,
				}
				respPutIns, err := body.Put()
				if err != nil {
					statusStr = err.Error()
					continue
				}

				log.Infof("active parameter, key: %s, value: %s, status:%s", scriptKey, value, respPutIns.Status)
				if respPutIns.Status == "OK" {
					message = append(message, scriptKey)
				} else {
					if statusStr != utils.ERROR {
						statusStr = respPutIns.Status
					}
					message = append(message, respPutIns.Value)
				}
			}

			message = utils.RemoveDuplicateElement(message)
			status := strings.ToUpper(statusStr)
			if status == "OK" {
				sendChanToAdm(ch, item, utils.SUCCESS, strings.Join(message, ","))
			} else if status == utils.WARNING {
				sendChanToAdm(ch, item, utils.SUGGEST, strings.Join(message, ","))
			} else {
				sendChanToAdm(ch, item, utils.FAILD, strings.Join(message, ","))
			}
		}
	}

	return nil
}

// GetScheduler : get schedule instance
func GetScheduler() *Scheduler {
	if instance == nil {
		instance = new(Scheduler)
		_ = instance.Init()
	}

	return instance
}
