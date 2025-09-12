import json
import json5
import logging
from typing import Dict

# TO implement more gernel repair: todo
def json_repair(
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