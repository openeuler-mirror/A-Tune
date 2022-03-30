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
	"bufio"
	"os"
	"strconv"
	"strings"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
)

// NumaMem represent the memory topology type
type NumaMem struct {
	Path string
}

/*
GetAllCPU check the cpu information
*/
func (m *NumaMem) GetAllCPU(ch chan *PB.AckCheck) ([]int, error) {
	file, err := os.Open(m.Path)
	if err != nil {
		return nil, err
	}

	defer file.Close()

	cpus := make([]int, 0)
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		parts := strings.Fields(scanner.Text())
		if len(parts) < 4 {
			continue
		}
		if "cpus" == strings.Trim(parts[2], ":") {
			cpuParts := parts[3:]
			for _, cpuIndex := range cpuParts {
				cpu, _ := strconv.Atoi(cpuIndex)
				cpus = append(cpus, cpu)
			}
		}
	}

	return cpus, nil
}
