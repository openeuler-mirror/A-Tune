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

package numaaware

import (
	"gitee.com/openeuler/A-Tune/common/topology"
)

type lighterLoadCallback struct {
	node *topology.TopoNode
	t    topology.TopoType
}

// Callback to find less load node
func (callback *lighterLoadCallback) Callback(node *topology.TopoNode) {
	if node.Type() != callback.t {
		return
	}
	if callback.node == nil {
		callback.node = node
		return
	}
	diff := node.GetLoadInfo().CompareLoad(callback.node.GetLoadInfo())
	if diff < 0 || (diff == 0 && node.GetLoadInfo().CompareBind(callback.node.GetLoadInfo()) < 0) {
		callback.node = node
	}
}

// SelectTypeNode select node with least load and TopoType t
func SelectTypeNode(t topology.TopoType) *topology.TopoNode {
	var callback lighterLoadCallback
	callback.t = t
	callback.node = nil

	topology.ForeachTypeCall(t, &callback)
	return callback.node
}

// SelectLighterLoadNode select given node's child which has least load and TopoType t
func SelectLighterLoadNode(node *topology.TopoNode, t topology.TopoType) *topology.TopoNode {
	var callback lighterLoadCallback
	callback.t = t
	callback.node = nil

	node.ForeachChildCall(&callback)
	return callback.node
}

type lighterBindCallback struct {
	node *topology.TopoNode
	t    topology.TopoType
}

// Callback to find less bind node
func (callback *lighterBindCallback) Callback(node *topology.TopoNode) {
	if node.Type() != callback.t {
		return
	}
	if callback.node == nil {
		callback.node = node
		return
	}
	if node.GetLoadInfo().CompareBind(callback.node.GetLoadInfo()) < 0 {
		callback.node = node
		return
	}
}

// SelectLighterLoadNode select given node's child which has least bind and TopoType t
func SelectLighterBindNode(node *topology.TopoNode, t topology.TopoType) *topology.TopoNode {
	var callback lighterBindCallback
	callback.t = t
	callback.node = nil

	node.ForeachChildCall(&callback)
	return callback.node
}
