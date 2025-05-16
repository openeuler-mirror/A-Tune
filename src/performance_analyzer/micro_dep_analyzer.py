from .base_analyzer import BaseAnalyzer
import logging
class MicroDepAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt_dict = {
            "frontend_bound": "TopDown中的前端瓶颈（frontend bound）",
            "bad_spec": "TopDown中的预测失败瓶颈（bad speculation）",
            "retiring": "TopDown中的指令完成（retiring）",
            "backend_bound": "TopDown中的后端瓶颈（backend bound）",
            "frontend_latency_bound": "TopDown中的前端瓶颈下的前端延时瓶颈（frontend latency bound）",
            "frontend_bandwidth_bound": "TopDown中的前端瓶颈下的前端带宽瓶颈（frontend bandwidth bound）",
            "bs_mispred": "TopDown中的预测失败瓶颈中的分支预测失败瓶颈（bad speculation branch misprediction）",
            "bs_mclear": "TopDown中的预测失败瓶颈中的流水线清空瓶颈（bad speculation machine clears）",
            "core_bound": "TopDown中的后端瓶颈中的后端执行瓶颈（core bound）",
            "mem_bound": "TopDown中的后端瓶颈中的后端内存子系统瓶颈（memory bound）",
            "core_fsu_bound": "TopDown中的后端执行瓶颈中的浮点/向量计算瓶颈（core fsu bound）",
            "core_other_bound": "TopDown中的后端执行瓶颈中的后端其他执行瓶颈（core other bound）",
            "mem_l1_bound": "TopDown中的后端内存子系统瓶颈中的读取L1 cache造成的指令执行瓶颈（不包含L2/L3）",
            "mem_l2_bound": "TopDown中的后端内存子系统瓶颈中的读取L2 cache造成的指令执行瓶颈（不包含L1/L3）",
            "mem_l3_dram_bound": "TopDown中的后端内存子系统瓶颈中的读取L3以及内存造成的指令执行瓶颈（不包含L1/L2）",
            "mem_store_bound": "TopDown中的后端内存子系统瓶颈中的内存写瓶颈（memory store bound）",
            "context_switches": "上下文切换次数（context-switches）",
            "cpu_migrations": "进程在不同CPU核之间的迁移次数（cpu-migrations）",
            "page_faults": "缺页异常次数（page-faults）",
            "l1i_missrate": "L1指令miss rate",
            "l1d_missrate": "L1数据miss rate",
            "l2i_missrate": "L2指令miss rate",
            "l2d_missrate": "L2数据miss rate",
            "l1i_mpki": "L1指令每千条指令中miss次数",
            "l1d_mpki": "L1数据每千条指令中miss次数",
            "l2i_mpki": "L2指令每千条指令中miss次数",
            "l2d_mpki": "L2数据每千条指令中miss次数",
            "branch_missrate": "分支预测失败率（branch missrate）",
            "alu_isq_stall": "算术逻辑单元全部被占用导致的执行瓶颈",
            "lsu_isq_stall": "访存逻辑单元全部被占用导致的执行瓶颈",
            "fsu_isq_stall": "浮点单元全部被占用导致的执行瓶颈",
            "l1i_tlb_missrate": "L1指令快表miss rate（l1i_tlb_missrate）",
            "l1d_tlb_missrate": "L1数据快表miss rate（l1d_tlb_missrate）",
            "l2i_tlb_missrate": "L2指令快表miss rate（l2i_tlb_missrate）",
            "l2d_tlb_missrate": "L2数据快表miss rate（l2d_tlb_missrate）",
            "itlb_walk_rate": "指令页表缓存未命中时触发页表遍历的频率（itlb_walk_rate）",
            "dtlb_walk_rate": "数据页表缓存未命中时触发页表遍历的频率（dtlb_walk_rate）",
            "l1i_tlb_mpki": "L1指令TLB每千条指令中miss次数",
            "l1d_tlb_mpki": "L1数据TLB每千条指令中miss次数",
            "l2i_tlb_mpki": "L2指令TLB每千条指令中miss次数",
            "l2d_tlb_mpki": "L2数据TLB每千条指令中miss次数",
            "itlb_walk_mpki": "指令TLB每千条指令中到页表查找次数",
            "dtlb_walk_mpki": "指令TLB每千条指令中到页表查找次数",
            "div_stall": "除法指令在关键路径导致的执行瓶颈",
        }
    def analyze(self) -> str:
        report = "基于采集的系统指标, 微架构初步的性能分析报告如下: \n"
        processed_data_dict = {}
        for k, v in self.data.items():
            if k in self.prompt_dict.keys():
                processed_data_dict[self.prompt_dict[k]] = v
            else:
                logging.warning("Cannot find prompt for item {k}")
        report +=  f"系统微架构状态是{processed_data_dict}\n"
        return report

    def generate_report(
        self,
        micro_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        report_prompt = f"""
        以下内容是linux系统中应用微架构相关的性能信息:
        {micro_report}
        信息中所涉及到的数据准确无误,真实可信。

        # OBJECTIVE #
        请根据上述信息,分析系统应用微架构的性能状况。
        要求：
        1.答案中不要包含任何优化建议。
        2.答案中尽可能保留信息中真实有效的数据。
        3.不要遗漏任何值得分析的信息。

        # STYLE #
        你是一个专业的系统运维专家,你的回答应该逻辑严谨、表述客观、简洁易懂、条理清晰，让你的回答真实可信

        # Tone #
        你应该尽可能秉承严肃、认真、严谨的态度

        # AUDIENCE #
        你的答案将会是其他系统运维专家的重要参考意见，请尽可能提供真实有用的信息，不要胡编乱造。

        # RESPONSE FORMAT #
        回答以"应用微架构分析如下:"开头，然后另起一行逐条分析。
        如果有多条分析结论，请用数字编号分点作答。
        
        """
        return self.ask_llm(report_prompt) + "\n"
