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
	"regexp"
	"strconv"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/models"
	"gitee.com/openeuler/A-Tune/common/registry"
	"gitee.com/openeuler/A-Tune/common/utils"
)

func init() {
	registry.RegisterCheckerService("mem_topo", &MemTopo{
		Path:           path.Join(config.DefaultCheckerPath, "mem_topo.xml"),
		DisableChecker: true,
	})
}

// MemTopo represent the memory topology type
type MemTopo struct {
	Path           string
	DisableChecker bool
}

// Init Mem
func (m *MemTopo) Init() error {
	exist, err := utils.PathExist(m.Path)
	if err != nil {
		return err
	}
	if exist {
		return nil
	}
	if _, err := models.MonitorGet("mem", "topo", "xml", m.Path, ""); err != nil {
		return err
	}

	return nil
}

// IsCheckDisabled method disable check method when run check command
func (m *MemTopo) IsCheckDisabled() bool {
	return m.DisableChecker
}

type children struct {
	ID          string `xml:"id"`
	Class       string `xml:"class"`
	Claimed     bool   `xml:"claimed"`
	Handle      string `xml:"handle"`
	Description string `xml:"description"`
	Product     string `xml:"product"`
	Vendor      string `xml:"vendor"`
	Physid      string `xml:"physid"`
	Serial      string `xml:"serial"`
	Slot        string `xml:"slot"`
	Units       string `xml:"units"`
	Size        int64  `xml:"size"`
	Width       int    `xml:"width"`
	Clock       int64  `xml:"clock"`
}

type memorysInfo struct {
	ID        string     `xml:"id"`
	Physid    string     `xml:"physid"`
	Childrens []children `xml:"children"`
}

type topology struct {
	XMLName xml.Name      `xml:"topology"`
	Memorys []memorysInfo `xml:"memorys"`
}

/*
Check method check the memory topolog, whether the memory interpolation is balanced.
*/
func (m *MemTopo) Check(ch chan *PB.AckCheck) error {
	file, err := os.Open(m.Path)
	if err != nil {
		return err
	}

	defer file.Close()

	data, err := ioutil.ReadAll(file)
	if err != nil {
		return err
	}

	topo := topology{}
	err = xml.Unmarshal(data, &topo)
	if err != nil {
		return err
	}

	reg := regexp.MustCompile(`DIMM.*?(\d)(\d)(\d)\s.*`)
	memNum := 0

	maxSocket := 0
	maxChannel := 0
	maxSlot := 0

	for _, memory := range topo.Memorys {
		for _, child := range memory.Childrens {
			if params := reg.FindStringSubmatch(child.Slot); params != nil {
				socket, _ := strconv.Atoi(params[1])
				channel, _ := strconv.Atoi(params[2])
				slot, _ := strconv.Atoi(params[3])
				if socket > maxSocket {
					maxSocket = socket
				}
				if channel > maxChannel {
					maxChannel = channel
				}
				if slot > maxSlot {
					maxSlot = slot
				}
			}
		}
	}

	memTotal := (maxSocket + 1) * (maxChannel + 1) * (maxSlot + 1)
	memLocation := make([]bool, memTotal)

	for _, memory := range topo.Memorys {
		for _, child := range memory.Childrens {
			if child.Size != 0 {
				if params := reg.FindStringSubmatch(child.Slot); params != nil {
					socket, _ := strconv.Atoi(params[1])
					channel, _ := strconv.Atoi(params[2])
					slot, _ := strconv.Atoi(params[3])
					index := socket*(maxChannel+1)*(maxSlot+1) + channel*(maxSlot+1) + slot
					memLocation[index] = true
				}

				memNum++
			}
		}
	}

	log.Infof("memory total num is : %d", memNum)

	if memNum == memTotal {
		sendChanToAdm(ch, "memory", utils.SUCCESS, fmt.Sprintf("memory num is %d, the memory slot is full", memNum))
		return nil
	}

	if memNum%(maxChannel+1) != 0 {
		sendChanToAdm(ch, "memory", utils.SUGGEST, fmt.Sprintf("memory num is %d, not recommend, recommand 8,16 or 32", memNum))
		return nil
	}

	memHalf := memTotal / 2

	for i := 0; i < memHalf; i++ {
		if memLocation[i] != memLocation[i+memHalf] {
			sendChanToAdm(ch, "memory", utils.SUGGEST,
				"memory location is not balanced, recommand to balance memory location")
			return nil
		}
	}
	sendChanToAdm(ch, "memory", utils.SUCCESS, fmt.Sprintf("memory num is %d, memory interpolation is correct", memNum))
	return nil
}

func sendChanToAdm(ch chan *PB.AckCheck, item string, status string, description string) {
	if ch == nil {
		return
	}

	ch <- &PB.AckCheck{Name: item, Status: status, Description: description}
}
