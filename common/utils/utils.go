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

package utils

import (
	PB "atune/api/profile"
	"bufio"
	"encoding/xml"
	"fmt"
	"gopkg.in/yaml.v2"
	"io"
	"io/ioutil"
	"math/rand"
	"net"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"plugin"
	"regexp"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/urfave/cli"
)

// disk filename
const (
	diskFilename = "diskstats"
)

// the number of args
const (
	ConstExactArgs = iota
	ConstMinArgs
)

// Status of AckCheck
const (
	SUCCESS = "SUCCESS"
	FAILD   = "FAILED"
	WARNING = "WARNING"
	ERROR   = "ERROR"
	INFO    = "INFO"
	SUGGEST = "SUGGEST"
	UNKNOWN = "UNKNOWN"
)

// config for waiting rest service
const (
	period  = 2
	timeout = 120
)

// CheckArgs method check command args num
func CheckArgs(context *cli.Context, expected, checkType int) error {
	var err error
	cmdName := context.Command.Name
	switch checkType {
	case ConstExactArgs:
		if context.NArg() != expected {
			err = fmt.Errorf("%s: %q requires exactly %d argument(s)", os.Args[0], cmdName, expected)
		}
	case ConstMinArgs:
		if context.NArg() < expected {
			err = fmt.Errorf("%s: %q requires a minimum of %d argument(s)", os.Args[0], cmdName, expected)
		}
	}

	if err != nil {
		fmt.Printf("Incorrect Usage.\n\n")
		_ = cli.ShowCommandHelp(context, cmdName)
		return err
	}
	return nil
}

// Fatal method exit the application
func Fatal(err error) {
	fmt.Fprintln(os.Stderr, err)
	os.Exit(1)
}

// Random method return a random uint value, the source is the timestamp
func Random() uint64 {
	rand.Seed(time.Now().Unix())
	return rand.Uint64()
}

// LoadPlugins method load the plugin service
func LoadPlugins(path string) error {
	abs, err := filepath.Abs(path)
	if err != nil {
		return err
	}

	pattern := filepath.Join(abs, fmt.Sprintf("*"))
	libs, err := filepath.Glob(pattern)
	if err != nil {
		return err
	}

	for _, lib := range libs {
		if _, err := plugin.Open(lib); err != nil {
			fmt.Printf("load %s failed : err:%s\n", lib, err)
			continue
		}
	}

	return nil
}

// PathExist method check path if exist or not
func PathExist(path string) (bool, error) {
	_, err := os.Stat(path)
	if err == nil {
		return true, nil
	}
	if os.IsNotExist(err) {
		return false, nil
	}
	return false, err
}

// PathIsDir method check path is dir or not
func PathIsDir(path string) (bool, error) {
	info, err := os.Stat(path)
	if err == nil {
		return info.IsDir(), nil
	}
	if os.IsNotExist(err) {
		return false, fmt.Errorf("path %s doens't exist", path)
	}

	return false, err
}

// Print method print AckCheck to stdout
func Print(ackCheck *PB.AckCheck) {
	fc := 32
	if ackCheck.Status == FAILD {
		fc = 31
	} else if ackCheck.Status == WARNING {
		fc = 33
	} else if ackCheck.Status == SUGGEST {
		fc = 36
	} else if ackCheck.Status == INFO {
		fc = 37
	}
	if ackCheck.Description == "" {
		fmt.Printf("%c[1;40;%dm %s %c[0m\n", 0x1B, fc, ackCheck.GetName(), 0x1B)
	} else {
		description := strings.Replace(ackCheck.Description, "\n", ",", -1)
		fmt.Printf(" [%c[1;40;%dm %-7s] %-40s %-50s %c[0m\n", 0x1B, fc, ackCheck.Status, ackCheck.Name, description, 0x1B)
	}
}

// PrintStr method print string to stdout
func PrintStr(description string) {
	fmt.Printf("%c[1;40;%dm %s %c[0m\n", 0x1B, 32, description, 0x1B)
}

// IsHost method check whether it is a physical machine or a virtual machine
func IsHost() bool {
	cmd := exec.Command("virt-what")
	_, err := cmd.Output()

	return err == nil
}

