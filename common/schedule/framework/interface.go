package framework

import (
	"atune/common/topology"
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
