import re
from typing import List
import requests
from src.config import config
from langchain_openai import ChatOpenAI
import httpx

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
requests.Session.verify = False
def get_llm_response(prompt: str) -> str:
    if 'enable' == config["ssl"]:
        client = ChatOpenAI(
        openai_api_key=config["LLM_KEY"],
        openai_api_base=config["LLM_URL"],
        model_name=config["LLM_MODEL_NAME"],
        tiktoken_model_name="cl100k_base",
        max_tokens=config["LLM_MAX_TOKENS"],
        streaming=True
        )
    elif 'disable' ==  config["ssl"]:
        client = ChatOpenAI(
            openai_api_key=config["LLM_KEY"],
            openai_api_base=config["LLM_URL"],
            model_name=config["LLM_MODEL_NAME"],
            tiktoken_model_name="cl100k_base",
            max_tokens=config["LLM_MAX_TOKENS"],
            streaming=True,
            http_client=httpx.Client(verify=False)
        )
    else:
        raise ValueError(f"无效的SSL配置: {config['ssl']}，必须为 'enable' 或 'disable'")
    result = client.invoke(input=prompt)
    return re.sub(r"<think>.*?</think>", "", result.content, flags=re.DOTALL)


def get_embedding(text: str) -> List[float]:
    data = {
        "model": config["REMOTE_EMBEDDING_MODEL_NAME"],
        "texts": [text]
    }
    res = requests.post(url=config['REMOTE_EMBEDDING_ENDPOINT'], json=data, verify=False)
    if res.status_code != 200:
        return []
    return res.json()[0]

  