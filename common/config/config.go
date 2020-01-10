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

package config

import (
	"atune/common/log"
	"atune/common/utils"
	"fmt"
	"os"
	"path"
	"strings"

	"github.com/go-ini/ini"
)

// application common config
const (
	Version = "0.0.1"

	EnvAddr    = "ATUNED_ADDR"
	EnvPort    = "ATUNED_PORT"
	EnvTLS     = "ATUNE_TLS"
	EnvCliCert = "ATUNE_CLICERT"

	DefaultTgtPort = "60001"
	DefaultTgtAddr = "127.0.0.1"
)

// default path config
const (
	DefaultPath             = "/usr/lib/atuned/"
	DefaultModDaemonSvrPath = DefaultPath + "modules"
	DefaultConfPath         = "/etc/atuned/"
	DefaultTuningPath       = DefaultConfPath + "tuning/"
	DefaultScriptPath       = "/usr/libexec/atuned/scripts"
	DefaultCollectorPath    = "/usr/libexec/atuned/collector"
	DefaultAnalysisPath     = "/usr/libexec/atuned/analysis"
	DefaultTempPath         = "/run/atuned"
	DefaultCheckerPath      = "/usr/share/atuned/checker/"
	DefaultBackupPath       = "/usr/share/atuned/backup/"
)

// log config
const (
	LogPath     = "/var/log/atuned"
	LogFileName = "atuned.log"
	Formatter   = "text"
	Modes       = "syslog"
)

// python service url
const (
	Protocol   string = "http"
	LocalHost  string = "localhost"
	APIVersion string = "v1"

	ConfiguratorURI   string = "setting"
	MonitorURI        string = "monitor"
	OptimizerURI      string = "optimizer"
	CollectorURI      string = "collector"
	ClassificationURI string = "classification"
	ProfileURI        string = "profile"
	TrainingURI       string = "training"
)

// database config
const (
	DatabasePath string = "/var/lib/atuned"
	DatabaseType string = "sqlite3"
	DatabaseName string = "atuned.db"
)

// monitor config
const (
	FileFormat string = "xml"
)

//tuning config
const (
	TuningFile          string      = DefaultTempPath + "/tuning.log"
	TuningRestoreConfig string      = "-tuning-restore.conf"
	FilePerm            os.FileMode = 0600
	DefaultTimeFormat   string      = "2006-01-02 15:04:05"
)

// the grpc server config
var (
	Address           string
	Port              string
	RestPort          string
	TLS               bool
	TLSServerCertFile string
	TLSServerKeyFile  string
	TLSHTTPCertFile   string
	TLSHTTPKeyFile    string
	TLSHTTPCACertFile string
)

// Cfg type, the type that load the conf file
type Cfg struct {
	Raw *ini.File
}

//Load method load the default conf file
func (c *Cfg) Load() error {
	defaultConfigFile := path.Join(DefaultConfPath, "atuned.cnf")

	exist, err := utils.PathExist(defaultConfigFile)
	if err != nil {
		return err
	}
	if !exist {
		return fmt.Errorf("could not find default config file")
	}

	cfg, err := ini.Load(defaultConfigFile)
	if err != nil {
		return fmt.Errorf("faild to parse %s, %v", defaultConfigFile, err)
	}

	c.Raw = cfg

	section := cfg.Section("server")
	Address = section.Key("address").MustString("127.0.0.1")
	Port = section.Key("port").MustString("60001")
	RestPort = section.Key("rest_port").MustString("8383")
	TLS = section.Key("tls").MustBool(false)

	if TLS {
		TLSServerCertFile = section.Key("tlsservercertfile").MustString("")
		TLSServerKeyFile = section.Key("tlsserverkeyfile").MustString("")
		TLSHTTPCertFile = section.Key("tlshttpcertfile").MustString("")
		TLSHTTPKeyFile = section.Key("tlshttpkeyfile").MustString("")
		TLSHTTPCACertFile = section.Key("tlshttpcacertfile").MustString("")
	}

	if err := initLogging(cfg); err != nil {
		return err
	}

	return nil
}

//NewCfg method create the cfg struct that store the conf file
func NewCfg() *Cfg {
	return &Cfg{
		Raw: ini.Empty(),
	}
}

func initLogging(cfg *ini.File) error {
	modes := strings.Split(Modes, ",")
	err := log.InitLogger(modes, cfg)

	return err
}

// GetURL return the url
func GetURL(uri string) string {
	protocol := Protocol
	if TLS {
		protocol = "https"
	}
	url := fmt.Sprintf("%s://%s:%s/%s/%s", protocol, LocalHost, RestPort, APIVersion, uri)
	return url
}
