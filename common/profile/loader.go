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
	"path"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/go-ini/ini"
	
	CONF "gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/sqlstore"
)

func filter(vs []string) []string {
	regex := regexp.MustCompile("^[a-zA-Z0-9_.-]+$")
	vsf := make([]string, 0)

	for _, v := range vs {
		if regex.MatchString(v) {
			vsf = append(vsf, v)
		}
	}

	return vsf
}

/*
Load profile_names slice, and it's include profiles, the profiles slice returned must be in order.
The profile inherit from it's include profile, make sure the include profile behind the main profile,
and not override by the include profile.
*/
func loadProfile(profileNames []string, profiles []Profile,
	processedProfiles []string, included bool) ([]Profile, []string) {
	for _, name := range profileNames {
		name = strings.Trim(name, " ")

		processedProfiles = append(processedProfiles, name)

		config, err := loadConfigData(name)
		if err != nil {
			fmt.Println("Failed to loadConfigData")
			continue
		}
		profile := Create(name, name, config)

		profiles = append(profiles, profile)
		if profile.options != nil {
			if profile.options.HasKey("include") {
				include, _ := profile.options.GetKey("include")
				names := make([]string, 0)
				names = append(names, strings.Split(include.Value(), ",")...)
				profiles, processedProfiles = loadProfile(names, profiles, processedProfiles, true)
			}
		}
		profile.included = included
	}

	return profiles, processedProfiles
}

func isInclude(section string, profile Profile) (int, bool) {
	var index = 0
	for index, unit := range profile.units {
		if unit.Name() == section {
			return index, true
		}
	}

	return index, false
}

func merge(profiles []Profile) Profile {
	final := profiles[0]

	// Ingnore included profile name
	if final.included {
		final.name = ""
		final.path = ""
	}

	for i, profile := range profiles {
		if i == 0 { // Ignore first element: final
			continue
		}

		// Process Options
		if profile.options != nil {
			for _, key := range profile.options.Keys() {
				if key.Name() == "include" {
					continue
				}

				if final.options == nil {
					final.options, _ = final.config.NewSection("main")
				}
				_, _ = final.options.NewKey(key.Name(), key.Value())

				section, _ := final.config.GetSection("main")
				_, _ = section.NewKey(key.Name(), key.Value())
			}
		}

		// Process Units
		for _, unit := range profile.units {
			index, include := isInclude(unit.Name(), final)
			if !include {
				final.units = append(final.units, unit)

				section, _ := final.config.NewSection(unit.Name())
				for _, key := range unit.Keys() {
					_, _ = section.NewKey(key.Name(), key.Value())
				}
			} else {
				section, _ := final.config.GetSection(unit.Name())
				for _, key := range unit.Keys() {
					if final.units[index].HasKey(key.Name()) {
						continue
					} else {
						_, _ = final.units[index].NewKey(key.Name(), key.Value())
						_, _ = section.NewKey(key.Name(), key.Value())
					}
				}
			}
		}

		// Process inputs parameter
		if profile.inputs != nil {
			for _, key := range profile.inputs.Keys() {
				if final.inputs == nil {
					final.inputs, _ = final.config.NewSection("inputs")
				}
				_, _ = final.inputs.NewKey(key.Name(), key.Value())

				section, _ := final.config.GetSection("inputs")
				_, _ = section.NewKey(key.Name(), key.Value())
			}
		}
		//
		if !profile.included {
			final.name = final.name + " " + profile.name
			final.path = final.path + "," + profile.path
		}
	}

	return final
}

// LoadFromWorkloadType method load the profile content depned the workload type
func LoadFromWorkloadType(workloadType string) (Profile, bool) {
	classProfile := &sqlstore.GetClass{Class: workloadType}
	err := sqlstore.GetClasses(classProfile)
	if err != nil {
		log.Errorf("inquery class_profile table failed")
		return Profile{}, false
	}
	if len(classProfile.Result) == 0 {
		log.Errorf("%s is not exist in the class_profile table", workloadType)
		return Profile{}, false
	}

	profileType := classProfile.Result[0].ProfileType
	profileNames := strings.Split(profileType, ",")

	pro, errMsg := Load(profileNames)
	return pro, errMsg == ""
}

// LoadFromProfile method load the profile content depend the profile name
func LoadFromProfile(profiles string) (Profile, bool) {
	profileNames := strings.Split(profiles, ",")
	pro, errMsg := Load(profileNames)
	return pro, errMsg == ""
}

// Load method load the profile content depned the profile names list
func Load(profileNames []string) (Profile, string) {
	profileNames = filter(profileNames)
	if len(profileNames) == 0 {
		fmt.Println("No profile or invaild profiles were specified.")
		return Profile{}, "no valid profile specified"
	}

	profiles := make([]Profile, 0)
	processedProfiles := make([]string, 0)
	profiles, _ = loadProfile(profileNames, profiles, processedProfiles, false)

	if len(profiles) == 0 {
		return Profile{}, "profile not found"
	}
	finalProfile := merge(profiles)

	defaultConfigFile := path.Join(CONF.DefaultConfPath, "atuned.cnf")
	cfg, _ := ini.Load(defaultConfigFile)
	finalProfile.inputs = cfg.Section("system")

	finalProfile.name = strings.Join(profileNames, ",")
	return finalProfile, ""
}

func loadConfigData(name string) (*ini.File, error) {
	var config *ini.File

	err := filepath.Walk(CONF.DefaultProfilePath, func(absPath string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			absFilename := absPath[len(CONF.DefaultProfilePath)+1:]
			filenameOnly := strings.TrimSuffix(strings.ReplaceAll(absFilename, "/", "-"),
				path.Ext(info.Name()))
			if filenameOnly == name {
				var err error
				config, err = ini.Load(absPath)
				if err != nil {
					return err
				}
				return nil
			}
		}
		return nil
	})

	if err != nil {
		return nil, err
	}
	if config == nil {
		return nil, fmt.Errorf("%s profile is not found!", name)
	}
	for _, section := range config.Sections() {
		if section.Name() == "script" {
			if section.HasKey("shell") {
				key, _ := section.GetKey("shell")
				scriptPath := strings.Trim(key.Value(), " ")
				config.Section(section.Name()).Key("shell").SetValue(scriptPath)
			}
		}
	}

	return config, nil
}
