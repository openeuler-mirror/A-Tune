from openai import OpenAI
import re
import httpx
import yaml

#读取配置文件
def load_llm_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config.get('llm', {})

llm_config = load_llm_config("config/llm_config.yaml")

# 创建 OpenAI 客户端实例
client = OpenAI(
    base_url=llm_config.get('base_url', ''),
    api_key=llm_config.get('api_key', ''),
    http_client=httpx.Client(verify=False)
)
role_prompt = "你是一个专业的文本分析专家，擅长从复杂的技术文档中精准提取关键的应用参数信息，并以清晰、规范的方式呈现提取结果。"
role_prompt2 = "你是一位资深的性能调优专家，拥有丰富的操作系统应用参数调优经验，并能给出有效的建议。"

json_example = """
[
    {
        "name": "innodb_write_io_threads",
        "info": {
          "desc": "The number of I/O threads for write operations in InnoDB. ",
          "needrestart": "true",
          "type": "continuous",
          "min_value":2,
          "max_value":200,
          "default_value":4,
          "dtype": "int",
          "version":"8.0",
          "related_param":[],
          "options":null
        }
    },
    {
        "name": "innodb_read_io_threads",
        "info": {
            "desc": "MySQL [mysqld] parameters 'innodb_read_io_threads'.",
            "needrestart": "true",
            "type": "continuous",
            "min_value": 1,
            "max_value": 64,
            "default_value": 4,
            "dtype": "int",
            "version":"8.0",
            "related_param":[],
            "options":null
        }
    }
]
"""

def get_messages(
    role_prompt: str,
    history: str,
    usr_prompt: str,
) -> list:
    """
    构建消息列表，用于与OpenAI模型进行对话。

    Parameters:
        role_prompt (str): 系统角色提示。
        history (str): 历史对话内容。
        usr_prompt (str): 用户当前请求。

    Returns:
        list: 包含系统角色提示、历史对话和当前请求的消息列表。
    """
    messages = []
    if role_prompt != "":
        messages.append({"role": "system", "content": role_prompt})
    if len(history) > 0:
        messages.append({"role": "assistant", "content":history})
    if usr_prompt != "":
        messages.append({"role": "user", "content": usr_prompt})
    return messages



def parameter_official_knowledge_preparation(text: str, app: str)-> str:
    """
    从官方文档文本中提取参数信息并返回JSON格式的参数列表。

    Parameters:
        text (str): 官方文档文本内容。
        example (str): 示例JSON格式。
        app (str): 应用程序名称。

    Returns:
        str: 包含提取参数信息的JSON字符串，若提取失败则返回None。
    """
    prompt = '''
    你是一个专业的文本分析助手，擅长从技术文档中精准提取关键信息。现在，我给你一段关于{app}数据库参数配置相关的文本内容。你的任务是从这段文本中提取所有包含的{app}配置参数的信息，并按照指定格式输出。
    
    <文本内容>
    {text}

    <任务要求>
    请将提取的信息以JSON格式返回，其中每个参数的信息应包含以下字段（如果文本中未提及某字段，请设置为null，不要自行生成信息）：
    name（参数名称）
    desc（参数描述）
    needrestart（设置参数后是否需要重启，布尔值）
    type（参数是否连续，可以为continuous或discrete）
    min_value（参数的最小值）
    max_value（参数的最大值）
    default_value（参数的默认值）
    dtype（参数的数据类型，如int、string、boolean、float，该字段请只在给定的这几个中选择）
    version（参数的生效版本）
    related_param(与该参数存在关联的参数)
    options(参数的离散值集合)

    <注意事项>
    如果参数取值为连续值，请将options字段设置为null。
    如果参数取值为离散值（如ON/OFF），请将min_value字段和max_value字段均设置为null，将options设置为离散值集合（如["ON", "OFF"]）。
    如果文本中未提及某个字段，请在JSON中将该字段设置为null。
    如果文本中未提及某个参数，请不要在JSON中输出该参数。
    最大值和最小值可以从“Permitted values”或“Range”等描述中获取。
    needrestart字段可以参考Dynamic内容，Dynamic表示是否能动态调整该参数，该值为yes时needrestart值为false；该值为no时needrestart为true。
    related_param字段可以在参数的描述中查找，若描述中提到其他的参数，则可以进一步判断是不是一个相关参数，如果是，请在该字段用列表输出。若没有，输出一个空列表。

    <输出示例>
    请按照以下格式输出JSON数据:
    {example}

    '''
    example = json_example
    messages = get_messages(role_prompt,[],prompt.format(app=app, example=example, text=text))
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=llm_config.get('model', ''),  
        temperature=1
    )

    # 打印响应内容
    print(chat_completion.choices[0].message.content)
    ans = chat_completion.choices[0].message.content
    ans = re.sub(r"<think>.*?</think>", "", ans, flags=re.DOTALL)
    json_pattern =  r'\[.*\]'
    json_str = re.search(json_pattern, ans, re.DOTALL)

    if json_str:
        # 提取匹配到的JSON字符串
        json_str = json_str.group(0)
        return json_str
    else:
        print("没有找到JSON数据")
        return 
    

