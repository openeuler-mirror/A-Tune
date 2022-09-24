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

package utils

import (
	"archive/tar"
	"bufio"
	"compress/gzip"
	"encoding/csv"
	"encoding/xml"
	"fmt"
	"io"
	"io/ioutil"
	"math"
	"net"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"plugin"
	"reflect"
	"regexp"
	"strconv"
	"strings"
	"syscall"
	"time"

	"gopkg.in/yaml.v2"

	"github.com/urfave/cli"

	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/log"
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

// const for function ParseXxx
const (
	DecimalBase = 10
	HexBase     = 16
	Uint64Bits  = 64
)

// ProcDir is path of proc sysfs
var ProcDir = "/proc/"

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

var accurency = 0.0001

// config for waiting rest service
const (
	period  = 2
	timeout = 120
)

//file attribute
const (
	PipeMode    uint32      = 0600
	FilePerm    os.FileMode = 0600
	MaxFileSize int64       = 100 * 1024 * 1024
)

// Rest service host and port
var RestHost = "localhost"
var RestPort = "8383"

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

// LoadPlugins method load the plugin service
func LoadPlugins(path string) error {
	abs, err := filepath.Abs(path)
	if err != nil {
		return err
	}

	pattern := filepath.Join(abs, "*")
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
	fileInfo, err := os.Stat(path)
	if err == nil {
		if !fileInfo.IsDir() && fileInfo.Size() > MaxFileSize {
			return true, fmt.Errorf("the size of %s exceeds"+
				" the maximum value which is %d", fileInfo.Name(), MaxFileSize)
		}
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

	err = syscall.Mkfifo(npipe, PipeMode)
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
func WaitForPyservice() error {
	ticker := time.NewTicker(time.Second * period)
	timeout := time.After(time.Second * timeout)
	addr := RestHost + ":" + RestPort
	for {
		select {
		case <-ticker.C:
			conn, err := net.Dial("tcp", addr)
			if err != nil {
				continue
			}
			conn.Close()
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

// IsInputStringValid: common input string validator
func IsInputStringValid(input string) bool {
	if input != "" {
		if isOk, _ := regexp.MatchString("^[a-zA-Z0-9/._-]*$", input); isOk {
			return isOk
		}
	}
	return false
}

// WriteFile: write or append string to file
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

// ParseFile: parse yaml or xml file
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

// ReadAllFile read all file to string.
func ReadAllFile(path string) string {
	content, err := ioutil.ReadFile(path)
	if err != nil {
		return ""
	}
	return string(content)
}

// ReadCSV read data from test.csv
func ReadCSV(path string) ([][]string, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	lines, err := csv.NewReader(file).ReadAll()
	if err != nil {
		return nil, err
	}

	data := make([][]string, 0)
	for _, line := range lines {
		if len(line) > 0 {
			data = append(data, line)
		}
	}

	return data, nil
}

// CreateCompressFile create a .tar.gz file as target of compress
func CreateCompressFile(path string) (string, error) {
	temp := strings.Split(path, "/")
	compressName := temp[len(temp)-1] + "-" + time.Now().Format("20060101") + ".tar.gz"

	zipFile, _ := os.Create(compressName)
	defer zipFile.Close()

	gzipWrt := gzip.NewWriter(zipFile)
	defer gzipWrt.Close()

	tarWrt := tar.NewWriter(gzipWrt)
	defer tarWrt.Close()

	file, err := os.Open(path)
	if err != nil {
		log.Errorf("Open file error: %v", err)
		os.Remove(compressName)
		return "", err
	}

	err = Compress(file, "", tarWrt)
	if err != nil {
		log.Errorf("Compress error : %v", err)
		os.Remove(compressName)
		return "", err
	}

	absPath, _ := filepath.Abs(compressName)
	return absPath, nil
}

// Compress recursionly compress all files under given path
func Compress(file *os.File, prefix string, tarWrt *tar.Writer) error {
	info, err := file.Stat()
	if err != nil {
		log.Errorf("%v", err)
		return err
	}

	if info.IsDir() {
		if strings.EqualFold(prefix, "") {
			prefix = info.Name()
		} else {
			prefix = prefix + "/" + info.Name()
		}
		subfiles, err := file.Readdir(-1)
		if err != nil {
			log.Errorf("%v", err)
			return err
		}

		for _, subfile := range subfiles {
			f, err := os.Open(file.Name() + "/" + subfile.Name())
			if err != nil {
				log.Errorf("%v", err)
				return err
			}
			err = Compress(f, prefix, tarWrt)
			if err != nil {
				log.Errorf("%v", err)
				return err
			}
		}
	} else {
		header, err := tar.FileInfoHeader(info, "")
		if err != nil {
			return err
		}
		if !strings.EqualFold(prefix, "") {
			header.Name = prefix + "/" + header.Name
		}
		err = tarWrt.WriteHeader(header)
		if err != nil {
			return err
		}
		_, err = io.Copy(tarWrt, file)
		file.Close()
		if err != nil {
			return err
		}
	}
	return nil
}

// Pair: pair of name and score
type Pair struct {
	Name  string
	Score float64
}

// SortedPair: Pairs sorted by score
type SortedPair []Pair

func (p SortedPair) Swap(i, j int) {
	p[i], p[j] = p[j], p[i]
}

func (p SortedPair) Len() int {
	return len(p)
}

func (p SortedPair) Less(i, j int) bool {
	return p[i].Score >= p[j].Score
}

func IsEquals(a, b float64) bool {
	return math.Abs(a-b) < accurency
}

// CalculateBenchMark: parse benchmark string
func CalculateBenchMark(eval string) (float64, error) {
	kvs := strings.Split(eval, "=")
	if len(kvs) != 2 {
		return 0.0, fmt.Errorf("evaluation format error")
	}
	floatEval, err := strconv.ParseFloat(kvs[1], 64)
	if err != nil {
		return 0.0, err
	}

	return floatEval, nil
}

// Mean calculate the average value
func Mean(data []float64) float64 {
	var mean float64 = 0
	for i := 0; i < len(data); i++ {
		mean += (data[i] - mean) / float64(i+1)
	}
	return mean
}

// Variance calculate the variance
func Variance(data []float64) float64 {
	if len(data) <= 0 {
		return 0
	}
	mean := Mean(data)
	var sum float64 = 0
	for i := 0; i < len(data); i++ {
		diff := data[i] - mean
		sum += diff * diff
	}
	return sum / float64(len(data))
}

// StandardDeviation calculate the standard deviation
func StandardDeviation(data []float64) float64 {
	return math.Sqrt(Variance(data))
}

// ChangeFileName: Change file name
func ChangeFileName(dataPath string) (string, string, error) {
	dir, fileName := filepath.Split(dataPath)
	extension := filepath.Ext(dataPath)
	name := strings.TrimSuffix(fileName, extension)
	timestamp := strconv.FormatInt(time.Now().UnixNano()/1e6, 10)
	newFilePath := dir + name + "-" + timestamp + extension
	log.Infof("new file path: %s", newFilePath)
	err := os.Rename(dataPath, newFilePath)
	if err != nil {
		return "", "", err
	}
	return newFilePath, timestamp, nil
}

// GetLogFilePath: Get log file path
func GetLogFilePath(dirPath string) (string, error) {
	dir, err := ioutil.ReadDir(dirPath)
	if err != nil {
		log.Errorf("dir path does not exists")
		return "", err
	}

	for _, file := range dir {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".log") && strings.HasPrefix(file.Name(), "test-") {
			return dirPath + "/" + file.Name(), nil
		}
	}
	return "", fmt.Errorf("cannot find log file")
}

// Check whether the value is in the list
func CheckValueInSlice(value string, strList []string) bool {
	for _, str := range strList {
		if str == value {
			return true
		}
	}
	return false
}

// Divide requires into groups
func DivideToGroups(strs string, groups []string) []string {
	strsArr := strings.Split(strs, ",")
	div := make([]string, len(groups))
	for _, val := range strsArr {
		for ind, group := range groups {
			if strings.Contains(group, val) {
				if div[ind] == "" {
					div[ind] += val
				} else {
					div[ind] += " " + val
				}
				break
			}
		}
	}
	divRes := make([]string, 0)
	for _, val := range div {
		if val != "" {
			divRes = append(divRes, val)
		}
	}
	return divRes
}

func StringArrayToInterface(array []string) []interface{} {
	var goalArray []interface{}
	for _, value := range array {
		goalArray = append(goalArray, value)
	}
	return goalArray
}

func InArray(array []interface{}, element interface{}) bool {
	if element == nil || array == nil {
		return false
	}
	for _, value := range array {
		if reflect.TypeOf(value).Kind() == reflect.TypeOf(element).Kind() {
			if value == element {
				return true
			}
		}
	}
	return false
}
