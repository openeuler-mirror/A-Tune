package plugins

import (
	"atune/common/schedule/framework"
	"atune/common/schedule/plugins/numaaware"
	"atune/common/schedule/plugins/powersave"
)

// PluginFactory used to create new plugin
type PluginFactory = func() (framework.Plugin, error)

// Registry used to register new plugin
type Registry map[string]PluginFactory

// PluginTables used to get all plugin create functions
func PluginTables() Registry {
	return Registry{
		numaaware.Name: numaaware.New,
		powersave.Name: powersave.New,
	}
}
