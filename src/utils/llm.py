import re
from typing import List
import requests
from src.config import config
from langchain_openai import ChatOpenAI
import httpx
from colorama import init, Fore, Style
import logging

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
requests.Session.verify = False
def get_llm_response(prompt: str, **kwargs) -> str:
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
    result = client.invoke(input=prompt, **kwargs)
    logging.debug("%sget_llm_response ask:\n%s\n%s", Fore.YELLOW, prompt, Style.RESET_ALL)

    match = re.search(r"<think>(.*?)</think>(.*)", result.content, flags=re.DOTALL)
    if match:
        thought_process = match.group(1).strip("\n")
        thought_result = match.group(2).strip("\n")
        logging.debug("%sget_llm_response think:\n%s\n%s", Fore.GREEN, thought_process, Style.RESET_ALL)
        logging.debug("%sget_llm_response ans:\n%s\n%s", Fore.GREEN, thought_result, Style.RESET_ALL)
        return thought_result
    else:
        logging.debug("%sget_llm_response ans:\n%s\n%s", Fore.GREEN, result, Style.RESET_ALL)
        return result.content


def get_embedding(text: str) -> List[float]:
    data = {
        "model": config["REMOTE_EMBEDDING_MODEL_NAME"],
        "texts": [text]
    }
    res = requests.post(url=config['REMOTE_EMBEDDING_ENDPOINT'], json=data, verify=False)
    if res.status_code != 200:
        return []
    return res.json()[0]

  