#从文本中提取参数信息
def parameter_knowledge_preparation(text: str, params: list, app: str) -> str:
    """
    从web等文本中提取给定参数列表中的参数信息并返回JSON格式的参数列表。

    Parameters:
        text (str): 文本内容。
        example (str): 示例JSON格式。
        params (list): 参数列表。
        app (str): 应用程序名称。

    Returns:
        str: 包含提取参数信息的JSON字符串，若提取失败则返回None。
    """
    prompt = '''
    你是一个专业的文本分析助手，擅长从技术文档中精准提取关键信息。现在，我给你一段关于{app}参数配置相关的文本内容。你的任务是从这段文本中提取以下参数的信息，请将给定参数列表的参数信息尽可能详细地提取。
    
    <文本内容>
    {text}

    <任务要求>
    注意，我只需要这些给定参数的信息，其他参数的信息请不要输出：
    给定的参数列表是：{params}
    请将提取的信息以 JSON 格式返回，其中每个参数的信息应包含在对应的键下。如果文本中没有提到的参数，请不要在 JSON 中将该参数输出。

    参考的执行步骤是：
    1. 首先匹配是否有给定参数列表中的{app}参数
    2. 将该参数的值或者描述等信息找到，需要的信息包括参数名称(name)，参数描述(desc)，参数设置后是否需要重启(needrestart)，参数是否连续(type)，参数最小值(min_value)，参数最大值(max_value)，参数默认值(default_value)，参数的数据类型(dtype),参数的生效版本（version）,与该参数存在关联的参数(related_param),参数的离散值集合(options)。注意：Dynamic表示是否能动态调整该参数，其为yes时needrestart为false。
    3. 注意如果参数取值为连续值，请将options字段设置为null。如果参数取值为离散值（如ON/OFF），请将min_value字段和max_value字段均设置为null，将options设置为离散值集合（如["ON", "OFF"]）。
    4. 将找到的信息保存，未找到的信息项设置为null，请不要自己生成相关的信息，要在文本中查找。
    5. 将你从文本中获取到的信息以 json 格式输出，一个输出的示例为：
    {example}
    其中没有获取到的信息请设置为null
    
    注意：只输出一个包括参数信息的 json。如果文本中没有提到的参数，请不要在 JSON 中输出。不在example中的信息项，请不要输出。

'''
    example = json_example
    messages = get_messages(role_prompt,[],prompt.format(app=app, params=params,example=example, text=text))
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=llm_config.get('model', ''), 
        temperature=0.1,
    )

    # 打印响应内容
    print(chat_completion.choices[0].message.content)
    ans = chat_completion.choices[0].message.content
    ans = re.sub(r"<think>.*?</think>", "", ans, flags=re.DOTALL)

    json_pattern =  r'\[.*\]'
    json_str = re.search(json_pattern, ans, re.DOTALL)

    if json_str:
        # 提取匹配到的JSON字符串
        json_str = json_str.group(0)
        return json_str
    else:
        print("没有找到JSON数据")
        return 


