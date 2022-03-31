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

package timer

import (
	"fmt"
	"io"
	"strconv"
	"time"

	CTX "golang.org/x/net/context"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/client"
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/utils"
)

func init() {
	// registry.RegisterDaemonService("timer", &Timer{})
}

// Timer : a timer for dynamic tuning
type Timer struct {
	Cfg      *config.Cfg
	ticker   *time.Ticker
	interval int
	isRun    bool
}

// Init method init the Timer service
func (t *Timer) Init() error {
	t.interval = 60
	return nil
}

// Set the config of the monitor
func (t *Timer) Set(cfg *config.Cfg) {
	t.Cfg = cfg
}

//Run method start the ticker, auto-tuning the system
func (t *Timer) Run() error {
	/* Static & Dynamic judge */
	if err := utils.WaitForPyservice(); err != nil {
		log.Errorf("waiting for pyservice failed: %v", err)
		return err
	}

	section, err := t.Cfg.Raw.GetSection("server")
	if err != nil {
		log.Errorf("failed to get section system, error: %v", err)
		return err
	}
	if !section.Haskey("type") {
		return fmt.Errorf("type is not exist in the server section")
	}

	if section.Key("type").Value() == "static" {
		return nil
	} else if section.Key("type").Value() == "dynamic" {
		if section.Haskey("interval") {
			t.interval, _ = section.Key("interval").Int()
		}

		d, _ := time.ParseDuration(strconv.FormatInt(int64(t.interval), 10) + "s")
		t.ticker = time.NewTicker(d)
		t.isRun = true

		c, err := client.NewClientWithoutCli(config.DefaultTgtAddr, config.DefaultTgtPort)
		if err != nil {
			return err
		}
		defer c.Close()

		for {
			<-t.ticker.C
			log.Info("active the ticker, starting dynamic tuning,")
			go func() {
				svc := PB.NewProfileMgrClient(c.Connection())
				stream, err := svc.Analysis(CTX.Background(), &PB.AnalysisMessage{})
				if err != nil {
					log.Error(err)
					return
				}
				for {
					_, err := stream.Recv()
					if err == io.EOF {
						break
					}

					if err != nil {
						log.Error(err)
						return
					}
				}
			}()
		}
	} else {
		return fmt.Errorf("in section server, type must be dynamic or statis")
	}
}
