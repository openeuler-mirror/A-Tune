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
 * Create: 2020-07-23
 */

package tuning

import (
	"fmt"
	"gopkg.in/yaml.v2"
	"os"
	"path/filepath"

	"github.com/newm4n/grool/builder"
	gContext "github.com/newm4n/grool/context"
	"github.com/newm4n/grool/engine"
	"github.com/newm4n/grool/model"
	"github.com/newm4n/grool/pkg"
	
	PB "gitee.com/openeuler/A-Tune/api/profile"
	"gitee.com/openeuler/A-Tune/common/config"
	"gitee.com/openeuler/A-Tune/common/log"
	"gitee.com/openeuler/A-Tune/common/project"
	"gitee.com/openeuler/A-Tune/common/utils"
)

// TuningData : the struct which store the collection data
type TuningData struct {
	CacheMissRatio    float64 `mapstructure:"PERF.STAT.CACHE-MISS-RATIO"`
	DtlbLoadMissRatio float64 `mapstructure:"PERF.STAT.DTLB-LOAD-MISS-RATIO"`
	Ipc               float64 `mapstructure:"PERF.STAT.IPC"`
	ItlbLoadMissRatio float64 `mapstructure:"PERF.STAT.ITLB-LOAD-MISS-RATIO"`
	Migrations        float64 `mapstructure:"PERF.STAT.migrations"`
	MemoryBound       float64 `mapstructure:"MEMORY-BOUND"`
	Mpki              float64 `mapstructure:"PERF.STAT.MPKI"`
	Sbpc              float64 `mapstructure:"PERF.STAT.SBPC"`
	Sbpi              float64 `mapstructure:"PERF.STAT.SBPI"`
	StorageUtil       float64 `mapstructure:"STORAGE.STAT.util"`
	TotalUtil         float64 `mapstructure:"MEM.BANDWIDTH.Total_Util"`
	AquSz             float64 `mapstructure:"STORAGE.STAT.aqu-sz"`
	Cswchs            float64 `mapstructure:"SYS.TASKS.cswchs"`
	Cutil             float64 `mapstructure:"CPU.STAT.cutil"`
	Errs              float64 `mapstructure:"NET.STAT.errs"`
	Ifutil            float64 `mapstructure:"NET.STAT.ifutil"`
	IoBi              float64 `mapstructure:"MEM.VMSTAT.io.bi"`
	IoBo              float64 `mapstructure:"MEM.VMSTAT.io.bo"`
	Iowait            float64 `mapstructure:"CPU.STAT.iowait"`
	Irq               float64 `mapstructure:"CPU.STAT.irq"`
	Ldavg1            float64 `mapstructure:"SYS.LDAVG.ldavg-1"`
	Ldavg5            float64 `mapstructure:"SYS.LDAVG.ldavg-5"`
	MemorySwpt        float64 `mapstructure:"MEM.VMSTAT.memory.swpt"`
	Nice              float64 `mapstructure:"CPU.STAT.nice"`
	PlistSz           float64 `mapstructure:"SYS.LDAVG.plist-sz"`
	Procs             float64 `mapstructure:"SYS.TASKS.procs"`
	ProcsB            float64 `mapstructure:"MEM.VMSTAT.procs.b"`
	ProcsR            float64 `mapstructure:"MEM.STAT.procs.r"`
	RMbs              float64 `mapstructure:"STORAGE.STAT.rMBs"`
	WMbs              float64 `mapstructure:"STORAGE.STAT.wMBs"`
	RAwait            float64 `mapstructure:"STORAGE.STAT.r_await"`
	WAwait            float64 `mapstructure:"STORAGE.STAT.w_await"`
	RareqSz           float64 `mapstructure:"STORAGE.STAT.rareq-sz"`
	WareqSz           float64 `mapstructure:"STORAGE.STAT.wareq-sz"`
	Rrqm              float64 `mapstructure:"STORAGE.STAT.rrqm"`
	Wrqm              float64 `mapstructure:"STORAGE.STAT.wrqm"`
	Rs                float64 `mapstructure:"STORAGE.STAT.rs"`
	Ws                float64 `mapstructure:"STORAGE.STAT.ws"`
	RunqSz            float64 `mapstructure:"SYS.LDAVG.runq-sz"`
	RxKbs             float64 `mapstructure:"NET.STAT.rxkBs"`
	RxPcks            float64 `mapstructure:"NET.STAT.rxpcks"`
	TxKbs             float64 `mapstructure:"NET.STAT.txkBs"`
	TxPcks            float64 `mapstructure:"NET.STAT.txpcks"`
	Soft              float64 `mapstructure:"CPU.STAT.soft"`
	Steal             float64 `mapstructure:"CPU.STAT.steal"`
	Sys               float64 `mapstructure:"CPU.STAT.sys"`
	SystemCs          float64 `mapstructure:"MEM.VMSTAT.system.cs"`
	SystemIn          float64 `mapstructure:"MEM.VMSTAT.system.in"`
	User              float64 `mapstructure:"CPU.STAT.usr"`
	Util              float64 `mapstructure:"CPU.STAT.util"`
	UtilCpu           float64 `mapstructure:"MEM.VMSTAT.util.cpu"`
	UtilSwap          float64 `mapstructure:"MEM.VMSTAT.util.swap"`
}

