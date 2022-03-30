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
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path"
	"regexp"
	"sort"
	"strings"
	"time"

	"github.com/go-ini/ini"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/http"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/models"
	"gitee.com/openeuler/A-Tune/common/registry"
	"gitee.com/openeuler/A-Tune/common/schedule"
	"gitee.com/openeuler/A-Tune/common/sqlstore"
	"gitee.com/openeuler/A-Tune/common/utils"
)

// Profile :profile implement setting profile
type Profile struct {
	included bool

	name string
	path string
	collId int

	options *ini.Section
	units   []*ini.Section

	config *ini.File

	inputs *ini.Section

	items map[string]*ini.File
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

// Put method set the key to value, both specified by ConfigPutBody
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

// Post method get the current value of the spefied key by ConfigPutBody
func (c *ConfigPutBody) Post() (*RespPut, error) {
	url := config.GetURL(config.ConfiguratorURI)
	res, err := http.Post(url, c)
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

// Backup method backup the workload type of the Profile
func (p *Profile) Backup() error {
	// NOTE: we only clone p and p.units exist.
	if (p == nil) || (p.units == nil) {
		return nil
	}

	timeUnix := time.Now().Format("2006_01_02_15_04_05")
	backedPath := path.Join(config.DefaultBackupPath, p.name+"_"+timeUnix)
	err := os.MkdirAll(backedPath, 0750)
	if err != nil {
		log.Error("failed to create backup path")
		return nil
	}

	buf := bytes.NewBuffer(nil)

	for _, unit := range p.units {
		// Ignore the sections ["main", "DEFAULT", "bios"]
		if name := unit.Name(); (name == "main") ||
			(name == "DEFAULT") ||
			(name == "bios" || name == "tip" || name == "check") {
			continue
		}

		_, _ = buf.WriteString("[" + unit.Name() + "]" + "\n")

		for _, key := range unit.Keys() {
			keyName := key.Name()
			keyName, err := p.replaceParameter(keyName)
			if err != nil {
				return err
			}
			keyValue, err := p.replaceParameter(key.Value())
			if err != nil {
				return err
			}

			cfg := keyName + "=" + keyValue
			body := &models.Profile{
				Section: unit.Name(),
				Config:  cfg,
				Path:    backedPath,
			}

			respIns, err := body.Backup()
			if err != nil {
				log.Errorf(err.Error())
				continue
			}
			if respIns.Status == utils.FAILD {
				log.Errorf("backup failed: %s", respIns.Value)
				continue
			}
			_, _ = buf.WriteString(keyName + "=" + respIns.Value + "\n")
		}
	}

	profileItems := &sqlstore.ProfileLog{
		ProfileID:  p.name,
		Context:    buf.String(),
		Timestamp:  time.Now(),
		BackupPath: backedPath,
	}

	if err := sqlstore.InsertProfileLog(profileItems); err != nil {
		return err
	}

	return nil
}

// RollbackActive method rollback the history profile, then backup and active the current profile
func (p *Profile) RollbackActive(ch chan *PB.AckCheck) error {
	if err := Rollback(); err != nil {
		return err
	}

	if err := p.Backup(); err != nil {
		return err
	}

	return p.active(ch)
}

func (p *Profile) active(ch chan *PB.AckCheck) error {
	if p.config == nil {
		return nil
	}

	if err := p.ItemSort(); err != nil {
		return err
	}

	//when active profile, make sure the output in the same order
	var itemKeys []string
	for item := range p.items {
		itemKeys = append(itemKeys, item)
	}
	sort.Strings(itemKeys)

	for _, item := range itemKeys {
		value := p.items[item]
		for _, section := range value.Sections() {
			if section.Name() == "main" {
				continue
			}
			if section.Name() == "DEFAULT" {
				continue
			}

			for _, key := range section.Keys() {
				scriptKey := key.Name()
				scriptKey, err := p.replaceParameter(scriptKey)
				if err != nil {
					return err
				}
				value, err := p.replaceParameter(key.Value())
				if err != nil {
					return err
				}
				if section.Name() == "script" {
					scriptKey = strings.Trim(scriptKey, " ")
				}

				if section.HasKey(scriptKey) {
					key.SetValue(value)
					continue
				}
				_, _ = section.NewKey(scriptKey, value)
				section.DeleteKey(key.Name())
			}
		}
	}

	scheduler := schedule.GetScheduler()
	scheduler.SetScheduleId(p.collId)
	_ = scheduler.Active(ch, itemKeys, p.items)

	return nil
}

// SetWorkloadType method set the workload type name to Profile
func (p *Profile) SetWorkloadType(name string) {
	p.name = name
}

// SetCollectionId method set the collId 'int id' to Profile
func (p *Profile) SetCollectionId(id int) {
	p.collId = id
}

//ItemSort method allocate property to different item
func (p *Profile) ItemSort() error {
	if p.config == nil {
		return nil
	}
	p.items = make(map[string]*ini.File)
	var itemName string
	for _, section := range p.config.Sections() {
		for _, key := range section.Keys() {
			if section.Name() == "main" {
				continue
			}
			if section.Name() == "DEFAULT" {
				continue
			}
			if section.Name() == "inputs" {
				continue
			}
			if section.Name() == "tip" {
				itemName = key.Value()
			} else {
				itemQuery, err := sqlstore.GetPropertyItem(key.Name())
				if err != nil {
					log.Errorf("key %s is not exist in tuned_item", key.Name())
					itemName = "OTHERS"
				} else {
					itemName = itemQuery
				}
			}

			if _, ok := p.items[itemName]; !ok {
				p.items[itemName] = ini.Empty()
			}
			if itemSection := p.items[itemName].Section(section.Name()); itemSection == nil {
				_, _ = p.items[itemName].NewSection(section.Name())
			}
			itemSection, _ := p.items[itemName].GetSection(section.Name())
			_, _ = itemSection.NewKey(key.Name(), key.Value())
		}
	}
	return nil
}

// Check method check wether the actived profile is effective
func (p *Profile) Check(ch chan *PB.AckCheck) error {
	if p.config == nil {
		return nil
	}

	for _, section := range p.config.Sections() {
		if section.Name() == "main" {
			continue
		}
		if section.Name() == "DEFAULT" {
			continue
		}
		if section.Name() == "tip" {
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
				log.Infof("initializing checker service in profile check: %s", service.Name)
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

		var statusStr string
		for _, key := range section.Keys() {
			scriptKey := key.Name()
			scriptKey, err := p.replaceParameter(scriptKey)
			if err != nil {
				return err
			}

			value, err := p.replaceParameter(key.Value())
			if err != nil {
				return err
			}

			if section.Name() == "script" {
				scriptKey = strings.Trim(key.Name(), " ")
			}

			body := &ConfigPutBody{
				Section: section.Name(),
				Key:     scriptKey,
				Value:   value,
			}

			respPutIns, err := body.Post()
			if err != nil {
				sendChanToAdm(ch, key.Name(), utils.FAILD, err.Error())
				continue
			}

			statusStr = respPutIns.Status

			statusStr = strings.ToUpper(statusStr)
			if statusStr == "OK" {
				description := fmt.Sprintf("value: %s", value)
				sendChanToAdm(ch, key.Name(), utils.SUCCESS, description)
			} else if statusStr == utils.UNKNOWN {
				description := fmt.Sprintf("expect value: %s, real value: %s", value, statusStr)
				sendChanToAdm(ch, key.Name(), utils.WARNING, description)
			} else {
				description := fmt.Sprintf("expect value: %s, real value: %s", value, statusStr)
				sendChanToAdm(ch, key.Name(), utils.FAILD, description)
			}
		}
	}

	return nil
}

// ActiveTuned method set the profile that dynamic tuned matched
func (p *Profile) ActiveTuned(ch chan *PB.AckCheck, params string) error {
	if p.config == nil {
		return nil
	}

	tuned := make(map[string]string)
	paramTuned := strings.Split(params, ",")
	for _, param := range paramTuned {
		value := strings.Split(param, "=")
		if len(value) != 2 {
			continue
		}
		tuned[value[0]] = value[1]
	}

	for _, section := range p.config.Sections() {
		if section.Name() == "main" {
			continue
		}
		if section.Name() == "DEFAULT" {
			continue
		}
		if section.Name() == "tip" {
			continue
		}

		var statusStr string
		for _, key := range section.Keys() {
			scriptKey := key.Name()
			if section.Name() == "script" {
				scriptKey = strings.Trim(key.Name(), " ")
			}
			if _, exist := tuned[key.Name()]; !exist {
				continue
			}

			body := &ConfigPutBody{
				Section: section.Name(),
				Key:     scriptKey,
				Value:   tuned[key.Name()],
			}

			respPutIns, err := body.Put()
			if err != nil {
				sendChanToAdm(ch, key.Name(), utils.FAILD, err.Error())
				continue
			}

			log.Infof("active parameter, key: %s, value: %s, status:%s", scriptKey, key.Value(), respPutIns.Status)
			statusStr = respPutIns.Status

			statusStr = strings.ToUpper(statusStr)
			if statusStr == "OK" {
				description := fmt.Sprintf("value: %s", key.Value())
				sendChanToAdm(ch, key.Name(), utils.SUCCESS, description)
			} else if statusStr == utils.WARNING {
				description := fmt.Sprintf("expext value: %s, real value: %s", key.Value(), statusStr)
				sendChanToAdm(ch, key.Name(), utils.SUGGEST, description)
			} else {
				description := fmt.Sprintf("expext value: %s, real value: %s", key.Value(), statusStr)
				sendChanToAdm(ch, key.Name(), utils.FAILD, description)
			}
		}
	}

	return nil
}

func sendChanToAdm(ch chan *PB.AckCheck, item string, status string, description string) {
	if ch == nil {
		return
	}

	ch <- &PB.AckCheck{Name: item, Status: status, Description: description}
}

func (p *Profile) replaceParameter(str string) (string, error) {
	re := regexp.MustCompile(`\{([^}]+)\}`)
	matches := re.FindAllStringSubmatch(str, -1)
	if len(matches) > 0 {
		if p.inputs == nil {
			return str, fmt.Errorf("input section is not exist")
		}
		for _, match := range matches {
			if len(match) < 2 {
				continue
			}
			if !p.inputs.Haskey(match[1]) {
				return str, fmt.Errorf("%s is not exist int the inputs section", match[1])
			}
			value := p.inputs.Key(match[1]).Value()
			str = re.ReplaceAllString(str, value)
		}
	}
	return str, nil
}
