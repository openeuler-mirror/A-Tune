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

package tuning

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"strings"

	"github.com/caibirdme/yql"
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/http"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/profile"
	"gitee.com/openeuler/A-Tune/common/sqlstore"
)

// RuleBody : the body send to monitor service
type RuleBody struct {
	Module  string `json:"module"`
	Purpose string `json:"purpose"`
	Field   string `json:"field"`
}

// Post method calling the monitor service
func (r *RuleBody) Post() (*map[string]interface{}, error) {
	url := config.GetURL(config.MonitorURI)
	res, err := http.Post(url, r)
	if err != nil {
		return nil, err
	}

	defer res.Body.Close()
	if res.StatusCode != 200 {
		log.Errorf("URL: %s, response code: %d", url, res.StatusCode)
		return nil, fmt.Errorf("get monitor data failed, url: %s", url)
	}

	respBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}
	respPostIns := new(map[string]interface{})

	err = json.Unmarshal(respBody, respPostIns)
	if err != nil {
		return nil, err
	}
	return respPostIns, nil
}

/*
RuleTuned method will be tuned the system parameter depend on the rules int the table
if rule mached, it will perform the corresponding operation
*/
func RuleTuned(workloadType string) error {
	rules := &sqlstore.GetRuleTuned{Class: workloadType}
	if err := sqlstore.GetRuleTuneds(rules); err != nil {
		return err
	}

	if len(rules.Result) < 1 {
		log.Info("no rules to tuned")
		return nil
	}

	for _, rule := range rules.Result {
		rulePostBody := new(RuleBody)

		monitors := strings.Split(rule.Monitor, ".")
		if len(monitors) != 2 {
			log.Errorf("profile: %s, rule: %d, Monitor is not correct", workloadType, rule.ID)
			continue
		}

		rulePostBody.Module = monitors[0]
		rulePostBody.Purpose = monitors[1]
		rulePostBody.Field = rule.Field

		var respPostIns *map[string]interface{}
		var err error
		respPostIns, err = rulePostBody.Post()
		if err != nil {
			return err
		}

		if rule.Name == "hpre" {
			var support bool
			support, err = IsSupportHpre()
			if err != nil {
				continue
			}
			if !support {
				log.Info("current system is not support hpre")
				continue
			}

			match, _ := HpreTuned(*respPostIns, rule.Expression)
			if match {
				ruleAction(workloadType, rule.Action)
			} else {
				ruleAction(workloadType, rule.OppositeAction)
			}

			return nil
		}
		log.Info("response from server:", respPostIns)
		ruler, _ := yql.Rule(rule.Expression)
		match, err := ruler.Match(*respPostIns)
		if err != nil {
			log.Errorf("profile: %s, rule: %d, match error: %v", workloadType, rule.ID, err)
			continue
		}

		if match {
			ruleAction(workloadType, rule.Action)
		} else {
			ruleAction(workloadType, rule.OppositeAction)
		}
	}
	return nil
}

func ruleAction(workloadType string, action string) {
	pro, _ := profile.LoadFromWorkloadType(workloadType)

	_ = pro.ActiveTuned(nil, action)
}
