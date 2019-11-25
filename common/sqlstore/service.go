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

package sqlstore

import (
	"atune/common/log"
	"errors"
	"strings"
)

// GetClasses method return item of table class_profile
func GetClasses(query *GetClass) error {
	query.Result = make([]*ClassProfile, 0)
	session := globalEngine.Table("class_profile")

	if query.Class != "" {
		session.Where("class=?", query.Class)
	}

	if query.Active {
		session.Where("active=?", query.Active)
	}

	if err := session.Find(&query.Result); err != nil {
		return err
	}

	return nil
}

// InsertClassProfile method insert item to class_profile table
func InsertClassProfile(value *ClassProfile) error {
	session := globalEngine.Table("class_profile")
	if _, err := session.Insert(value); err != nil {
		return err
	}
	return nil
}

// UpdateClassProfile method update the class_profile table
func UpdateClassProfile(value *ClassProfile) error {
	session := globalEngine.Table("class_profile")
	if _, err := session.Where("class = ?", value.Class).Update(value); err != nil {
		return err
	}
	return nil
}

// DeleteClassProfile method delete item from class_profile table by workloadType
func DeleteClassProfile(workloadType string) error {
	session := globalEngine.Table("class_profile")
	if _, err := session.Exec("delete from class_profile where class = ?", workloadType); err != nil {
		return err
	}
	return nil
}

// GetClassApps method return the item of table class_apps
func GetClassApps(query *GetClassApp) error {
	query.Result = make([]*ClassApps, 0)
	session := globalEngine.Table("class_apps")

	if query.Class != "" {
		session.Where("class=?", query.Class)
	}

	if err := session.Find(&query.Result); err != nil {
		return err
	}
	return nil
}

// InsertClassApps method insert item to class_apps table
func InsertClassApps(value *ClassApps) error {
	session := globalEngine.Table("class_apps")
	if _, err := session.Insert(value); err != nil {
		return err
	}
	return nil
}

// DeleteClassApps method delete item from class_apps table by workload type
func DeleteClassApps(workloadType string) error {
	session := globalEngine.Table("class_apps")
	if _, err := session.Exec("delete from class_apps where class = ?", workloadType); err != nil {
		return err
	}
	return nil
}

// ExistWorkloadType method return true if workloadType exist otherwise return false
func ExistWorkloadType(workloadType string) (bool, error) {
	session := globalEngine.Table("class_apps")
	exist, err := session.Where("class=?", workloadType).Exist()

	if err != nil {
		return false, err
	}
	return exist, nil
}

// GetContext method return the optimization item of workload type name
func GetContext(name string) (string, error) {
	query := make([]*Profile, 0)

	session := globalEngine.Table("profile")
	if err := session.Where("profile_type=?", name).Find(&query); err != nil {
		return "", err
	}

	if len(query) != 1 {
		return "", errors.New("name not exist")
	}

	context := query[0].ProfileInformation
	return context, nil
}

// InsertProfile method insert self define profile to table profile
func InsertProfile(value *Profile) error {
	session := globalEngine.Table("profile")
	session.Insert(value)
	return nil
}

// UpdateProfile method update the profile table
func UpdateProfile(value *Profile) error {
	session := globalEngine.Table("profile")
	if _, err := session.Where("profile_type = ?", value.ProfileType).Update(value); err != nil {
		return err
	}
	return nil
}

// DeleteProfile method delete the item from profile table
func DeleteProfile(profileType string) error {
	session := globalEngine.Table("profile")
	if _, err := session.Exec("delete from profile where profile_type = ?", profileType); err != nil {
		return err
	}
	return nil

}

// ExistProfile method return true if profileType exist otherwise return false
func ExistProfile(profileType string) (bool, error) {
	session := globalEngine.Table("profile")
	exist, err := session.Where("profile_type=?", profileType).Exist()

	if err != nil {
		return false, err
	}
	return exist, nil
}

// ActiveProfile method set the workload type state to active
func ActiveProfile(name string) error {
	session := globalEngine.Table("class_profile")

	name = strings.Trim(name, " ")

	profile := new(ClassProfile)
	session.Where("active=?", true).Get(profile)

	if profile.Class == name {
		return nil
	}

	session.Exec("update class_profile set active=? where class = ?", !profile.Active, profile.Class)

	newProfile := new(ClassProfile)
	has, err := session.Where("class=?", name).Get(newProfile)
	if err != nil {
		return err
	} else if !has {
		return errors.New("Profile does not exist")
	}

	session.Exec("update class_profile set active=? where class = ?", !newProfile.Active, newProfile.Class)

	return nil
}

