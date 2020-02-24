/* Copyright (c) Huawei Technologies Co., Ltd. 2019-2019. All rights reserved. */

// Package sched implements utility to set schedule properties of tasks
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
