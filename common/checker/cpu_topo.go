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
	registry.RegisterCheckerService("cpu_topo", &CPUTopo{
		Path: path.Join(config.DefaultCheckerPath, "cpu_topo.xml"),
	})
}

// CPUTopo represent the memory topology type
type CPUTopo struct {
	Path string
}

// Init CPUTopo
func (m *CPUTopo) Init() error {
	exist, err := utils.PathExist(m.Path)
	if err != nil {
		return err
	}
	if exist {
		return nil
	}
	if _, err := models.MonitorGet("cpu", "topo", "xml", m.Path, ""); err != nil {
		return err
	}

	return nil
}

type info struct {
	Name  string `xml:"name,attr"`
	Value string `xml:"value,attr"`
}

type machine struct {
	Info []info `xml:"info"`
}

type cpuTopology struct {
	XMLName xml.Name `xml:"topology"`
	Machine machine  `xml:"object"`
}

/*
Check method check the memory topolog, whether the memory interpolation is balanced.
*/
func (m *CPUTopo) Check(ch chan *PB.AckCheck) error {
	file, err := os.Open(m.Path)
	if err != nil {
		return err
	}

	defer file.Close()

	data, err := ioutil.ReadAll(file)
	if err != nil {
		return err
	}

	topology := cpuTopology{}
	err = xml.Unmarshal(data, &topology)
	if err != nil {
		return err
	}

	sendChanToAdm(ch, "system information:", utils.SUCCESS, "")
	for _, info := range topology.Machine.Info {
		if info.Name == "OSRelease" {
			message := fmt.Sprintf("    %s: %s", info.Name, info.Value)
			sendChanToAdm(ch, message, utils.SUCCESS, "")
		}
		if info.Name == "DMIBIOSVersion" {
			message := fmt.Sprintf("    %s: %s", info.Name, info.Value)
			sendChanToAdm(ch, message, utils.SUCCESS, "")
		}
	}
	return nil
}