// GetPropertyItem method return the classification of the specified property
func GetPropertyItem(property string) (string, error) {
	tunedItem := new(TunedItem)
	session := globalEngine.Table("tuned_item")
	has, err := session.Where("property=?", property).Get(tunedItem)
	if err != nil {
		return "", err
	}

	if !has {
		return "", errors.New("property is not exist")
	}

	item := tunedItem.Item

	return item, nil
}

// GetProfileIDByName method return the profile history ID.
// the parameter name is workload type
func GetProfileIDByName(name string) (int64, error) {
	query := make([]*Profile, 0)

	session := globalEngine.Table("profile")
	if err := session.Where("name=?", name).Find(&query); err != nil {
		return -1, err
	}

	if len(query) != 1 {
		return -1, errors.New("profile name not exist")
	}

	//id := query[0].Id
	id := int64(0)
	return id, nil
}

// GetTuneds method return the dynamic tuned items which used for bayes search
func GetTuneds(query *GetTuned) error {
	query.Result = make([]*Tuned, 0)
	session := globalEngine.Table("tuned")

	if query.Class != "" {
		session.Where("class=?", query.Class)
	}

	if err := session.Find(&query.Result); err != nil {
		return err
	}

	return nil
}

// GetRuleTuneds method return the rules inquery from rule_tuned table
func GetRuleTuneds(query *GetRuleTuned) error {
	query.Result = make([]*RuleTuned, 0)
	session := globalEngine.Table("rule_tuned")

	if query.Class != "" {
		session.Where("class=?", query.Class)
	}

	if err := session.Find(&query.Result); err != nil {
		return err
	}
	return nil
}

// GetCollections method return the collection metrics
func GetCollections() ([]*Collection, error) {
	collections := make([]*Collection, 0)

	session := globalEngine.Table("collection")
	if err := session.Find(&collections); err != nil {
		return nil, err
	}

	return collections, nil
}

// InsertProfileLog method insert profile history to database
func InsertProfileLog(value *ProfileLog) error {
	session := globalEngine.Table("profile_log")
	session.Insert(value)
	return nil
}

// GetProfileLogs method return profile histories
func GetProfileLogs() ([]*ProfileLog, error) {
	profileLogs := make([]*ProfileLog, 0)

	session := globalEngine.Table("profile_log")
	if err := session.Find(&profileLogs); err != nil {
		return nil, err
	}
	return profileLogs, nil
}

// DelProfileLogByID method delete the profile history by ID
func DelProfileLogByID(id int64) error {
	session := globalEngine.Table("profile_log")
	if _, err := session.Exec("delete from profile_log where id = ?", id); err != nil {
		return err
	}
	return nil
}

// GetProfileLogByID method get the profile history by id
func GetProfileLogByID(query *GetProfileLog) error {
	query.Result = make([]*ProfileLog, 0)
	session := globalEngine.Table("profile_log")
	if err := session.Where("id = ?", query.ID).Find(&query.Result); err != nil {
		return err
	}
	return nil
}

// GetProfileMaxID method get the id profile history
func GetProfileMaxID() (*ProfileLog, error) {
	profileLog := new(ProfileLog)
	session := globalEngine.Table("profile_log")
	has, err := session.Desc("id").Limit(1).Get(profileLog)
	if err != nil {
		return nil, err
	}
	if !has {
		return nil, nil
	}
	return profileLog, nil
}

// InActiveProfile method set the active field to false
func InActiveProfile() error {
	session := globalEngine.Table("profile_log")

	if _, err := session.Exec("update class_profile set active=? where active = ?", false, true); err != nil {
		return err
	}
	return nil
}

func UpdateSchedule(typename string, strategy string) error {
	session := globalEngine.Table("schedule")

	item := new(Schedule)
	has, err := session.Where("type=?", typename).Get(item)
	if err != nil {
		log.Info("Schedule have not the type = ?", typename)
		return err
	} else if !has {
		_, err = session.Exec("insert into schedule (type, strategy) values (?, ?)", typename, strategy)
		if err != nil {
			log.Info("Insert Schedule values (?, ?)", typename, strategy)
			return err
		}
	} else {
		_, err = session.Exec("update schedule set type=?,strategy=? where type=?", typename, strategy, typename)
		log.Info(err)
	}

	return nil
}

func GetSchedule() []*Schedule {
	session := globalEngine.Table("schedule")

	items := make([]*Schedule, 0)
	if err := session.Find(&items); err != nil {
		return nil
	}

	return items
}
