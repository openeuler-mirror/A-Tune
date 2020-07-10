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

package sqlstore

import (
	"errors"
	"time"
)

var (
	// ErrServiceNotFound : error message
	ErrServiceNotFound = errors.New("service not fount")
)

// ClassApps : table class_apps
type ClassApps struct {
	Class         string `xorm:"class"`
	Apps          string `xorm:"apps"`
	ResourceLimit string `xorm:"resource_limit"`
	Deletable     bool   `xorm:"deletable"`
}

// ClassProfile : table class_profile
type ClassProfile struct {
	Class       string `xorm:"class"`
	ProfileType string `xorm:"profile_type"`
	Active      bool   `xorm:"active"`
}

// Tuned : table tuned
type Tuned struct {
	ID    int64  `xorm:"id"`
	Class string `xorm:"class"`
	Name  string `xorm:"name"`
	Type  string `xorm:"type"`
	Value string `xorm:"value"`
	Range string `xorm:"range"`
	Step  int64  `xorm:"step"`
}

// RuleTuned : table rule_tuned
type RuleTuned struct {
	ID             int64  `xorm:"id"`
	Name           string `xorm:"name"`
	Class          string `xorm:"class"`
	Expression     string `xorm:"expression"`
	Action         string `xorm:"action"`
	OppositeAction string `xorm:"opposite_action"`
	Monitor        string `xorm:"monitor"`
	Field          string `xorm:"field"`
}

// Collection : table collection
type Collection struct {
	ID      int64  `xorm:"id"`
	Name    string `xorm:"name"`
	Module  string `xorm:"module"`
	Purpose string `xorm:"purpose"`
	Metrics string `xorm:"metrics"`
}

// ProfileLog : table profile_log
type ProfileLog struct {
	ID         int64     `xorm:"id"`
	ProfileID  string    `xorm:"profile_id"`
	Context    string    `xorm:"context"`
	BackupPath string    `xorm:"backup_path"`
	Timestamp  time.Time `xorm:"timestamp"`
}

// Schedule : table schedule strategy
type Schedule struct {
	ID       int64  `xorm:"id"`
	Type     string `xorm:"type"`
	Strategy string `xorm:"strategy"`
}

// GetClass : inquery the class_profile table
type GetClass struct {
	Active bool
	Class  string
	Result []*ClassProfile
}

// GetClassApp : inquery the class_apps table
type GetClassApp struct {
	Class  string
	Result []*ClassApps
}

// TunedItem : table tuned_item
type TunedItem struct {
	ID       int64 `xorm:"id"`
	Property string
	Item     string
}

// GetTuned : inquery the tuned for bayes search
type GetTuned struct {
	ID     int64
	Class  string
	Result []*Tuned
}

// GetRuleTuned : for inquery rules for tuned
type GetRuleTuned struct {
	Class  string
	Result []*RuleTuned
}

// GetProfileLog : for inquery profile_log table
type GetProfileLog struct {
	ID     int64
	Result []*ProfileLog
}
