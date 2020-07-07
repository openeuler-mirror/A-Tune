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
 * Create: 2020-04-28
 */

package sched

import (
	"fmt"
	"math/bits"
	"syscall"
	"unsafe"
)

const (
	cpuSetSize = 1024
	cpuBits    = bits.UintSize
	cpuBytes   = cpuBits / 8
)

type cpuSet [cpuSetSize / cpuBits]uintptr

// SetAffinity set thread cpu affinity.
func SetAffinity(tid uint64, cpu []uint32) error {
	var mask cpuSet
	for _, cpuID := range cpu {
		mask[cpuID/cpuBits] |= 1 << (cpuID % cpuBits)
	}
	if _, _, errno := syscall.RawSyscall(syscall.SYS_SCHED_SETAFFINITY,
		uintptr(tid), uintptr(len(mask)*cpuBytes), uintptr(unsafe.Pointer(&mask[0]))); errno != 0 {
		return fmt.Errorf("tid:%d setaffinity fails:%s", tid, syscall.Errno(errno))
	}
	return nil
}
