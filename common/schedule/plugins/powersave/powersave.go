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

package powersave

import (
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/schedule/framework"
	"gitee.com/openeuler/A-Tune/common/topology"
)

// PowerSave pick node concerning NUMA topology
type PowerSave struct {
}

// Name of plugin
const Name = "powersave"

// Name return name of plugin
func (na *PowerSave) Name() string {
	return Name
}

type powerSaveCallback struct {
	node *topology.TopoNode
}

// callback to update cpu load
func (callback *powerSaveCallback) Callback(node *topology.TopoNode) {
	if callback.node == nil {
		callback.node = node
	} else {
		if callback.node.GetLoad() > node.GetLoad() {
			callback.node = node
		}
	}
}

// Preprocessing do some work before pick nodes
func (na *PowerSave) Preprocessing(bindtaskinfo *[]*framework.BindTaskInfo) {
	log.Infof("preprocessing in %s plugin", Name)
}

// PickNodesforPids set nodes for given tasks
func (na *PowerSave) PickNodesforPids(bindtaskinfo *[]*framework.BindTaskInfo) {
	var callback powerSaveCallback

	log.Infof("PickNodesforPids in %s plugin", Name)
	callback.node = nil
	topology.ForeachTypeCall(topology.TopoTypeNUMA, &callback)

	for idx := range *bindtaskinfo {
		(*bindtaskinfo)[idx].Node = callback.node
	}
}

// Postprocessing do some work after task bindings
func (na *PowerSave) Postprocessing(bindtaskinfo *[]*framework.BindTaskInfo) {
	log.Infof("BalanceNode in %s plugin", Name)
}

// New create a PowerSave
func New() (framework.Plugin, error) {
	return &PowerSave{}, nil
}
