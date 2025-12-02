from src.performance_analyzer.base_analyzer import BaseAnalyzer
from src.utils.common import translate


class AppAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def analyze(self) -> str:
        if not self.data:
            return translate(f"当前系统没有运行{self.app}应用，无需分析性能。\n",
            f"The current system is not running the {self.app} application; there is no need to analyze performance.\n")
        
        report = translate(f"基于采集的系统指标, {self.app}初步的性能分析如下:\n",
        f"Based on the collected system metrics, the preliminary performance analysis of {self.app} is as follows:\n")
        for cmd, result in self.data.items():
            profile_prompt = translate(
                f"""
# CONTEXT # 
以下内容是linux命令<{cmd}>的输出：
{result}

# OBJECTIVE #
请根据上述信息,简要分析{self.app}应用的性能状况。
要求：
1.答案不超过200字。
2.答案中不要包含任何优化建议。
3.答案中尽可能保留信息中真实有效的数据。

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
The following is the output of the Linux command <{cmd}>:
{result}

# OBJECTIVE #
Please briefly analyze the performance status of the {self.app} application based on the information provided above.
Requirements:
1. The answer should not exceed 200 words.
2. Do not include any optimization suggestions in your answer.
3. Retain as much of the real and valid data from the information as possible.

# STYLE #
You are a professional system operations expert. Your response should be logically rigorous, objective, concise, and easy to understand, with clear and coherent structure, making your answer credible and trustworthy.

# TONE #
You should maintain a serious, earnest, and rigorous attitude.

# AUDIENCE #
Your answer will serve as an important reference for other system operations experts. Please provide as much real and useful information as possible, and do not fabricate any details.

# RESPONSE FORMAT #
If there are multiple analysis conclusions, please list them in numbered points.
""")
            report += self.ask_llm(profile_prompt)

        return report

    def generate_report(
            self,
            app_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        if app_report == "The current system is not running the ceph application; there is no need to analyze ceph performance.\n":
            return app_report
        report_prompt = translate(
            f"""
# CONTEXT # 
linux系统中正在运行{self.app}应用, 以下内容是{self.app}相关的性能信息:
{app_report}
信息中所涉及到的数据准确无误,真实可信。

# OBJECTIVE #
请根据上述信息,分析{self.app}应用的性能状况。
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
回答以"{self.app}分析如下:"开头，然后另起一行逐条分析。
如果有多条分析结论，请用数字编号分点作答。
        """,
            f"""
# CONTEXT #
The {self.app} application is currently running on a Linux system. The following content contains performance information related to {self.app}:
{app_report}
The data mentioned in the information is accurate and reliable.

# OBJECTIVE #
Please analyze the performance status of the {self.app} application based on the above information.
Requirements:
1. Do not include any optimization suggestions in your answer.
2. Retain as much of the real and valid data from the information as possible.
3. Do not omit any information that is worth analyzing.

# STYLE #
You are a professional system operations expert. Your response should be logically rigorous, objective, concise, and easy to understand, with clear and logical organization, making your answer credible.

# TONE #
You should maintain a serious, earnest, and rigorous attitude.

# AUDIENCE #
Your answer will serve as an important reference for other system operations experts. Please provide as much real and useful information as possible, and do not fabricate any information.

# RESPONSE FORMAT #
The answer should start with "{self.app} analysis is as follows:" and then proceed to analyze each point on a new line.
If there are multiple analysis conclusions, please number them and list them separately.
""")
        return self.ask_llm(report_prompt) + "\n"
