import json
from typing import Dict

# TO implement more gernel repair: todo
def json_repair(
    json_str: str
) -> Dict:
    json_start = json_str.find('{')
    json_end = json_str.rfind('}') + 1
    json_str = json_str[json_start:json_end]
    json_data = json.loads(json_str)
    return json_data