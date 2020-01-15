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

package main

import (
	"atune/common/config"
	"atune/common/log"
	"atune/common/registry"
	SVC "atune/common/service"
	"atune/common/sqlstore"
	"atune/common/utils"
	"fmt"
	"net"
	"os"

	"github.com/coreos/go-systemd/daemon"
	"github.com/urfave/cli"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/reflection"
)

const (
	atunedUsage = `atuned daemon is the AI system daemon
To get more info of how to use atuned:
	# atuned help
`
)

type swServer struct {
	server *grpc.Server
	svcs   map[string]interface{}
}

func newServer(rpc *grpc.Server) (*swServer, error) {
	server := new(swServer)
	server.server = rpc
	server.svcs = make(map[string]interface{})

	return server, nil
}

func createSvcInsts(ctx *cli.Context, svr *swServer) error {
	if err := SVC.WalkServices(func(nm string, svc *SVC.ProfileService) error {
		inst, err := svc.NewInst(ctx)
		if err != nil {
			fmt.Printf("Create %s instance failed\n", nm)
			return nil
		}

		log.Infof("Create %s service successfully\n", nm)

		sinst, ok := inst.(SVC.SvrService)
		if !ok {
			return fmt.Errorf("not impletment SvrService")
		}

		if err := sinst.RegisterServer(svr.server); err != nil {
			return err
		}

		svr.svcs[nm] = inst

		return nil
	}); err != nil {
		return err
	}

	return nil
}

func loadModules(ctx *cli.Context, svr *swServer, path string) error {
	exist, err := utils.PathExist(path)
	if err != nil {
		return err
	}
	if !exist {
		return nil
	}

	if err := utils.LoadPlugins(path); err != nil {
		return err
	}

	if err := createSvcInsts(ctx, svr); err != nil {
		return err
	}

	return nil
}

func doBeforeJob(ctx *cli.Context) error {
	// Load conf file
	cfg := config.NewCfg()
	if err := cfg.Load(); err != nil {
		log.Errorf("Faild to load config file, error: %v", err)
		return fmt.Errorf("faild to load config file, error: %v", err)
	}

	store := &sqlstore.Sqlstore{
		Cfg: cfg,
	}
	// init the sqlite3 database engine
	if err := store.Init(); err != nil {
		log.Error(err)
		return err
	}

	services := registry.GetDaemonServices()

	for _, service := range services {
		log.Infof("initializing service: %s", service.Name)
		service.Instance.Set(cfg)
		if err := service.Instance.Init(); err != nil {
			return fmt.Errorf("service init faild: %v", err)
		}
	}

	// starting all service
	for _, srv := range services {
		service := srv
		backgroundService, ok := service.Instance.(registry.BackgroundService)
		if !ok {
			continue
		}

		go func() {
			err := backgroundService.Run()
			if err != nil {
				log.Errorf("service %s running faild, reason: %v", service.Name, err)
				return
			}
		}()
	}

	return nil
}

func runatuned(ctx *cli.Context) error {
	var lis net.Listener
	var err error
	if config.TransProtocol == "tcp" {
		lis, err = net.Listen("tcp", config.Address+":"+config.Port)
	} else if config.TransProtocol == "unix" {
		os.Remove(config.DefaultTgtAddr)
		lis, err = net.Listen("unix", config.Address)
		if err != nil {
			log.Fatalf("failed to listen: %v", err)
		}
		err = os.Chmod(config.DefaultTgtAddr, 0600)
	} else {
		return fmt.Errorf("not support protocol:%s", config.TransProtocol)
	}

	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	var opts []grpc.ServerOption
	if config.TLS {
		log.Info("server tls enabled")
		creds, err := credentials.NewServerTLSFromFile(config.TLSServerCertFile, config.TLSServerKeyFile)
		if err != nil {
			log.Fatalf("Failed to generate credentials %v", err)
		}
		opts = []grpc.ServerOption{grpc.Creds(creds)}
	}
	s := grpc.NewServer(opts...)

	server, err := newServer(s)
	if err != nil {
		return err
	}

	if err := loadModules(ctx, server, config.DefaultModDaemonSvrPath); err != nil {
		return err
	}

	if err := utils.WaitForPyservice(); err != nil {
		log.Errorf("waiting for pyservice faild: %v", err)
		return err
	}

	log.Info("pyservice has been started")
	_, _ = daemon.SdNotify(false, "READY=1")

	reflection.Register(s)
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}

	return nil
}

func main() {
	app := cli.NewApp()
	app.Name = "atuned"
	app.Usage = atunedUsage

	app.Version = config.Version
	app.Before = doBeforeJob
	app.Action = runatuned

	if err := app.Run(os.Args); err != nil {
		fmt.Printf("%s\n", err)
		os.Exit(1)
	}
}
