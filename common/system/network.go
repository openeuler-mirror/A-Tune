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

package system

import (
	"encoding/xml"
)

type netChild struct {
	Name    string `xml:"logicalname"`
	Claimed string `xml:"claimed"`
	Class   string `xml:"class"`
}

type network struct {
	Name     string   `xml:"logicalname"`
	Vendor   string   `xml:"vendor"`
	Product  string   `xml:"product"`
	NetChild netChild `xml:"children"`
}

// NetworkTopo storage the network info
type NetworkTopo struct {
	XMLName  xml.Name  `xml:"topology"`
	Networks []network `xml:"networks"`
}
