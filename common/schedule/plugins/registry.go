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

package plugins

import (
	"gitee.com/openeuler/A-Tune/common/schedule/framework"
	"gitee.com/openeuler/A-Tune/common/schedule/plugins/numaaware"
	"gitee.com/openeuler/A-Tune/common/schedule/plugins/powersave"
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