// TuningFile used to store the object which match the tuning rule
type TuningFile struct {
	prjs   *[]project.YamlPrjSvr `yaml:"-"`
	PrjSrv *project.YamlPrjSvr
	ch     chan *PB.AckCheck
}

// NewTuningFile method create a TuningFile instance
func NewTuningFile(workloadType string, ch chan *PB.AckCheck) *TuningFile {
	tuningFile := new(TuningFile)
	tuningFile.PrjSrv = new(project.YamlPrjSvr)
	tuningFile.PrjSrv.Project = workloadType
	tuningFile.PrjSrv.Maxiterations = 20

	prjs := make([]project.YamlPrjSvr, 0)
	tuningFile.prjs = &prjs
	tuningFile.ch = ch
	return tuningFile
}

// Load method load the yaml come with the atuned
func (t TuningFile) Load() error {
	err := filepath.Walk(config.DefaultTuningPath, func(path string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			prj := new(project.YamlPrjSvr)
			if err := utils.ParseFile(path, "yaml", &prj); err != nil {
				return fmt.Errorf("load %s failed, err: %v", path, err)
			}
			log.Infof("project:%s load %s success", prj.Project, path)
			*t.prjs = append(*t.prjs, *prj)
		}
		return nil
	})

	if err != nil {
		return err
	}
	return nil
}

// AppendObject add the tuning object which match the rules
func (t *TuningFile) AppendObject(object string) {
	log.Infof("append %s object to dest tuning file", object)
	var exist bool = false
	for _, prj := range *t.prjs {
		for _, obj := range prj.Object {
			if obj.Name != object {
				continue
			}
			exist = true
			t.PrjSrv.Object = append(t.PrjSrv.Object, obj)
			break
		}
		if exist {
			log.Infof("find object: %s", object)
			t.ch <- &PB.AckCheck{Name: fmt.Sprintf("   appending parameter: %s", object)}
			return
		}
	}
	t.ch <- &PB.AckCheck{Name: fmt.Sprintf("   appending parameter: %s, but not founded", object)}
}

// Save method save the project to file
func (t *TuningFile) Save(dstFile string) error {
	data, err := yaml.Marshal(t.PrjSrv)
	if err != nil {
		return err
	}
	log.Debugf("data content: %s", string(data))
	err = utils.WriteFile(dstFile, string(data), utils.FilePerm,
		os.O_WRONLY|os.O_CREATE|os.O_TRUNC)
	if err != nil {
		log.Error(err)
		return err
	}
	return nil

}

// RuleEngine: holds context and knowledge base
type RuleEngine struct {
	DataContext   *gContext.DataContext
	Grool         *engine.Grool
	KnowledgeBase *model.KnowledgeBase
}

// NewRuleEngine: builds and returns a new instance of rule engine from source file
func NewRuleEngine(srcFile string) *RuleEngine {
	ruleEngine := new(RuleEngine)

	ruleEngine.KnowledgeBase = model.NewKnowledgeBase()
	ruleBuilder := builder.NewRuleBuilder(ruleEngine.KnowledgeBase)
	fileRes := pkg.NewFileResource(srcFile)
	err := ruleBuilder.BuildRuleFromResource(fileRes)
	if err != nil {
		return nil
	}

	ruleEngine.DataContext = gContext.NewDataContext()
	ruleEngine.Grool = engine.NewGroolEngine()

	return ruleEngine
}

// AddContext: add context to the rule engine
func (r *RuleEngine) AddContext(key string, obj interface{}) error {
	err := r.DataContext.Add(key, obj)
	if err != nil {
		return err
	}

	return nil
}

// Execute: rule engine start to execute based on context and knowledge base
func (r *RuleEngine) Execute() error {
	if r.Grool == nil {
		return fmt.Errorf("grool engine is nill")
	}

	return r.Grool.Execute(r.DataContext, r.KnowledgeBase)
}