// CreateNamedPipe method create a named pip to communicate
func CreateNamedPipe() (string, error) {
	npipe := strconv.FormatInt(time.Now().Unix(), 10)
	npipe = path.Join("/run", npipe)

	exist, err := PathExist(npipe)
	if err != nil {
		return "", err
	}
	if exist {
		_ = os.Remove(npipe)
	}

	err = syscall.Mkfifo(npipe, 0666)
	if err != nil {
		return "", err
	}
	return npipe, nil
}

// CopyFile method copy file from srcName to dstname
func CopyFile(dstName string, srcName string) error {
	src, err := os.Open(srcName)
	if err != nil {
		return err
	}
	defer src.Close()

	dst, err := os.OpenFile(dstName, os.O_WRONLY|os.O_CREATE, 0640)
	if err != nil {
		return err
	}
	defer dst.Close()

	if _, err := io.Copy(dst, src); err != nil {
		return err
	}
	return nil
}

// RemoveDuplicateElement method remove duplicate elem from slice
func RemoveDuplicateElement(message []string) []string {
	result := make([]string, 0, len(message))
	messageMap := map[string]struct{}{}
	for _, item := range message {
		if _, ok := messageMap[item]; !ok {
			messageMap[item] = struct{}{}
			result = append(result, item)
		}
	}
	return result
}

// WaitForPyservice method waiting for pyEngine service start success
func WaitForPyservice(address string, port string) error {
	ticker := time.NewTicker(time.Second * period)
	timeout := time.After(time.Second * timeout)
	addr := address + ":" + port
	for {
		select {
		case <-ticker.C:
			_, err := net.Dial("tcp", addr)
			if err != nil {
				continue
			}
			return nil
		case <-timeout:
			return fmt.Errorf("waiting for pyservice timeout")
		}
	}
}

// InterfaceByName method check the interface state, up or down
// if interface is not exist or down return err, otherwise return nil
func InterfaceByName(name string) error {
	netIntface, err := net.InterfaceByName(name)
	if err != nil {
		return fmt.Errorf("interface %s is not exist", name)
	}
	if netIntface.Flags&net.FlagUp == 0 {
		return fmt.Errorf("interface %s may be down", name)
	}
	return nil
}

// DiskByName method check wether the disk is exist
// if disk is exist return nil, otherwise return error
func DiskByName(disk string) error {
	diskFile := path.Join("/proc", diskFilename)
	file, err := os.Open(diskFile)
	if err != nil {
		return fmt.Errorf("open file %s error: %v", diskFile, err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		parts := strings.Fields(scanner.Text())
		if len(parts) < 4 {
			continue
		}
		if parts[2] == disk {
			return nil
		}
	}

	return fmt.Errorf("disk %s is not exist", disk)
}

// common input string validator
func IsInputStringValid(input string) bool {
	if input != "" {
		if isOk, _ := regexp.MatchString("^[a-zA-Z0-9/._-]*$", input); isOk {
			return isOk
		}
	}
	return false
}

//write or append string to file
func WriteFile(filename string, data string, perm os.FileMode, wrapper int) error {
	f, err := os.OpenFile(filename, wrapper, perm)
	if err != nil {
		return err
	}
	n, err := f.WriteString(data)
	if err == nil && n < len(data) {
		err = io.ErrShortWrite
	}
	if err1 := f.Close(); err == nil {
		err = err1
	}
	return err
}

//parse yaml or xml file
func ParseFile(filePath string, fileFormat string, out interface{}) error {
	exist, err := PathExist(filePath)
	if err != nil {
		return err
	}

	if !exist {
		return fmt.Errorf("%s is not exist", filePath)
	}

	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return err
	}

	switch fileFormat {
	case "yaml":
		if err := yaml.Unmarshal(data, out); err != nil {
			return err
		}
	case "xml":
		if err := xml.Unmarshal(data, out); err != nil {
			return err
		}
	default:
		return fmt.Errorf("this conversion mode of %s is not supported", fileFormat)
	}

	return nil
}

//create dir if the dir is not exist
func CreateDir(dir string, perm os.FileMode) error {
	exist, err := PathExist(dir)
	if err != nil {
		return err
	}
	if !exist {
		if err = os.MkdirAll(dir, perm); err != nil {
			return err
		}
	}
	return nil
}
