import json
from typing import Dict

# TO implement more gernel repair: todo
def json_repair(
    json_str: str
) -> Dict:
    json_start = json_str.find('{')
    json_end = json_str.rfind('}') + 1
    json_str = json_str[json_start:json_end]
    try:
        json_data = json.loads(json_str)
    except json.decoder.JSONDecodeError as e:
        raise RuntimeError(f"failed to parse json, raw json_str is {json_str}")
    return json_data