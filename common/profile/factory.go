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
	"github.com/go-ini/ini"
)

// Create method create the Profile structer
// name is the workloadType name
// path is the profile path which can be removed in the future
func Create(name string, path string, config *ini.File) Profile {
	profile := Profile{
		name:   name,
		path:   path,
		config: config,
	}

	if config == nil {
		return profile
	}

	for _, section := range config.Sections() {
		if section.Name() == "DEFAULT" {
			continue
		}

		if section.Name() == "main" {
			profile.options = section
		} else {
			profile.units = append(profile.units, section)
		}
	}

	return profile
}
