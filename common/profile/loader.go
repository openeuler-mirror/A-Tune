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
	CONF "atune/common/config"
	"atune/common/log"
	"atune/common/sqlstore"
	"fmt"
	"path"
	"regexp"
	"strings"

	"github.com/go-ini/ini"
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
func loadProfile(profileNames []string, profiles []Profile, processedProfiles []string, included bool) ([]Profile, []string) {
	for _, name := range profileNames {
		name = strings.Trim(name, " ")

		processedProfiles = append(processedProfiles, name)

		config, err := loadConfigData(name)
		if err != nil {
			fmt.Println("Failure to load_config_data")
			continue
		}
		profile := Create(name, name, config)

		profiles = append(profiles, profile)
		if profile.options != nil {
			if profile.options.HasKey("include") {
				include, _ := profile.options.GetKey("include")
				names := make([]string, 0)
				names = append(names, strings.Trim(include.Value(), ""))
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
				final.options.NewKey(key.Name(), key.Value())

				section, _ := final.config.GetSection("main")
				section.NewKey(key.Name(), key.Value())
			}
		}

		// Process Units
		for _, unit := range profile.units {
			index, include := isInclude(unit.Name(), final)
			if !include {
				final.units = append(final.units, unit)

				section, _ := final.config.NewSection(unit.Name())
				for _, key := range unit.Keys() {
					section.NewKey(key.Name(), key.Value())
				}
			} else {
				section, _ := final.config.GetSection(unit.Name())
				for _, key := range unit.Keys() {
					if final.units[index].HasKey(key.Name()) {
						/*FIXME: Ignore the same key*/
						continue
					} else {
						final.units[index].NewKey(key.Name(), key.Value())
						section.NewKey(key.Name(), key.Value())
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
				final.inputs.NewKey(key.Name(), key.Value())

				section, _ := final.config.GetSection("inputs")
				section.NewKey(key.Name(), key.Value())
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
		log.Errorf("inquery class_profile table faild")
		return Profile{}, false
	}
	if len(classProfile.Result) == 0 {
		log.Errorf("%s is not exist in the class_profile table", workloadType)
		return Profile{}, false
	}

	profileType := classProfile.Result[0].ProfileType
	profileNames := strings.Split(profileType, ",")

	pro, exist := Load(profileNames)
	pro.name = workloadType
	return pro, exist
}

// Load method load the profile content depned the profile names list
func Load(profileNames []string) (Profile, bool) {
	profileNames = filter(profileNames)
	if len(profileNames) == 0 {
		fmt.Println("No profile or invaild profiles were specified.")
		return Profile{}, false
	}

	profiles := make([]Profile, 0)
	processedProfiles := make([]string, 0)
	profiles, processedProfiles = loadProfile(profileNames, profiles, processedProfiles, false)

	if len(profiles) == 0 {
		return Profile{}, false
	}
	finalProfile := merge(profiles)

	defaultConfigFile := path.Join(CONF.DefaultConfPath, "atuned.cnf")
	cfg, _ := ini.Load(defaultConfigFile)
	finalProfile.inputs = cfg.Section("system")

	return finalProfile, true
}

func loadConfigData(name string) (*ini.File, error) {
	context, err := sqlstore.GetContext(name)
	if err != nil {
		fmt.Println("Canot find profile ", name)
		return nil, err
	}

	config, err := ini.Load([]byte(context))
	if err != nil {
		fmt.Println("Failure to load context", name)
		return nil, err
	}

	// Filter {i:PROFILE_DIR}
	//dir_name := path.Dir(filename)
	dirName := CONF.DefaultScriptPath
	regex := regexp.MustCompile("\\${i:PROFILE_DIR}")
	for _, section := range config.Sections() {
		for _, key := range section.Keys() {
			config.Section(section.Name()).Key(key.Name()).SetValue(regex.ReplaceAllString(key.Value(), dirName))
		}
	}

	// Filter script=
	for _, section := range config.Sections() {
		if section.Name() == "script" {
			if section.HasKey("shell") {
				key, _ := section.GetKey("shell")
				scriptPath := path.Join(dirName, strings.Trim(key.Value(), " "))
				config.Section(section.Name()).Key("shell").SetValue(scriptPath)
			}
		}
	}

	return config, nil
}
