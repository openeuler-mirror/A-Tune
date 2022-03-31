/*
 * Copyright (c) 2020 Huawei Technologies Co., Ltd.
 * A-Tune is licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Create: 2020-05-25
 */

package profile

import (
	"fmt"
	"io/ioutil"
	"os"
	"path"
	"path/filepath"
	"strings"

	"github.com/go-ini/ini"
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/utils"
)

// ExistProfile method return true if profile exist otherwise return false
func ExistProfile(profileName string) (bool, error) {
	var exist bool
	err := filepath.Walk(config.DefaultProfilePath, func(absPath string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			absFilename := absPath[len(config.DefaultProfilePath)+1:]
			filenameOnly := strings.TrimSuffix(strings.ReplaceAll(absFilename, "/", "-"),
				path.Ext(info.Name()))
			if filenameOnly == profileName {
				exist = true
			}
		}
		return nil
	})

	if err != nil {
		return false, err
	}

	return exist, nil
}

// DeleteProfile method delete the profile from profile path
func DeleteProfile(profileName string) error {
	err := filepath.Walk(config.DefaultProfilePath, func(absPath string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			absFilename := absPath[len(config.DefaultProfilePath)+1:]
			filenameOnly := strings.TrimSuffix(strings.ReplaceAll(absFilename, "/", "-"),
				path.Ext(info.Name()))
			if filenameOnly == profileName {
				if err := os.Remove(absPath); err != nil {
					return err
				}
				lastDir := absPath[:strings.LastIndex(absPath, "/")]
				for lastDir != config.DefaultProfilePath {
					dir, err := ioutil.ReadDir(lastDir)
					if err != nil {
						return err
					}
					if len(dir) == 0 {
						if err = os.Remove(lastDir); err != nil {
							return err
						}
					}
					lastDir = lastDir[:strings.LastIndex(lastDir, "/")]
				}
			}
		}
		return nil
	})

	if err != nil {
		return err
	}

	return nil
}

// UpdateProfile method update the profile
func UpdateProfile(profileName string, data string) error {
	err := filepath.Walk(config.DefaultProfilePath, func(absPath string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			absFilename := absPath[len(config.DefaultProfilePath)+1:]
			filenameOnly := strings.TrimSuffix(strings.ReplaceAll(absFilename, "/", "-"),
				path.Ext(info.Name()))
			if filenameOnly == profileName {
				err := utils.WriteFile(absPath, data, utils.FilePerm, os.O_WRONLY|os.O_CREATE|os.O_TRUNC)
				if err != nil {
					return err
				}
			}
		}
		return nil
	})

	if err != nil {
		return err
	}

	return nil
}

// GetProfileInclude method get include info in profile
func GetProfileInclude(name string) (string, error) {
	var file *ini.File
	err := filepath.Walk(config.DefaultProfilePath, func(absPath string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			absFilename := absPath[len(config.DefaultProfilePath)+1:]
			filenameOnly := strings.TrimSuffix(strings.ReplaceAll(absFilename, "/", "-"),
				path.Ext(info.Name()))
			if filenameOnly == name {
				var err error
				file, err = ini.Load(absPath)
				if err != nil {
					return err
				}
				return nil
			}
		}
		return nil
	})

	if err != nil {
		return "", err
	}

	if file == nil {
		return "", fmt.Errorf("%s profile is not found", name)
	}

	for _, section := range file.Sections() {
		if section.Name() == "main" {
			if section.HasKey("include") {
				key, _ := section.GetKey("include")
				values := make([]string, 0)
				for _, includeValue := range strings.Split(key.Value(), ",") {
					segValue := strings.SplitN(includeValue, "-", 2)
					value := segValue[0]
					if len(segValue) >= 2 {
						value = segValue[1]
					}
					values = append(values, value)
				}

				return strings.Join(values, "-"), nil
			}
		}
	}

	return "", nil
}