#参数信息的gpt来源
def get_gpt_knowledge(params: list, app: str) -> str:
    """
    GPTT获取给定参数列表中每个参数的详细信息，包括名称、描述、获取命令、设置命令等，并返回JSON格式的参数列表。

    Parameters:
        params (list): 参数列表。
        example (str): 示例JSON格式。
        app (str): 应用程序名称。

    Returns:
        str: 包含参数信息的JSON字符串，若获取失败则返回None。
    """
    prompt =  '''
    请根据以下{app}参数列表，详细描述每个参数的相关知识，包括包括参数名称(name)，参数描述(desc)，参数获取命令(get)，参数设置命令(set)，参数设置后是否需要重启(needrestart)，参数是否连续(type)，参数最小值(min_value)，参数最大值(max_value)，参数默认值(default_value)，参数的数据类型(dtype)，参数的生效版本(version)，参数的互相关联参数(related_param),参数的离散值集合(options)。
    {params}
    
    <任务要求>：
    1.对于每个参数，提供清晰的定义和作用描述。
    2.参数的描述(desc)要求至少包括：1）这个参数的详细作用；2）可以缓解系统的哪一方面瓶颈，从CPU，disk IO，network，memory中选择相关的瓶颈给出；3）取值的描述，如果取值只有几个，分别描述每个取值的意义。如果取值为范围，则说明增大或减小该值的意义和作用。
    3.参数的最小值(min_value)和最大值(max_value)及默认值(default_value)，请直接给出数值，不要出现计算，数值不需要引号。若参数取值为连续值，则参数的离散值（options）字段设置为null；若参数取值为离散值，请将最大值最小值设置为null，将参数离散值（options）字段设置为离散取值，例如参数取值为ON/OFF，则将options设置为["ON","OFF"]
    4.参数的互相关联参数(related_param)是与该参数相互影响的参数，一般需要同时调整配置。该字段请用列表输出，若没有，则输出一个空列表。
    5.使用准确的技术术语，并确保描述的准确性和可靠性。
    6.输出格式将每个参数的所有信息总结为一个json格式的知识。
    最终将结果以json格式输出，输出的json格式不要包含注释，参数的描述用中文输出，描述中的瓶颈用英文表示，其余字段用英文输出，输出示例格式为：
    {example}
    '''

    example = json_example    
    messages = get_messages(role_prompt2,[],prompt.format(app=app, params=params, example=example))
    chat_completion = client.chat.completions.create(
        messages=messages,
        model= llm_config.get('model', ''), 
        temperature=0.1
    )

    # 打印响应内容
    print(chat_completion.choices[0].message.content)
    ans = chat_completion.choices[0].message.content
    ans = re.sub(r"<think>.*?</think>", "", ans, flags=re.DOTALL)

    json_pattern =  r'\[.*\]'
    json_str = re.search(json_pattern, ans, re.DOTALL)

    if json_str:
        # 提取匹配到的JSON字符串
        json_str = json_str.group(0)
        print(json_str)
        return json_str
    else:
        print("没有找到JSON数据")
        return  

def aggregate_web_result(text: str, param: str, app: str) -> str:
    """
    将多个JSON格式的参数描述整合成一个完整的JSON对象。

    Parameters:
        text (str): 多个JSON格式的参数描述文本。
        param (str): 参数名称。
        app (str): 应用程序名称。

    Returns:
        str: 整合后的JSON字符串，若整合失败则返回None。
    """
    prompt =  '''
    我有一些JSON格式的{app}参数结构化信息，这些JSON对象描述了同一个参数{param}的不同属性。这些JSON对象可能包含重复或部分信息，需要将它们整合成一个完整的JSON对象。
    目标：
    将所有描述同一参数的JSON对象整合成一个完整的JSON对象，合并重复字段，并确保每个字段的值是准确且完整的。
    要求：
    请根据输入，生成一个整合后的JSON对象，确保字段值完整，但是请不要添加你的知识，只根据提供的json对象填充。
    输入：以下是输入的json格式的参数信息
    {text}
    '''
    messages = get_messages(role_prompt2,[],prompt.format(app=app, param=param, text=text))
    chat_completion = client.chat.completions.create(
        messages=messages,
        model= llm_config.get('model', ''), 
        temperature=0.1
    )
    print(chat_completion.choices[0].message.content)
    ans = chat_completion.choices[0].message.content
    ans = re.sub(r"<think>.*?</think>", "", ans, flags=re.DOTALL)
    json_pattern =  r'\{.*\}'
    json_str = re.search(json_pattern, ans, re.DOTALL)

    if json_str:
        # 提取匹配到的JSON字符串
        json_str = json_str.group(0)
        return json_str
    else:
        print("没有找到JSON数据")
        return  

