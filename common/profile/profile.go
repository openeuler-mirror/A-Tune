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

package profile

import (
	PB "atune/api/profile"
	"atune/common/config"
	"atune/common/http"
	"atune/common/log"
	"atune/common/models"
	"atune/common/schedule"
	"atune/common/sqlstore"
	"atune/common/utils"
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
)

// Profile :profile implement setting profile
type Profile struct {
	included bool

	name string
	path string

	options *ini.Section
	units   []*ini.Section

	config *ini.File

	inputs *ini.Section

	items  map[string]*ini.File
	backup bool
}

// ConfigPutBody :body send to CPI service
type ConfigPutBody struct {
	Section string `json:"section"`
	Key     string `json:"key"`
	Value   string `json:"value"`
}

// RespPut ; response of call CPI service
type RespPut struct {
	Status string `json:status`
	Value  string `json:value`
}

// Put method set the key to value, both specified by ConfigPutBody
func (c *ConfigPutBody) Put() (*RespPut, error) {
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
	respPutIns := new(RespPut)
	err = json.Unmarshal(resBody, respPutIns)
	if err != nil {
		return nil, err
	}

	return respPutIns, nil

}

// Get method get the current value of the spefied key by ConfigPutBody
func (c *ConfigPutBody) Get() (*RespPut, error) {
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
	os.MkdirAll(backedPath, os.ModePerm)

	buf := bytes.NewBuffer(nil)

	for _, unit := range p.units {
		// Ignore the sections ["main", "DEFAULT", "bios"]
		if name := unit.Name(); (name == "main") || (name == "DEFAULT") || (name == "bios" || name == "tip") {
			continue
		}

		buf.WriteString("[" + unit.Name() + "]" + "\n")

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
			config := keyName + "=" + keyValue
			body := &models.Profile{
				Section: unit.Name(),
				Config:  config,
				Path:    backedPath,
			}

			respPutIns, _ := body.Backup()
			if respPutIns == nil || (respPutIns.Status == "FAILED") {
				continue
			}
			buf.WriteString(keyName + "=" + respPutIns.Value + "\n")
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
					scriptKey = path.Join(config.DefaultScriptPath, strings.Trim(key.Name(), " "))
				}

				if section.HasKey(scriptKey) {
					key.SetValue(value)
					continue
				}
				section.NewKey(scriptKey, value)
				section.DeleteKey(key.Name())
			}
		}
	}

	scheduler := schedule.GetScheduler()
	scheduler.Active(ch, itemKeys, p.items)
	p.Save()

	return nil
}

// Save method set the workload type of Profile to active state
func (p *Profile) Save() error {
	return sqlstore.ActiveProfile(p.name)
}

// SetWorkloadType method set the workload type name to Profile
func (p *Profile) SetWorkloadType(name string) {
	p.name = name
}

//ItemSort method allocate property to diffrent item
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
				if key.Value() == "warning" {
					itemName = "SUGGEST"
				} else {
					itemName = "REQUEST"
				}
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
				p.items[itemName].NewSection(section.Name())
			}
			itemSection, _ := p.items[itemName].GetSection(section.Name())
			itemSection.NewKey(key.Name(), key.Value())
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

		var statusStr = "OK"
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
				scriptKey = path.Join(config.DefaultScriptPath, strings.Trim(key.Name(), " "))
			}

			body := &ConfigPutBody{
				Section: section.Name(),
				Key:     scriptKey,
				Value:   value,
			}

			respPutIns, err := body.Get()
			if err != nil {
				sendChanToAdm(ch, key.Name(), utils.FAILD, err.Error())
				continue
			}

			statusStr = respPutIns.Status

			statusStr = strings.ToUpper(statusStr)
			if statusStr == "OK" {
				description := fmt.Sprintf("value: %s", value)
				sendChanToAdm(ch, key.Name(), utils.SUCCESS, description)
			} else if statusStr == "UNKNOWN" {
				description := fmt.Sprintf("expext value: %s, real value: %s", value, statusStr)
				sendChanToAdm(ch, key.Name(), utils.WARNING, description)
			} else {
				description := fmt.Sprintf("expext value: %s, real value: %s", value, statusStr)
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

		var statusStr = "OK"
		for _, key := range section.Keys() {
			scriptKey := key.Name()
			if section.Name() == "script" {
				scriptKey = path.Join(config.DefaultScriptPath, strings.Trim(key.Name(), " "))
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
			} else if statusStr == "UNKNOWN" {
				description := fmt.Sprintf("expext value: %s, real value: %s", key.Value(), statusStr)
				sendChanToAdm(ch, key.Name(), utils.WARNING, description)
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
			if !p.inputs.Haskey(match[1]) {
				return str, fmt.Errorf("%s is not exist int the inputs section", match[1])
			}
			value := p.inputs.Key(match[1]).Value()
			str = re.ReplaceAllString(str, value)
		}
	}
	return str, nil
}
