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
	"bytes"
	"crypto/tls"
	"crypto/x509"
	"encoding/json"
	"encoding/pem"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"strings"

	"gitee.com/openeuler/A-Tune/common/config"
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

// VerifyCertificate checks whether certificate file is valid and unexpired
func VerifyCertificate(certFile string, pool *x509.CertPool) error {
	certBytes, err := ioutil.ReadFile(certFile)
	if err != nil {
		return err
	}
	block, _ := pem.Decode(certBytes)
	if block == nil {
		return errors.New("failed to decode certificate")
	}
	cert, err := x509.ParseCertificate(block.Bytes)
	if err != nil {
		return errors.New("failed to parse certificate: " + err.Error())
	}
	opts := x509.VerifyOptions{
		Roots: pool,
	}
	_, err = cert.Verify(opts)
	if err != nil {
		return errors.New("failed to verify certificate: " + err.Error())
	}
	return nil
}

// NewhttpClient create an http client
func NewhttpClient(url string) (*httpClient, error) {
	var client *http.Client
	segs := strings.Split(url, "/")
	if len(segs) < 5 {
		return nil, fmt.Errorf("url: %s is not correct", url)
	}
	uri := segs[4]
	if config.IsEnginePort(uri) && config.EngineTLS || !config.IsEnginePort(uri) && config.RestTLS {
		pool := x509.NewCertPool()
		caFile := config.TLSEngineCACertFile
		if !config.IsEnginePort(uri) {
			caFile = config.TLSRestCACertFile
		}
		caCrt, err := ioutil.ReadFile(caFile)
		if err != nil {
			return nil, err
		}
		pool.AppendCertsFromPEM(caCrt)

		if err = VerifyCertificate(caFile, pool); err != nil {
			return nil, err
		}

		clientCertFile := config.TLSEngineClientCertFile
		clientKeyFile := config.TLSEngineClientKeyFile
		if !config.IsEnginePort(uri) {
			clientCertFile = config.TLSRestServerCertFile
			clientKeyFile = config.TLSRestServerKeyFile
		}

		if err = VerifyCertificate(clientCertFile, pool); err != nil {
			return nil, err
		}

		clientCrt, err := tls.LoadX509KeyPair(clientCertFile, clientKeyFile)
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
	if err != nil {
		return nil, err
	}

	request.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	request.Header.Add("Content-Type", "application/json")

	return request, nil
}

// Get method call the restfull GET method
func Get(url string, data interface{}) (*http.Response, error) {
	restClient, err := NewhttpClient(url)
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
	restClient, err := NewhttpClient(url)
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
	restClient, err := NewhttpClient(url)
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
	restClient, err := NewhttpClient(url)
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
