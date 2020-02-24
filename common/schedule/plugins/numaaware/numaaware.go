package numaaware

import (
	"atune/common/log"
	"atune/common/schedule/framework"
	"atune/common/topology"
)

// NumaAware pick node concerning NUMA topology
type NumaAware struct {
}

// Name of plugin
const Name = "numaaware"

// Name return name of plugin
func (na *NumaAware) Name() string {
	return Name
}

type numaAwareCallback struct {
	node *topology.TopoNode
}

// callback to update cpu load
func (callback *numaAwareCallback) Callback(node *topology.TopoNode) {
	if callback.node == nil {
		callback.node = node
	} else {
		if callback.node.GetLoad() < node.GetLoad() {
			callback.node = node
		}
	}
}

// Preprocessing do some work before pick nodes
func (na *NumaAware) Preprocessing(bindtaskinfo *[]framework.BindTaskInfo) {
	log.Infof("preprocessing in %s plugin", Name)
}

// PickNodesforPids set nodes for given tasks
func (na *NumaAware) PickNodesforPids(bindtaskinfo *[]framework.BindTaskInfo) {
	var callback numaAwareCallback

	log.Infof("PickNodesforPids in %s plugin", Name)
	callback.node = nil
	topology.ForeachTypeCall(topology.TopoTypeNUMA, &callback)

	for idx := range *bindtaskinfo {
		(*bindtaskinfo)[idx].Node = callback.node
	}
}

// Postprocessing do some work after task bindings
func (na *NumaAware) Postprocessing(bindtaskinfo *[]framework.BindTaskInfo) {
	log.Infof("BalanceNode in %s plugin", Name)
}

// New create a NumaAware
func New() (framework.Plugin, error) {
	return &NumaAware{}, nil
}
