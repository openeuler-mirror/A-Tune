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

package schedule

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"io"
	"os"
	"strings"

	"github.com/go-ini/ini"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/http"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/models"
	"gitee.com/openeuler/A-Tune/common/registry"
	"gitee.com/openeuler/A-Tune/common/sqlstore"
	"gitee.com/openeuler/A-Tune/common/utils"
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
		return nil, fmt.Errorf("connect to configurator service failed")
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
		return nil, fmt.Errorf("connect to configurator service failed")
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
	id       int
}

var instance *Scheduler = nil

// Init schedule table
func (s *Scheduler) Init() error {
	s.schedule = sqlstore.GetSchedule()

	return nil
}

// SetScheduleId method set id to scheduler
func (s *Scheduler) SetScheduleId(scheduleId int) {
	s.id = scheduleId
}

// Schedule :update database and do schedule
func (s *Scheduler) Schedule(pids string, strategy string, save bool, ch chan *PB.AckCheck) error {
	schedManager, err := GetScheduleManager()
	if err != nil {
		return err
	}

	scheduler, err := schedManager.New(strategy,
		pids,
		WithChannel(ch),
	)

	if err != nil {
		return err
	}

	schedManager.Submit(scheduler)
	schedManager.Start()

	return nil
}

// Active schedule strategy
func (s *Scheduler) Active(ch chan *PB.AckCheck, itemKeys []string, items map[string]*ini.File) error {
	logStr := ""
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
					log.Infof("tip key name: %s, key value: %s", key.Name(), key.Value())
					currLog := section.Name() + "|" + key.Name() + "|" + key.Value() + "|"
					logStr += currLog + "\n"
					_, err := models.InitTransfer("log", "running", currLog, "", s.id)
					if err != nil {
						log.Errorf("log info write error: transfer data %v", err)
					}
				}
				continue
			}
			if section.Name() == "schedule" {
				for _, key := range section.Keys() {
					_ = s.Schedule(key.Name(), key.Value(), false, ch)
					currLog := section.Name() + "|" + key.Name() + "|" + key.Value() + "|"
					logStr += currLog + "\n"
					_, err := models.InitTransfer("log", "running", currLog, "", s.id)
					if err != nil {
						log.Errorf("log info write error: transfer data %v", err)
					}
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

					if !registry.IsCheckDisabled(service.Instance) {
						continue
					}
					err := checkerService.Check(ch)
					if err != nil {
						log.Errorf("service %s running failed, reason: %v", service.Name, err)
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
				currLog := section.Name() + "|" + statusStr + "|" + key.Name() + "|" + key.Value() + "|"
				if statusStr != "OK" {
					currLog += respPutIns.Value
				}
				logStr += currLog + "\n"
				_, err = models.InitTransfer("log", "running", currLog, "", s.id)
				if err != nil {
					log.Errorf("log info write error: transfer data %v", err)
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

	logFile, err := utils.GetLogFilePath(config.DefaultTempPath)
	if err != nil {
		log.Infof("get log file path failed: %v", err)
	} else {
		file, err := os.OpenFile(logFile, os.O_APPEND|os.O_WRONLY, 0640)
		if err != nil {
			return fmt.Errorf("open file failed: %v", err)
		}
		defer file.Close()

		_, err = io.WriteString(file, logStr)
		if err != nil {
			log.Errorf("write to log failed: %v", err)
		}
	}

	_, err = models.InitTransfer("log", "finished", "", "", s.id)
	if err != nil {
		log.Errorf("log info write error: transfer data %v", err)
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
