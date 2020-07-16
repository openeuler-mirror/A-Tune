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

package framework

import (
	"gitee.com/openeuler/A-Tune/common/topology"
)

// BindTaskInfo used for plugins to set nodes for processes
type BindTaskInfo struct {
	Node *topology.TopoNode
	Pid  uint64
}

// Plugin :interface used for different policy to implement
type Plugin interface {
	Name() string
	Preprocessing(bindtaskinfo *[]*BindTaskInfo)
	PickNodesforPids(bindtaskinfo *[]*BindTaskInfo)
	Postprocessing(bindtaskinfo *[]*BindTaskInfo)
}
