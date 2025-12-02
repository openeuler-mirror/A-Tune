from .base_analyzer import BaseAnalyzer
from src.utils.common import translate
import logging
class MicroDepAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt_dict = {
            "frontend_bound": translate("TopDown中的前端瓶颈（frontend bound）", "Frontend Bound in Top-Down"),
            "bad_spec": translate("TopDown中的预测失败瓶颈（bad speculation）", "Bad Speculation in Top-Down"),
            "retiring": translate("TopDown中的指令完成（retiring）", "Retiring in Top-Down"),
            "backend_bound": translate("TopDown中的后端瓶颈（backend bound）", "Backend Bound in Top-Down"),
            "frontend_latency_bound": translate("TopDown中的前端瓶颈下的前端延时瓶颈（frontend latency bound）", "Frontend Latency Bound"),
            "frontend_bandwidth_bound": translate("TopDown中的前端瓶颈下的前端带宽瓶颈（frontend bandwidth bound）", "Frontend Bandwidth Bound"),
            "bs_mispred": translate("TopDown中的预测失败瓶颈中的分支预测失败瓶颈（bad speculation branch misprediction）", "Branch Misprediction"),
            "bs_mclear": translate("TopDown中的预测失败瓶颈中的流水线清空瓶颈（bad speculation machine clears）", "Machine Clears"),
            "core_bound": translate("TopDown中的后端瓶颈中的后端执行瓶颈（core bound）", "Core Bound"),
            "mem_bound": translate("TopDown中的后端瓶颈中的后端内存子系统瓶颈（memory bound）", "Memory Bound"),
            "core_fsu_bound": translate("TopDown中的后端执行瓶颈中的浮点/向量计算瓶颈（core fsu bound）", "Floating Point/Vector Bound"),
            "core_other_bound": translate("TopDown中的后端执行瓶颈中的后端其他执行瓶颈（core other bound）", "Other Core Execution Bound"),
            "mem_l1_bound": translate("TopDown中的后端内存子系统瓶颈中的读取L1 cache造成的指令执行瓶颈（不包含L2/L3）", "L1 Cache Bound (excl. L2/L3)"),
            "mem_l2_bound": translate("TopDown中的后端内存子系统瓶颈中的读取L2 cache造成的指令执行瓶颈（不包含L1/L3）", "L2 Cache Bound (excl. L1/L3)"),
            "mem_l3_dram_bound": translate("TopDown中的后端内存子系统瓶颈中的读取L3以及内存造成的指令执行瓶颈（不包含L1/L2）", "L3/DRAM Bound (excl. L1/L2)"),
            "mem_store_bound": translate("TopDown中的后端内存子系统瓶颈中的内存写瓶颈（memory store bound）", "Memory Store Bound"),
            "context_switches": translate("上下文切换次数（context-switches）", "Context Switches"),
            "cpu_migrations": translate("进程在不同CPU核之间的迁移次数（cpu-migrations）", "CPU Migrations"),
            "page_faults": translate("缺页异常次数（page-faults）", "Page Faults"),
            "l1i_missrate": translate("L1指令miss rate", "L1 Instruction Miss Rate"),
            "l1d_missrate": translate("L1数据miss rate", "L1 Data Miss Rate"),
            "l2i_missrate": translate("L2指令miss rate", "L2 Instruction Miss Rate"),
            "l2d_missrate": translate("L2数据miss rate", "L2 Data Miss Rate"),
            "l1i_mpki": translate("L1指令每千条指令中miss次数", "L1 Instruction Misses Per Kilo Instructions"),
            "l1d_mpki": translate("L1数据每千条指令中miss次数", "L1 Data Misses Per Kilo Instructions"),
            "l2i_mpki": translate("L2指令每千条指令中miss次数", "L2 Instruction Misses Per Kilo Instructions"),
            "l2d_mpki": translate("L2数据每千条指令中miss次数", "L2 Data Misses Per Kilo Instructions"),
            "branch_missrate": translate("分支预测失败率（branch missrate）", "Branch Miss Rate"),
            "alu_isq_stall": translate("算术逻辑单元全部被占用导致的执行瓶颈", "ALU Execution Stall"),
            "lsu_isq_stall": translate("访存逻辑单元全部被占用导致的执行瓶颈", "Load/Store Unit Stall"),
            "fsu_isq_stall": translate("浮点单元全部被占用导致的执行瓶颈", "Floating Point Unit Stall"),
            "l1i_tlb_missrate": translate("L1指令快表miss rate（l1i_tlb_missrate）", "L1 Instruction TLB Miss Rate"),
            "l1d_tlb_missrate": translate("L1数据快表miss rate（l1d_tlb_missrate）", "L1 Data TLB Miss Rate"),
            "l2i_tlb_missrate": translate("L2指令快表miss rate（l2i_tlb_missrate）", "L2 Instruction TLB Miss Rate"),
            "l2d_tlb_missrate": translate("L2数据快表miss rate（l2d_tlb_missrate）", "L2 Data TLB Miss Rate"),
            "itlb_walk_rate": translate("指令页表缓存未命中时触发页表遍历的频率（itlb_walk_rate）", "Instruction TLB Walk Rate"),
            "dtlb_walk_rate": translate("数据页表缓存未命中时触发页表遍历的频率（dtlb_walk_rate）", "Data TLB Walk Rate"),
            "l1i_tlb_mpki": translate("L1指令TLB每千条指令中miss次数", "L1 Instruction TLB MPKI"),
            "l1d_tlb_mpki": translate("L1数据TLB每千条指令中miss次数", "L1 Data TLB MPKI"),
            "l2i_tlb_mpki": translate("L2指令TLB每千条指令中miss次数", "L2 Instruction TLB MPKI"),
            "l2d_tlb_mpki": translate("L2数据TLB每千条指令中miss次数", "L2 Data TLB MPKI"),
            "itlb_walk_mpki": translate("指令TLB每千条指令中到页表查找次数", "Instruction TLB Walk MPKI"),
            "dtlb_walk_mpki": translate("数据TLB每千条指令中到页表查找次数", "Data TLB Walk MPKI"),
            "div_stall": translate("除法指令在关键路径导致的执行瓶颈", "Division Instruction Stall")
        }

    def analyze(self) -> str:
        report = translate("基于采集的系统指标, 微架构初步的性能分析报告如下: \n", 
            "Based on the collected system metrics, the preliminary performance analysis report of the microarchitecture is as follows: \n")
        processed_data_dict = {}
        for k, v in self.data.items():
            if k in self.prompt_dict.keys():
                processed_data_dict[self.prompt_dict[k]] = v
            else:
                logging.warning("Cannot find prompt for item {k}")
        report +=  translate(f"系统微架构状态是{processed_data_dict}\n", f"The system microarchitecture status is {processed_data_dict}\n")
        return report

    def generate_report(
        self,
        micro_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        report_prompt = translate(
            f"""
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
        """,
        f"""
The following content contains performance information related to the application microarchitecture in a Linux system:
{micro_report}
The data mentioned in the information is accurate and reliable.

# OBJECTIVE #
Please analyze the performance status of the system's application microarchitecture based on the above information.
Requirements:
1. Do not include any optimization suggestions in your answer.
2. Retain as much of the real and valid data from the information as possible.
3. Do not omit any information that is worth analyzing.

# STYLE #
You are a professional system operations expert. 
Your response should be logically rigorous, objective, concise, and easy to understand, 
with clear and logical organization, making your answer credible.

# TONE #
You should maintain a serious, earnest, and rigorous attitude.

# AUDIENCE #
Your answer will serve as an important reference for other system operations experts. Please provide as much real and useful information as possible, and do not fabricate any information.

# RESPONSE FORMAT #
Begin your answer with "application microarchitecture analysis is as follows:" and then start a new line to analyze each point separately.
If there are multiple analysis conclusions, please number them and list them separately.
        """)
        return self.ask_llm(report_prompt) + "\n"
