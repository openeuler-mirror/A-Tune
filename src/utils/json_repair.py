import json
import json5
import logging
from typing import Dict
from src.utils.llm import get_llm_response
from src.utils.common import translate

# TO implement more gernel repair: todo
def json_pair(
    json_str: str
) -> Dict:
    if not json_str or '{' not in json_str or '}' not in json_str:
        logging.warning(f"the input is not a json string: {json_str}")
        return {}
    
    json_start = json_str.find('{')
    json_end = json_str.rfind('}') + 1
    json_candidate = json_str[json_start:json_end]
    
    for parser_name, parser in [("json.load", json.loads), ("json5.loads", json5.loads)]:
        try:
            return parser(json_candidate)
        except Exception as e:
            logging.warning(f"failed to parse json with {parser_name}\nstring: {json_str}\nreson：{e}")

    return {}

def json_repair(
    json_str: str
) -> Dict:
    json_data = json_pair(json_str)
    if json_data != {}:
        return json_data
    prompt = translate(
        f'''
请检查并修复以下内容，使其成为合法、纯净的 JSON 对象。

要求：
移除所有非 JSON 内容。
修复语法错误，包括括号匹配、引号闭合、逗号使用、字符串和数值格式。
删除值为空或缺失的字段。
遇到重复键时，保留最先出现的键值对，忽略后续相同键。
仅输出一个可被 json.loads 直接解析的 JSON 对象，不要包含任何解释、注释、Markdown 代码块或额外文本。

<raw_input>
{json_str}
</raw_input>
''',
        f'''
Please check and fix the following content to make it a valid, clean JSON object.

Requirements:
Remove all non-JSON content.
Fix syntax errors, including bracket matching, quote closure, comma usage, and string and number formatting.
Delete fields with empty or missing values.
When encountering duplicate keys, retain the first key-value pair and ignore subsequent ones with the same key.
Output only one JSON object that can be directly parsed by json.loads; do not include any explanations, comments, Markdown code blocks, or additional text.

<raw_input>
{json_str}
</raw_input>
''')

    result = get_llm_response(prompt)
    return json_pair(result)
