from ..base_analyzer import BaseAnalyzer

from src.utils.llm import get_llm_response


class GaussdbAnalyzer():
    def __init__(self, data, **kwargs):
        self.data = data

    def run(self) -> str:
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        if not self.data:
            return None
        report_prompt = f"""
        # CONTEXT # 
        linux系统中正在运行GaussDB应用, 以下内容是GaussDB相关的性能信息:
        {self.data}
        信息中所涉及到的数据准确无误,真实可信。

        # OBJECTIVE #
        请根据上述信息,分析GaussDB应用的性能状况。
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
        回答以"GaussDB分析如下:"开头，然后另起一行逐条分析。
        如果有多条分析结论，请用数字编号分点作答。

        """
        return get_llm_response(report_prompt) + "\n"