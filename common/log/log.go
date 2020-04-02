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

package log

import (
	"fmt"
	"log/syslog"
	"os"
	"path/filepath"
	"runtime"

	"github.com/go-ini/ini"
	logrus "github.com/sirupsen/logrus"
	logrus_syslog "github.com/sirupsen/logrus/hooks/syslog"
)

type logger struct {
	entry *logrus.Entry
}

var rootLogger = logrus.New()
var baseLogger = logger{entry: logrus.NewEntry(rootLogger)}

// InitLogger method init the base logger
func InitLogger(modes []string, cfg *ini.File) error {
	sec, err := cfg.GetSection("log")
	if err != nil {
		return err
	}
	formatter := getLogFormat("text")

	_ = baseLogger.SetLevel(sec.Key("level").MustString("info"))
	for _, mode := range modes {
		switch mode {
		case "console":
			baseLogger.entry.Logger.Out = os.Stdout
			baseLogger.entry.Logger.Formatter = formatter
		case "syslog":
			syslogHook, err := logrus_syslog.NewSyslogHook("", "", syslog.LOG_INFO, "atuned")
			if err != nil {
				baseLogger.Errorf("syslog hook init failed:%v", err)
			}
			baseLogger.entry.Logger.AddHook(syslogHook)
		}
	}

	return nil
}

func (log logger) withFileField() *logrus.Entry {
	_, filename, line, ok := runtime.Caller(2)
	if ok {
		filename = filepath.Base(filename)
	}
	return log.entry.WithField("file", fmt.Sprintf("%s:%d", filename, line))
}

func (log logger) With(key string, value interface{}) Logger {
	return logger{log.entry.WithField(key, value)}
}

func (log logger) Debug(args ...interface{}) {
	log.withFileField().Debug(args...)
}

func (log logger) Debugln(args ...interface{}) {
	log.withFileField().Debugln(args...)
}

func (log logger) Debugf(format string, args ...interface{}) {
	log.withFileField().Debugf(format, args...)
}

func (log logger) Info(args ...interface{}) {
	log.withFileField().Info(args...)
}

func (log logger) Infoln(args ...interface{}) {
	log.withFileField().Infoln(args...)
}

func (log logger) Infof(format string, args ...interface{}) {
	log.withFileField().Infof(format, args...)
}

func (log logger) Warn(args ...interface{}) {
	log.withFileField().Warn(args...)
}

func (log logger) Warnln(args ...interface{}) {
	log.withFileField().Warnln(args...)
}

func (log logger) Warnf(format string, args ...interface{}) {
	log.withFileField().Warnf(format, args...)
}

func (log logger) Error(args ...interface{}) {
	log.withFileField().Error(args...)
}

func (log logger) Errorln(args ...interface{}) {
	log.withFileField().Errorln(args...)
}

func (log logger) Errorf(format string, args ...interface{}) {
	log.withFileField().Errorf(format, args...)
}

func (log logger) Fatal(args ...interface{}) {
	log.withFileField().Fatal(args...)
}

func (log logger) Fatalln(args ...interface{}) {
	log.withFileField().Fatalln(args...)
}

func (log logger) Fatalf(format string, args ...interface{}) {
	log.withFileField().Fatalf(format, args...)
}

func (log logger) SetLevel(level string) error {
	lev, err := logrus.ParseLevel(level)
	if err != nil {
		return err
	}

	log.entry.Logger.SetLevel(lev)
	return nil
}

// GetLogger method return the root logger of the logger service
func GetLogger() *logrus.Logger {
	return rootLogger
}

func getLogFormat(format string) logrus.Formatter {
	switch format {
	case "text":
		return &logrus.TextFormatter{}
	case "json":
		return &logrus.JSONFormatter{}
	default:
		return &logrus.TextFormatter{}
	}
}

// Debug method log debug level args
func Debug(args ...interface{}) {
	baseLogger.withFileField().Debug(args...)
}

// Debugln method log debug level args
func Debugln(args ...interface{}) {
	baseLogger.withFileField().Debugln(args...)
}

// Debugf method log debug level message with format string
func Debugf(format string, args ...interface{}) {
	baseLogger.withFileField().Debugf(format, args...)
}

// Info method log info level args
func Info(args ...interface{}) {
	baseLogger.withFileField().Info(args...)
}

// Infoln method log info level args
func Infoln(args ...interface{}) {
	baseLogger.withFileField().Infoln(args...)
}

// Infof method log info level message with format string
func Infof(format string, args ...interface{}) {
	baseLogger.withFileField().Infof(format, args...)
}

// Warn method log warn args
func Warn(args ...interface{}) {
	baseLogger.withFileField().Warn(args...)
}

// Warnln method log warn args
func Warnln(args ...interface{}) {
	baseLogger.withFileField().Warnln(args...)
}

// Warnf method log warn level message with format string
func Warnf(format string, args ...interface{}) {
	baseLogger.withFileField().Warnf(format, args...)
}

// Error method log error args
func Error(args ...interface{}) {
	baseLogger.withFileField().Error(args...)
}

// Errorln method log error args
func Errorln(args ...interface{}) {
	baseLogger.withFileField().Errorln(args...)
}

// Errorf method log error level message with format string
func Errorf(format string, args ...interface{}) {
	baseLogger.withFileField().Errorf(format, args...)
}

// Fatal method log fatal info
func Fatal(args ...interface{}) {
	baseLogger.withFileField().Fatal(args...)
}

// Fatalln method log fatal info
func Fatalln(args ...interface{}) {
	baseLogger.withFileField().Fatalln(args...)
}

// Fatalf method log fatal level message with format string
func Fatalf(format string, args ...interface{}) {
	baseLogger.withFileField().Fatalf(format, args...)
}

// WithField method add field to logger
func WithField(key string, value interface{}) Logger {
	return baseLogger.With(key, value)
}
