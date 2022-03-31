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

package checker

import (
	"encoding/xml"
	"fmt"
	"io/ioutil"
	"os"
	"path"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/models"
	"gitee.com/openeuler/A-Tune/common/registry"
	"gitee.com/openeuler/A-Tune/common/utils"
)

func init() {
	registry.RegisterCheckerService("cpu_info", &CPUInfo{
		Path: path.Join(config.DefaultCheckerPath, "cpu_info.xml"),
	})
}

// CPUInfo represent the memory topology type
type CPUInfo struct {
	Path string
}

// Init CPUInfo
func (m *CPUInfo) Init() error {
	exist, err := utils.PathExist(m.Path)
	if err != nil {
		return err
	}
	if exist {
		return nil
	}
	if _, err := models.MonitorGet("cpu", "info", "xml", m.Path, ""); err != nil {
		return err
	}

	return nil
}

type setting struct {
	ID    string `xml:"id,attr"`
	Value string `xml:"value,attr"`
}

type configuration struct {
	Setting []setting `xml:"setting"`
}

type node struct {
	ID            string        `xml:"id,attr"`
	Claimed       string        `xml:"claimed,attr"`
	Disabled      string        `xml:"disabled,attr"`
	Version       string        `xml:"version"`
	Size          int64         `xml:"size"`
	Configuration configuration `xml:"configuration"`
}

type cpuProcessor struct {
	XMLName xml.Name `xml:"list"`
	Nodes   []node   `xml:"node"`
}

/*
Check method check the cpu information
*/
func (m *CPUInfo) Check(ch chan *PB.AckCheck) error {
	file, err := os.Open(m.Path)
	if err != nil {
		return err
	}

	defer file.Close()

	data, err := ioutil.ReadAll(file)
	if err != nil {
		return err
	}

	cpus := cpuProcessor{}
	err = xml.Unmarshal(data, &cpus)
	if err != nil {
		return err
	}

	sendChanToAdm(ch, "cpu information:", utils.SUCCESS, "")
	for _, node := range cpus.Nodes {
		if node.Disabled == "true" {
			continue
		}
		cores := "0"
		for _, set := range node.Configuration.Setting {
			if set.ID == "enabledcores" {
				cores = set.Value
			}
		}
		message := fmt.Sprintf("    %s   version: %s  speed: %d HZ   cores: %s", node.ID, node.Version, node.Size, cores)
		sendChanToAdm(ch, message, utils.SUCCESS, "")
	}

	return nil
}
