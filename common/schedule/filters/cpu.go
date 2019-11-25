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

package filters

import (
	"atune/common/log"
	"atune/common/system"
	"errors"
)

type CpuSchedule struct {
	Name string
}

func (s *CpuSchedule) Filte(strategy string) error {
	switch strategy {
	case "auto":
	case "performance":
		return s.performance()
	case "powersave":
		return s.powersave()
	default:
		return errors.New("Strategy don't exist")
	}
	return nil
}

func (s *CpuSchedule) performance() error {
	system := system.GetSystem()

	for _, pid := range system.GetPids("") {
		log.Infof("pid: %d", pid)
	}

	return nil
}

func (s *CpuSchedule) powersave() error {
	system := system.GetSystem()

	for _, pid := range system.GetPids("") {
		log.Infof("pid: %d", pid)
	}

	return nil
}