def aggregate_result(param: str, official: str, web: str, gpt: str, app: str) -> str:
    """
    汇总来自官方文档、web网页和GPT的参数信息，并整合成一个完整的JSON对象。

    Parameters:
        param (str): 参数名称。
        official (str): 官方文档中的参数信息。
        web (str): web网页中的参数信息。
        gpt (str): GPT中的参数信息。
        app (str): 应用程序名称。

    Returns:
        str: 整合后的JSON字符串，若整合失败则返回None。
    """
    prompt = '''
    我有一些JSON格式的{app}参数结构化信息，这些JSON对象描述了同一个参数{param}，JSON信息的来源分别为官方文档，web网页和GPT。
    具体信息如下：
    官方文档:{official}
    web网页:{web}
    GPT:{gpt}

    请根据以下要求和提示，汇总并处理来自 官方文档、web网页 和 GPT 的信息，并确保最终的描述准确、完整且一致。输出与输入结构相同的 JSON 格式参数信息：

    1. 参数描述（desc）
   请综合官方文档、web网页和ChatGPT的描述，提取清晰、详细的参数功能描述。若来源中的描述有所不同，请优先参考GPT和官方文档中提供的详细说明，并与web网页中的实践建议进行对比，确保描述完整、详细且准确。如果有冲突，选择权威的描述。如无冲突，尽可能保留更多详细内容。描述最后总结为中文。

    2. 是否需要重启（needrestart）
   根据官方文档、web网页和ChatGPT提供的信息，判断该应用参数修改后是否需要重启{app}服务才能生效。若来源中存在不同的意见，优先参考官方文档和GPT来源中的内容。如果官方文档和GPT中的做法冲突，请重新分析是否需要重启并给出结果。

    3. 参数类型（type）
   请根据官方文档、web网页和ChatGPT提供的描述，确认该参数的类型。类型描述只包括`continuous`、`discrete`，优先参考官方文档中的类型定义，并与web网页中的使用实例进行对比，确保类型选择准确。如果不确定，请重新分析参数是离散还是连续。

    4. 最小值（min_value）
   请根据官方文档、web网页和ChatGPT提供的信息，确认该参数的最小值。若参数是离散的，该值设置为null。若来源中有不同的最小值，请优先参考官方文档中的说明，或者通过查看{app}官方文档来确认。如果web网页和ChatGPT中的值不同，确保选择的最小值符合实际环境配置需求。

    5. 最大值（max_value）
   根据官方文档、web网页和ChatGPT提供的信息，确认该参数的最大值。若参数是离散的，该值设置为null。如果不同来源给出的最大值有所不同，选择它们的交集或更具权威性的最大值。例如，如果官方文档明确给出了最大值范围，而web网页和ChatGPT提供的最大值偏大或偏小，请参照官方文档中的推荐值。

    6. 默认值（default_value）
   请根据官方文档、web网页和ChatGPT提供的信息，确认该参数的默认值。若不同来源提供的默认值不一致，请优先参考官方文档中的默认值。如果有多个来源提供相同的默认值，则采用该值作为最终结论。

    7. 数据类型（dtype）
   根据官方文档、web网页和ChatGPT提供的信息，确认该参数的数据类型（如`int`、`string`、`boolean`等）。如果不同来源对数据类型的定义不一致，请优先参考官方文档中的准确描述，确保数据类型与{app}的实际配置一致。如果有多个合理的选项，请选择最常见的类型并验证其准确性。

    8. 生效版本(version)
    根据官方文档、web网页和ChatGPT提供的信息，确认该参数的生效版本。请优先参考官方文档中的生效版本。如果有多个来源提供相同的生效版本，则采用该值作为最终结论。

    9.相关参数(related_param)
    根据官方文档、web网页和ChatGPT提供的信息，确认该参数的相关参数。该字段请将多个来源的值取并集输出为列表。

    10.参数的离散值(options)
    根据官方文档、web网页和ChatGPT提供的信息，确认该参数的离散取值。若参数是连续的，该值设置为null。若参数是离散的，请优先参考官方文档来源的内容，如果有多个来源提供相同的离散值，则采用该离散值为最终结论。

    注意：最终输出结构和输入结构相同，输出一个json格式的参数信息，请不要给出分析过程，只输出最后的json。

    '''
    messages = get_messages(role_prompt2,[],prompt.format(app=app, param=param, official=official, web=web, gpt=gpt))
    chat_completion = client.chat.completions.create(
        messages=messages,
        model= llm_config.get('model', ''), 
        temperature=0.1
    )
    #print(chat_completion.choices[0].message.content)
    ans = chat_completion.choices[0].message.content
    ans = re.sub(r"<think>.*?</think>", "", ans, flags=re.DOTALL)
    json_pattern =  r'\{.*\}'
    json_str = re.search(json_pattern, ans, re.DOTALL)

    if json_str:
        # 提取匹配到的JSON字符串
        json_str = json_str.group(0)
        return json_str
    else:
        print("没有找到JSON数据")
        return  


if __name__ == "__main__":
    parameter_knowledge_preparation()

