import json
import os
import logging
import math

import yaml
from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate


class ModelBasedParameterSuggestion:
    def __init__(self, config_path):
        # 读取配置文件
        config = self.load_config(config_path)
        
        # 设置环境变量
        # 这里使用的是通义千问，需要阿里云的灵积服务中的API_KEY，默认使用的是qwen-turbo模型
        os.environ["DASHSCOPE_API_KEY"] = config['api_key']
        self.model = Tongyi(temperature=0.1)
        self.format_instructions = '你的返回结果必须是一个正确JSON格式且能用json.loads()解析的字典,注意直接返回字典不要显示其他的描述信息(也不需要用三个引号的代码框包裹)'
        
        # 读取预知识
        with open(config['preknowledge_path'], 'r', encoding='utf-8') as file:
            self.content = file.read()
        
        self.log_file_path = config['log_file_path']
        self.parameters = config['parameters']

    @staticmethod
    def load_config(file_path):
        """
        加载配置文件
        """
        with open(file_path, 'r', encoding='utf-8') as stream:
            return yaml.safe_load(stream)

    def extract_log_until_iterations(self):
        """
        从指定的日志文件中提取从最后一个 'iterations': 开始直到出现第二个 'iterations': 的文本段落，
        并且在提取的文本达到8000个字符时自动停止。
        """
        extracted_text = ""
        start_recording = False
        stop_recording = False
        
        with open(self.log_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in reversed(lines):  # 从最后一行开始向前读取
                if len(extracted_text) >= 8000:
                    # 如果文本长度已经达到或超过了8000个字符，停止读取
                    break
                
                if "'iterations':" in line:
                    if not start_recording:
                        # 第一个 'iterations': ，开始记录
                        start_recording = True
                        continue
                    else:
                        # 第二个 'iterations': ，停止记录
                        stop_recording = True
                        extracted_text = line + extracted_text
                        break
                
                if start_recording and not stop_recording:
                    # 将当前行添加到提取的文本中
                    extracted_text = line + extracted_text
        
        return extracted_text.strip()

    def get_suggested_parameters(self):
        # 从日志文件中提取特定的日志片段
        log_info = self.extract_log_until_iterations()
        
        # 创建PromptTemplate
        prompt = PromptTemplate(
            template=(
                self.content +
                "以下是ATune调优的某一轮日志内容，请你深度理解和分析日志内容，"
                "然后对其中列出的参数结果进行合理的参数设置推荐，"
                "以达到更好的调优效果(注意备注信息中有每个参数的范围、类型、步长) {subject}.\n"
                "{format_instructions}"
            ),
            input_variables=["subject"],
            partial_variables={"format_instructions": self.format_instructions}
        )
        
        # 构建输入
        input0 = prompt.format(subject=log_info)
        
        # 调用模型
        output = self.model.invoke(input0)
        
        # 解析输出
        return list(json.loads(output).values())

    def validate_and_adjust_parameters(self, values):
        adjusted_parameter_values = []

        for index, value in enumerate(values):
            param_info = self.parameters[index]['info']

            # 数据类型检查
            if param_info['dtype'] == int:
                try:
                    int_value = int(value)
                except ValueError:
                    logging.error(
                        "Invalid integer value for %s: %s. Using default value.",
                        self.parameters[index]['name'], value
                    )
                    int_value = param_info['scope'][0]  # 使用最小值作为默认值
                value = int_value

            elif param_info['dtype'] == str:
                str_value = str(value)
                value = str_value

            # 范围检查
            if 'scope' in param_info:
                min_val, max_val = param_info['scope']
                if value < min_val:
                    value = min_val
                elif value > max_val:
                    value = max_val

            # 步长检查
            if 'step' in param_info:
                step = param_info['step']
                if value % step != 0:
                    # 找到最接近的符合步长的值
                    adjusted_value = math.floor(value / step) * step
                    if adjusted_value < min_val:
                        adjusted_value = min_val
                    elif adjusted_value > max_val:
                        adjusted_value = max_val
                    value = adjusted_value

            # 选项检查
            if 'options' in param_info and value not in param_info['options']:
                closest_option = min(param_info['options'], key=lambda x: abs(int(x) - int(value)))
                logging.warning(
                "Invalid option %s for %s. Using closest option: %s",
                value, self.parameters[index]['name'], closest_option
                )
                value = closest_option

            adjusted_parameter_values.append(value)

        return adjusted_parameter_values
if __name__ == "__main__":
    config_file_path = "config.yaml"

    # 读取配置并初始化类
    model_suggestor = ModelBasedParameterSuggestion(config_file_path)
    suggested_params = model_suggestor.get_suggested_parameters()
    logging.basicConfig(level=logging.INFO)
    LOGGER = logging.getLogger(__name__)

    # 校验并调整参数
    adjusted_values = model_suggestor.validate_and_adjust_parameters(suggested_params)
    print(adjusted_values)