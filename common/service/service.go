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

package module

import (
	"context"
	"fmt"
	"net"
	"strings"
	"sync"

	"github.com/urfave/cli"
	"google.golang.org/grpc"
	"google.golang.org/grpc/peer"
	
	"gitee.com/openeuler/A-Tune/common/config"
)

// OptServices :the global value to store grpc service
var OptServices = struct {
	sync.RWMutex
	services map[string]*ProfileService
}{}

func init() {
	OptServices.services = make(map[string]*ProfileService)
}

// ProfileService :the service for grpc server
type ProfileService struct {
	Name     string
	Requires []string
	Desc     string
	Path     string
	NewInst  func(ctx *cli.Context, opts ...interface{}) (interface{}, error)
}

func (s *ProfileService) String() string {
	return s.Name
}

// SvrService :every service need to implement SvrService and CliService interface.
// one for server side, the other is for client side
type SvrService interface {
	RegisterServer(*grpc.Server) error
	Healthy(opts ...interface{}) error
}

// CliService :the interface for grpc client
type CliService interface {
	Register() error
	GetCommand() cli.Command
}

// AddService method register the service svc
func AddService(svc *ProfileService) error {
	OptServices.Lock()
	defer OptServices.Unlock()

	if _, existed := OptServices.services[svc.Name]; existed {
		return fmt.Errorf("service existed : %s", svc.Name)
	}

	OptServices.services[svc.Name] = svc

	return nil
}

// WalkServices method callback the fn method
func WalkServices(fn func(nm string, svc *ProfileService) error) error {
	OptServices.Lock()
	defer OptServices.Unlock()

	for name, service := range OptServices.services {
		if err := fn(name, service); err != nil {
			return err
		}
	}

	return nil
}

// CreateInstance method return the instance of service of name
func CreateInstance(name string) (interface{}, error) {
	OptServices.Lock()
	defer OptServices.Unlock()

	svc, existed := OptServices.services[name]
	if !existed {
		return nil, fmt.Errorf("There is not %s service", name)
	}

	instance, err := svc.NewInst(nil)
	if err != nil {
		return nil, err
	}

	return instance, nil
}

// GetServices return the slice of the service name
func GetServices() ([]string, error) {
	OptServices.Lock()
	defer OptServices.Unlock()

	var svc []string
	for name := range OptServices.services {
		svc = append(svc, name)
	}

	return svc, nil
}

//CheckRpcIsLocalAddr return whether rpc is a local addr
func CheckRpcIsLocalAddr(ctx context.Context) (bool, error) {
	if config.TransProtocol != "tcp" {
		return true, nil
	}

	pr, ok := peer.FromContext(ctx)
	if !ok || pr.Addr == net.Addr(nil) {
		return false, fmt.Errorf("failed to get rpc client ip")
	}
	clientAddr := strings.Split(pr.Addr.String(), ":")[0]

	serverAddr, err := net.InterfaceAddrs()
	if err != nil {
		return false, err
	}

	for i := range serverAddr {
		addr, _, err := net.ParseCIDR(serverAddr[i].String())
		if err != nil {
			return false, err
		}
		if net.ParseIP(clientAddr).Equal(addr) {
			return true, nil
		}
	}
	return false, nil
}
