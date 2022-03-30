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

package client

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"io/ioutil"
	"net"
	"os"
	"time"
	"context"

	"github.com/urfave/cli"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	
	"gitee.com/openeuler/A-Tune/common/config"
)

type clientOpts struct {
	dialOptions []grpc.DialOption
}

// Opt allows callers to set options on the client
type Opt func(c *clientOpts) error

//Client :The grpc client structer
type Client struct {
	conn     *grpc.ClientConn
	services map[string]interface{}
}

// GetService method return the grpc client command plugin service
func (c *Client) GetService(name string) (interface{}, error) {
	_, ok := c.services[name]
	if !ok {
		return nil, fmt.Errorf("there is no service %s available", name)
	}

	return c.services[name], nil
}

// NewService method call the function to new a grpc client plugin service
func (c *Client) NewService(name string, fn func(cc *grpc.ClientConn) (interface{}, error)) error {
	if _, ok := c.services[name]; ok {
		return fmt.Errorf("service %s client has existed", name)
	}
	svc, err := fn(c.conn)
	if err != nil {
		return err
	}

	c.services[name] = svc

	return nil
}

// Connection method return the grpc connection of the client
func (c *Client) Connection() *grpc.ClientConn {
	return c.conn
}

//Close method close the grpc connection
func (c *Client) Close() {
	_ = c.conn.Close()
}

//GetState method return the state of the grpc connection
func (c *Client) GetState() string {
	return c.conn.GetState().String()
}

//NewWithConn method create a grpc client depend the connection
func NewWithConn(conn *grpc.ClientConn, opts ...Opt) (*Client, error) {
	return &Client{
		conn:     conn,
		services: make(map[string]interface{}),
	}, nil
}

//NewClientFromContext method create a grpc client depend the command context
func NewClientFromContext(ctx *cli.Context, opts ...Opt) (*Client, error) {
	addr, port := parseAddr(ctx)
	var address string
	if port == "" {
		address = addr
	} else {
		address = addr + ":" + port
	}

	return newClient(address, opts...)
}

// NewClientWithoutCli method create a grpc client depend the address and port
func NewClientWithoutCli(addr string, port string, opts ...Opt) (*Client, error) {
	if addr == config.DefaultTgtAddr {
		addr, _ = ParseEnvAddr()
	}
	if port == config.DefaultTgtPort {
		_, port = ParseEnvAddr()
	}

	var address string
	if port == "" {
		address = addr
	} else {
		address = addr + ":" + port
	}

	return newClient(address, opts...)
}

//NewClientFromConn method create a grpc client depend the conn, which is address:port format
func NewClientFromConn(conn string, opts ...Opt) (*Client, error) {
	return newClient(conn, opts...)
}

//NewClient method create a grpc client depend the address and port
func NewClient(addr string, port string, opts ...Opt) (*Client, error) {
	var address string
	if port == "" {
		address = addr
	} else {
		address = addr + ":" + port
	}
	return newClient(address, opts...)
}

// UnixConnect method creates a connection to given address
func UnixConnect(ctx context.Context, addr string) (net.Conn, error) {
	unixAddr, _ := net.ResolveUnixAddr("unix", addr)
	return net.DialUnix("unix", nil, unixAddr)
}

func newClient(address string, opts ...Opt) (*Client, error) {
	var copts clientOpts
	for _, o := range opts {
		if err := o(&copts); err != nil {
			return nil, err
		}
	}
	gopts := []grpc.DialOption{
		grpc.WithBlock(),
		grpc.FailOnNonTempDialError(true),
		grpc.WithBackoffMaxDelay(3 * time.Second),
	}

	envTls := os.Getenv(config.EnvTLS)
	if envTls == "yes" {
		pool := x509.NewCertPool()
		caCrt, err := ioutil.ReadFile(os.Getenv(config.EnvCaCert))
		if err != nil {
			return nil, err
		}
		if ok := pool.AppendCertsFromPEM(caCrt); !ok {
			return nil, fmt.Errorf("failed to append ca certs in client")
		}

		certificate, err := tls.LoadX509KeyPair(os.Getenv(config.EnvClientCert),
			os.Getenv(config.EnvClientKey))
		if err != nil {
			return nil, err
		}

		creds := credentials.NewTLS(&tls.Config{
			Certificates: []tls.Certificate{certificate},
			ServerName:   os.Getenv(config.EnvServerCN),
			RootCAs:      pool,
		})

		gopts = append(gopts, grpc.WithTransportCredentials(creds))
	} else {
		gopts = append(gopts, grpc.WithInsecure())
	}

	if address == config.DefaultTgtAddr {
		gopts = append(gopts, grpc.WithContextDialer(UnixConnect))
	}

	if len(copts.dialOptions) > 0 {
		gopts = copts.dialOptions
	}

	ctx := context.Background()
	ctx, cancel := context.WithTimeout(ctx, 60*time.Second)
	defer cancel()

	conn, err := grpc.DialContext(ctx, address, gopts...)
	if err != nil {
		return nil, fmt.Errorf("failed to dial %q : %s", address, err)
	}
	return NewWithConn(conn, opts...)
}

//ParseEnvAddr method return the ip and port depend the Env, if not return the default value
func ParseEnvAddr() (string, string) {
	addr := os.Getenv(config.EnvAddr)
	if addr == "" {
		addr = config.DefaultTgtAddr
	}

	port := os.Getenv(config.EnvPort)
	if port == "" {
		port = config.DefaultTgtPort
	}

	return addr, port
}

//ParseCliAddr method return the ip and port depend the command context
func ParseCliAddr(ctx *cli.Context) (string, string) {
	return ctx.GlobalString("address"), ctx.GlobalString("port")
}

func parseAddr(ctx *cli.Context) (string, string) {
	addr, port := ParseCliAddr(ctx)

	if addr == config.DefaultTgtAddr {
		addr, _ = ParseEnvAddr()
	}
	if port == config.DefaultTgtPort {
		_, port = ParseEnvAddr()
	}

	return addr, port
}
