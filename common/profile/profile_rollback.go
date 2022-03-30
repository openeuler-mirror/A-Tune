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
	"fmt"
	"os"
	"sort"
	"strings"

	"github.com/go-ini/ini"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/models"
	"gitee.com/openeuler/A-Tune/common/sqlstore"
	"gitee.com/openeuler/A-Tune/common/utils"
)

// HistoryProfile :load profile history type
type HistoryProfile struct {
	config *ini.File
}

// Resume method set the system state to the time before setting ProfileLog.
func (p *HistoryProfile) Resume(ch chan *PB.AckCheck) error {
	for _, section := range p.config.Sections() {
		sectionKeys := section.KeyStrings()
		for index := len(sectionKeys) - 1; index >= 0; index-- {
			key := section.Key(sectionKeys[index])
			body := &models.Profile{
				Section: section.Name(),
				Config:  key.Value(),
			}

			respPutIns, err := body.Resume()
			if err != nil {
				description := fmt.Sprintf("key: %s, resume failed: %v", key.Name(), err.Error())
				log.Errorf(description)
				sendChanToAdm(ch, key.Name(), utils.FAILD, description)
				continue
			}

			statusStr := respPutIns.Status
			statusStr = strings.ToUpper(statusStr)
			if statusStr == "OK" {
				description := fmt.Sprintf("value: %s", key.Value())
				sendChanToAdm(ch, key.Name(), utils.SUCCESS, description)
			} else {
				description := fmt.Sprintf("failed: %s", statusStr)
				sendChanToAdm(ch, key.Name(), utils.FAILD, description)
			}
		}
	}

	return nil
}

// Load method load the context to config field
func (p *HistoryProfile) Load(context string) error {
	config, err := ini.Load([]byte(context))
	if err != nil {
		return err
	}
	p.config = config
	return nil
}

// Rollback methed reset profile to system init state
func Rollback() error {
	profileLogs, err := sqlstore.GetProfileLogs()
	if err != nil {
		log.Errorf("get profile history failed, %v", err)
		return err
	}

	if len(profileLogs) < 1 {
		return nil
	}

	sort.Slice(profileLogs, func(i, j int) bool {
		return profileLogs[i].ID > profileLogs[j].ID
	})

	for _, pro := range profileLogs {
		log.Infof("begin to restore profile id: %d", pro.ID)
		profileInfo := HistoryProfile{}
		if err := profileInfo.Load(pro.Context); err != nil {
			log.Error(err.Error())
		}
		if err := profileInfo.Resume(nil); err != nil {
			log.Error(err.Error())
		}

		// delete profile log after restored
		if err := sqlstore.DelProfileLogByID(pro.ID); err != nil {
			return err
		}
		//delete backup dir
		if err := os.RemoveAll(pro.BackupPath); err != nil {
			return err
		}
	}
	if err := sqlstore.InActiveProfile(); err != nil {
		return nil
	}

	return nil
}
