/*
 * Copyright (c) 2019 Huawei Technologies Co., Ltd.
 * A-Tune is licensed under the Mulan PSL v1.
 * You can use this software according to the terms and conditions of the Mulan PSL v1.
 * You may obtain a copy of Mulan PSL v1 at:
 *     http://license.coscl.org.cn/MulanPSL
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v1 for more details.
 * Create: 2019-10-29
 */

package http

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"strings"
)

//HTTPClient :the structer that encapsulation the net/http package
type httpClient struct {
	client *http.Client
}

//Do method do the action send the data to the http server
func (c *httpClient) Do(req *http.Request) (*http.Response, error) {
	response, err := c.client.Do(req)
	return response, err
}

func newhttpClient() *httpClient {
	var client *http.Client

	client = &http.Client{}

	return &httpClient{
		client: client,
	}

}

func newRequest(method string, url string, body interface{}) (*http.Request, error) {
	var reader io.Reader

	switch body.(type) {
	case string:
		reader = strings.NewReader(body.(string))
	case []byte:
		reader = bytes.NewReader(body.([]byte))
	default:
		bytesData, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		reader = bytes.NewReader(bytesData)

	}

	request, err := http.NewRequest(method, url, reader)
	request.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	if err != nil {
		return nil, err
	}

	request.Header.Add("Content-Type", "application/json")

	return request, nil
}

// Get method call the restfull GET method
func Get(url string, data interface{}) (*http.Response, error) {
	restClient := newhttpClient()
	req, err := newRequest("GET", url, data)
	if err != nil {
		return nil, err
	}

	response, err := restClient.Do(req)
	if err != nil {
		return nil, err
	}

	return response, nil
}

//Post method call the restfull POST method
func Post(url string, data interface{}) (*http.Response, error) {
	restClient := newhttpClient()
	req, err := newRequest("POST", url, data)
	if err != nil {
		return nil, err
	}

	response, err := restClient.Do(req)
	if err != nil {
		return nil, err
	}

	return response, nil
}

// Put method call the restfull PUT method
func Put(url string, data interface{}) (*http.Response, error) {
	restClient := newhttpClient()
	req, err := newRequest("PUT", url, data)
	if err != nil {
		return nil, err
	}

	response, err := restClient.Do(req)
	if err != nil {
		return nil, err
	}

	return response, nil
}

// Delete method call the restfull DELETE method
func Delete(url string) (*http.Response, error) {
	restClient := newhttpClient()
	req, err := newRequest("DELETE", url, nil)
	if err != nil {
		return nil, err
	}

	response, err := restClient.Do(req)
	if err != nil {
		return nil, err
	}

	return response, nil
}
