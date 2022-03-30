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
	"github.com/mitchellh/mapstructure"
	
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/http"
	"gitee.com/openeuler/A-Tune/common/log"
)

// Event : the content of response
type Event struct {
	OverHead string `json:"overhead"`
	Object   string `json:"object"`
	Symbol   string `json:"symbol"`
}

// HprePostBody : body send to CPI service
type HprePostBody struct {
	Section string `json:"section"`
	Key     string `json:"key"`
}

// RespHprePost : response of CPI service
type RespHprePost struct {
	Value string `json:"value"`
}

// Get method call the service of CPI
func (h *HprePostBody) Get() (*RespHprePost, error) {
	url := config.GetURL(config.ConfiguratorURI)
	res, err := http.Get(url, h)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode != 200 {
		fmt.Println(res.StatusCode)
		respBody, err := ioutil.ReadAll(res.Body)
		fmt.Println(string(respBody), err)
		return nil, fmt.Errorf("get hpre support failed")
	}

	respBody, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	respPostIns := new(RespHprePost)
	err = json.Unmarshal(respBody, respPostIns)
	if err != nil {
		return nil, err
	}
	return respPostIns, nil
}

// HpreTuned method enable hpre if match the condition
func HpreTuned(m map[string]interface{}, expression string) (bool, error) {
	log.Infof("expression: %s", expression)
	for _, v := range m {
		switch vv := v.(type) {
		case []interface{}:
			for _, value := range vv {
				var event Event
				err := mapstructure.Decode(value, &event)
				if err != nil {
					log.Errorf("map %v convert to struct err %v", value, err)
					continue
				}

				log.Infof("OverHead: %s, Object: %s, Symbol: %s", event.OverHead, event.Object, event.Symbol)

				object := getObjectName(event.Object)

				match, err := yql.Match(expression, map[string]interface{}{
					"object": object,
				})

				if err != nil {
					log.Errorf("match error: %v", err)
					continue
				}
				if match {
					log.Infof("expression %s matches", expression)
					return true, nil
				}
			}
		}
	}
	return false, nil
}

func getObjectName(object string) string {
	objects := strings.Split(object, ".")
	if strings.Contains(objects[0], "-") {
		return strings.Split(objects[0], "-")[0]
	}
	return objects[0]
}

// IsSupportHpre method check system is support hpre or not, only can be used on ARM
func IsSupportHpre() (bool, error) {
	body := &HprePostBody{
		Section: "bios",
		Key:     "hpre_support",
	}
	respGetIns, err := body.Get()
	if err != nil {
		log.Infof("get support_hpre failed")
		return false, fmt.Errorf("get support_hpre failed")
	}

	if respGetIns.Value == "yes" {
		return true, nil
	}

	return false, nil
}
