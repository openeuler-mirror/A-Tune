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

package checker

import (
	PB "atune/api/profile"
	"atune/common/log"
	"atune/common/utils"
)

//ELF file structer
type ELF struct {
	FileName string
}

/*
Check method check the elf file format
*/
func (elf *ELF) Check(ch chan *PB.AckCheck) error {
	log.Debugf("Check %s", elf.FileName)

	sendChanToAdm(ch, elf.FileName, utils.SUCCESS, "FIXME: NOT Implement")

	return nil
}
