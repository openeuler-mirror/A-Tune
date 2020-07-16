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

package http

import (
	"gitee.com/openeuler/A-Tune/common/config"
	"bytes"
	"crypto/tls"
	"crypto/x509"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
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

func newhttpClient() (*httpClient, error) {
	var client *http.Client
	if config.TLS {
		pool := x509.NewCertPool()
		caCrt, err := ioutil.ReadFile(config.TLSHTTPCACertFile)
		if err != nil {
			return nil, err
		}
		pool.AppendCertsFromPEM(caCrt)

		clientCrt, err := tls.LoadX509KeyPair(config.TLSHTTPCertFile, config.TLSHTTPKeyFile)
		if err != nil {
			return nil, err
		}
		tr := &http.Transport{
			TLSClientConfig: &tls.Config{
				RootCAs:      pool,
				Certificates: []tls.Certificate{clientCrt}},
		}
		client = &http.Client{Transport: tr}
	} else {
		client = &http.Client{}
	}

	return &httpClient{
		client: client,
	}, nil
}

func newRequest(method string, url string, body interface{}) (*http.Request, error) {
	var reader io.Reader

	switch t := body.(type) {
	case string:
		reader = strings.NewReader(body.(string))
	case []byte:
		reader = bytes.NewReader(body.([]byte))
	default:
		bytesData, err := json.Marshal(body)
		if err != nil {
			fmt.Printf("Error in Unexpected type %T\n", t)
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
	restClient, err := newhttpClient()
	if err != nil {
		return nil, err
	}
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
	restClient, err := newhttpClient()
	if err != nil {
		return nil, err
	}
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
	restClient, err := newhttpClient()
	if err != nil {
		return nil, err
	}
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
	restClient, err := newhttpClient()
	if err != nil {
		return nil, err
	}
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
