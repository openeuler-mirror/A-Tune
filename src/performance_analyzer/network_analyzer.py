from .base_analyzer import BaseAnalyzer
from src.utils.common import translate

class NetworkAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def analyze(self) -> str:
        report = translate("基于采集的系统指标, 网络初步的性能分析如下：\n",
            "Based on the collected system metrics, the preliminary performance analysis of the network is as follows:\n")
        listenOverflows, fulldocookies, fulldrop, network_adapter = (
            self.data.get("listenOverflows", 0), 
            self.data.get("fulldocookies", 0),
            self.data.get("fulldrop", 0),
            self.data.get("network_adapter_metrics", "")
        )
        report += self.listenOverflows_analysis(listenOverflows)
        report += self.fulldocookies_analysis(fulldocookies)
        report += self.fulldrop_analysis(fulldrop)
        report += self.network_adapter_analysis(network_adapter)
        return report
    
    def listenOverflows_analysis(
        self,
        listenOverflows: float
    ) -> str:
        return self.generate_report_line(listenOverflows == 1, translate("系统存在因为监听队列回滚而丢弃TCP连接的现象。这通常表明系统无法及时处理传入的连接请求, 导致连接被系统自动丢弃",
            "The system is experiencing TCP connection drops due to listener queue rollbacks. This usually indicates that the system is unable to process incoming connection requests in a timely manner, causing the connections to be automatically dropped by the system."))

    def fulldrop_analysis(
        self,
        fulldrop: float
    ) -> str:
        return self.generate_report_line(fulldrop == 1, translate("系统存在因为TCP请求队列满了而丢弃新的连接请求的现象。这通常表明系统无法及时处理传入的连接请求, 导致内核自动丢弃这些请求",
            "The system is experiencing new connection requests being dropped due to a full TCP request queue. This usually indicates that the system is unable to process incoming connection requests in a timely manner, causing the kernel to automatically discard these requests."))

    def fulldocookies_analysis(
        self,
        fulldocookies: float
    ) -> str:
        return self.generate_report_line(fulldocookies == 1, translate("系统存在因为TCP请求队列满了而发送SYN COOKIE的现象。这通常表明系统无法及时处理传入的连接请求, 导致内核自动采取措施来处理这些请求, 例如发送SYN COOKIE",
            "The system is experiencing SYN cookies being sent due to a full TCP request queue. This usually indicates that the system is unable to process incoming connection requests in a timely manner, causing the kernel to automatically take measures to handle these requests, such as sending SYN cookies."))

    def network_adapter_analysis(
        self,
        network_adapter: str
    ) -> str:
        network_adapter_prompt = translate(
            f"""
# CONTEXT # 
当前有linux系统网卡的数据,性能指标是在linux系统中执行 netstat -i 获得的输出，内容如下：
{network_adapter}

# OBJECTIVE #
请根据这些性能指标,生成一份逻辑清晰、条理清楚的系统网卡的性能总结报告。
要求：
1.答案中只分析可能对系统性能产生影响的指标数据。
2.答案中不要包含任何优化建议。
3.答案中尽可能保留信息中真实有效的数据。
4.答案不超过200字。

# STYLE #
你是一个专业的系统运维专家,你的回答应该逻辑严谨、表述客观、简洁易懂、条理清晰，让你的回答真实可信

# Tone #
你应该尽可能秉承严肃、认真、严谨的态度

# AUDIENCE #
你的答案将会是其他系统运维专家的重要参考意见，请尽可能提供真实有用的信息，不要胡编乱造。

# RESPONSE FORMAT #
如果有多条分析结论，请用数字编号分点作答。
        """,
        f"""
# CONTEXT #
There is data on the network adapter of a Linux system. The performance metrics were obtained by executing the command `netstat -i` in the Linux system, and the output is as follows:
{network_adapter}

# OBJECTIVE #
Please generate a clear and logical performance summary report for the system's network adapter based on these performance metrics.
Requirements:
1. Only analyze the metric data that may have an impact on system performance.
2. Do not include any optimization suggestions in your answer.
3. Retain as much of the original and valid data as possible in your answer.
4. The answer should not exceed 200 words.

# STYLE #
You are a professional system operations expert. Your response should be logically rigorous, objective, concise, and easy to understand, with a clear structure, making your answer credible and trustworthy.

# TONE #
You should maintain a serious, earnest, and rigorous attitude.

# AUDIENCE #
Your answer will serve as an important reference for other system operations experts. Please provide as much real and useful information as possible, and do not fabricate any information.

# RESPONSE FORMAT #
If there are multiple analysis conclusions, please list them in numbered points.
""")
        return self.ask_llm(network_adapter_prompt)
    
    def generate_report(
        self,
        network_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        report_prompt = translate(
            f"""
以下内容是linux系统中网络传输相关的性能信息:
{network_report}
信息中所涉及到的数据准确无误,真实可信。

# OBJECTIVE #
请根据上述信息,分析系统网络传输的性能状况。
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
回答以"网络分析如下:"开头，然后另起一行逐条分析。
如果有多条分析结论，请用数字编号分点作答。   
        """,
        f"""
The following content contains performance information related to the network in a Linux system:
{network_report}

The data mentioned in the information is accurate and reliable.

# OBJECTIVE #
Please analyze the performance status of the system's network based on the above information.
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
Begin your answer with "network analysis is as follows:" and then start a new line to analyze each point separately.
If there are multiple analysis conclusions, please number them and list them separately.
        """)
        return self.ask_llm(report_prompt) + "\n"