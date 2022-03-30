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

package cpumask

import (
	"strconv"
	
	"gitee.com/openeuler/A-Tune/common/utils"
)

const cpumaskNum = 10
const oneMaskBits = 64

// Cpumask is union bit of cpus
type Cpumask struct {
	Masks [cpumaskNum]uint64
}

// Init cpumask
func (mask *Cpumask) Init() {
	for i := 0; i < cpumaskNum; i++ {
		mask.Masks[i] = 0
	}
}

// And bits of mask with dst
func (mask *Cpumask) And(dst *Cpumask) {
	for i := 0; i < cpumaskNum; i++ {
		mask.Masks[i] &= dst.Masks[i]
	}
}

// Or bits of mask with dst
func (mask *Cpumask) Or(dst *Cpumask) {
	for i := 0; i < cpumaskNum; i++ {
		mask.Masks[i] |= dst.Masks[i]
	}
}

// IsEqual check if bits of mask is equal to bits of dst
func (mask *Cpumask) IsEqual(dst *Cpumask) bool {
	for i := 0; i < cpumaskNum; i++ {
		if mask.Masks[i] != dst.Masks[i] {
			return false
		}
	}
	return true
}

// Set correspond bit of mask
func (mask *Cpumask) Set(nbit int) {
	maskIndex := nbit / oneMaskBits
	var oneMask = uint64(1) << uint(nbit%oneMaskBits)

	if maskIndex >= cpumaskNum || maskIndex < 0 {
		return
	}
	mask.Masks[maskIndex] |= oneMask
}

// Clear correspond bit of mask
func (mask *Cpumask) Clear(nbit int) {
	maskIndex := nbit / oneMaskBits
	var oneMask = uint64(1) << uint(nbit%oneMaskBits)

	if maskIndex >= cpumaskNum || maskIndex < 0 {
		return
	}
	mask.Masks[maskIndex] &= ^oneMask
}

// Copy bits of mask to dst
func (mask *Cpumask) Copy(dst *Cpumask) {
	for i := 0; i < cpumaskNum; i++ {
		mask.Masks[i] = dst.Masks[i]
	}
}

// ParseString get mask bits from hex string like "fff00aaff"
func (mask *Cpumask) ParseString(str string) error {
	var err error
	const CharsPerUint64 = 16

	mask.Init()
	for maskIndex := 0; maskIndex < cpumaskNum; maskIndex++ {
		endIndex := len(str) - maskIndex*CharsPerUint64
		startIndex := endIndex - CharsPerUint64
		if startIndex < 0 {
			startIndex = 0
		}
		oneMaskStr := str[startIndex:endIndex]
		mask.Masks[maskIndex], err = strconv.ParseUint(oneMaskStr, utils.HexBase, utils.Uint64Bits)
		if err != nil {
			return err
		}
		if startIndex == 0 {
			break
		}
	}
	return nil

}

func oneMaskWeight(mask uint64) int {
	weight := 0

	for mask > 0 {
		weight++
		mask = mask & (mask - 1)
	}
	return weight
}

// Weight get mask bits count
func (mask *Cpumask) Weight() int {
	weight := 0

	for i := 0; i < cpumaskNum; i++ {
		weight += oneMaskWeight(mask.Masks[i])
	}
	return weight
}

func lowBit(mask uint64) int {
	n := 0
	// check if any bit of low 32 bit is set, skip if no bit set
	if mask&0xffffffff == 0 {
		mask = mask >> 32
		n += 32
	}
	// check if any bit of low rest 16 bit is set, skip if no bit set
	if mask&0xffff == 0 {
		mask = mask >> 16
		n += 16
	}
	// check if any bit of low rest 8 bit is set, skip if no bit set
	if mask&0xff == 0 {
		mask = mask >> 8
		n += 8
	}
	// check if any bit of low rest 4 bit is set, skip if no bit set
	if mask&0xf == 0 {
		mask = mask >> 4
		n += 4
	}
	// check if any bit of low rest 2 bit is set, skip if no bit set
	if mask&0x3 == 0 {
		mask = mask >> 2
		n += 2
	}
	// check if any bit of low last bit is set, skip if no bit set
	if mask&0x1 == 0 {
		mask = mask >> 1
		n++
	}
	// return -1 if no bit set
	if mask&0x1 == 0 {
		return -1
	}
	return n
}

// Foreach get next set bit of mask from startBit
func (mask *Cpumask) Foreach(startBit int) int {
	startIndex := (startBit + 1) / oneMaskBits
	firstMask := mask.Masks[startIndex]
	firstMask &= ^((uint64(1) << uint64((startBit+1)%oneMaskBits)) - 1)
	leftbit := lowBit(firstMask)
	if leftbit != -1 {
		return startIndex*oneMaskBits + leftbit
	}

	for startIndex++; startIndex < cpumaskNum; startIndex++ {
		leftbit = lowBit(mask.Masks[startIndex])
		if leftbit != -1 {
			return startIndex*oneMaskBits + leftbit
		}
	}

	return -1
}
