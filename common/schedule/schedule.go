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
	"atune/common/sqlstore"
	"atune/common/utils"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"strings"

	"github.com/go-ini/ini"
)

func sendChanToAdm(ch chan *PB.AckCheck, item string, status string, description string) {
	if ch == nil {
		return
	}

	ch <- &PB.AckCheck{Name: item, Status: status, Description: description}
}

type ConfigPutBody struct {
	Section string `json:"section"`
	Key     string `json:"key"`
	Value   string `json:"value"`
}

type respPut struct {
	Status string `json:status`
	Value  string `json:value`
}

func (c *ConfigPutBody) Put() (*respPut, error) {
	url := config.GetUrl(config.ConfiguratorURI)
	res, err := http.Put(url, c)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("connect to configurator service faild")
	}
	resBody, err := ioutil.ReadAll(res.Body)
	respPutIns := new(respPut)
	err = json.Unmarshal(resBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil

}

func (c *ConfigPutBody) Get() (*respPut, error) {
	url := config.GetUrl(config.ConfiguratorURI)
	res, err := http.Get(url, c)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("connect to configurator service faild")
	}
	resBody, err := ioutil.ReadAll(res.Body)
	respPutIns := new(respPut)
	err = json.Unmarshal(resBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil

}

type Scheduler struct {
	schedule []*sqlstore.Schedule
	name     string

	typename string
	strategy string
	IsExit   bool
}

var instance *Scheduler = nil

func (s *Scheduler) Init() error {
	s.schedule = sqlstore.GetSchedule()

	return nil
}

func (s *Scheduler) Schedule(typename string, strategy string, save bool) error {
	if save {
		sqlstore.UpdateSchedule(typename, strategy)

		s.schedule = sqlstore.GetSchedule()
		for _, item := range s.schedule {
			s.DoSchedule(item.Type, item.Strategy)
		}
	} else {
		s.DoSchedule(typename, strategy)
	}

	return nil
}

func (s *Scheduler) DoSchedule(typename string, strategy string) error {
	filter := Factory(typename)
	if filter == nil {
		return errors.New("type don't exist")
	}

	return filter.Filte(strategy)
}

func (s *Scheduler) Active(ch chan *PB.AckCheck, itemKeys []string, items map[string]*ini.File) error {
	for _, item := range itemKeys {
		value := items[item]
		for _, section := range value.Sections() {
			if section.Name() == "main" {
				continue
			}
			if section.Name() == "DEFAULT" {
				continue
			}
			if section.Name() == "tip" {
				for _, key := range section.Keys() {
					description := fmt.Sprintf("%s", key.Name())
					if key.Value() == "error" {
						sendChanToAdm(ch, item, utils.REQUEST, description)
					} else {
						sendChanToAdm(ch, item, utils.WARNING, description)
					}
				}
				continue
			}
			if section.Name() == "schedule" {
				for _, key := range section.Keys() {
					s.Schedule(key.Name(), key.Value(), false)
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
					if statusStr != "ERROR" {
						statusStr = respPutIns.Status
					}
					message = append(message, respPutIns.Value)
				}
			}

			message = utils.RemoveDuplicateElement(message)
			status := strings.ToUpper(statusStr)
			if status == "OK" {
				sendChanToAdm(ch, item, utils.SUCCESS, strings.Join(message, ","))
			} else if status == "WARNING" {
				sendChanToAdm(ch, item, utils.REQUEST, strings.Join(message, ","))
			} else {
				sendChanToAdm(ch, item, utils.FAILD, strings.Join(message, ","))
			}
		}
	}

	return nil
}

func GetScheduler() *Scheduler {
	if instance == nil {
		instance = new(Scheduler)
		instance.Init()
	}

	return instance
}
