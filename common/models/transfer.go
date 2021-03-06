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
 * Create: 2020-11-28
 */

package models

import (
    "fmt"
    "io/ioutil"
    "strconv"
    "strings"

    "gitee.com/openeuler/A-Tune/common/config"
    "gitee.com/openeuler/A-Tune/common/http"
)

// TransferPutBody : the body put to transfer service
type TransferPutBody struct {
    Type            string `json:"type"`
    CollectId       int    `json:"collect_id"`
    Status          string `json:"status"`
    Data            string `json:"collect_data"`
    Workload        string `json:"workload_type"`
}

// Put method send benchmark result to optimizer service
func (o *TransferPutBody) Put() (int, error) {
    url := config.GetURL(config.TransferURI)
    response, err := http.Put(url, o)
    if err != nil {
        return -1, err
    }

    if response.StatusCode != 200 {
        return -1, fmt.Errorf("transfer data failed: %s, status: %d", o.Type, response.StatusCode)
    }

    resp, err := ioutil.ReadAll(response.Body)
    if err != nil {
        return -1, err
    }
    defer response.Body.Close()

    retId := strings.Replace(string(resp), "\n", "", -1)
    val, err := strconv.Atoi(retId)
    if err != nil {
        return -1, err
    }
    return val, nil
}

// InitTransfer method create transferBody and run put
func InitTransfer(types string, status string, data string, workload string, id int) (int, error) {
    transferPut := new(TransferPutBody)
    transferPut.Type = types
    transferPut.Status = status
    transferPut.CollectId = id
    transferPut.Data = data
    transferPut.Workload = workload
    return transferPut.Put()
}
