import re
import os
import threading
import time
from typing import List
import requests
from src.config import config
from langchain_openai import ChatOpenAI
import httpx
from colorama import init, Fore, Style
import logging

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
requests.Session.verify = False

g_llm_req_id = 0
g_llm_req_id_lock = threading.Lock()
g_llm_log_path = ""
g_llm_log_inited = False

def init_llm_log_dir():
    '''初始化llm log目录
    '''
    global g_llm_log_inited, g_llm_log_path
    if g_llm_log_inited:
        return
    # 默认使用log/llm路径，如果有配置log_dir，则使用 ${log_dir}/llm 路径
    log_dir = "log"
    if config["log_dir"]:
        log_dir = str(config["log_dir"])
    # 支持相对路径和绝对路径
    if not log_dir.startswith("/"):
        log_dir = os.path.join(os.getcwd(), log_dir)
    g_llm_log_path = os.path.join(log_dir, "llm")
    logging.info("llm log dir: %s", g_llm_log_path)
    os.makedirs(g_llm_log_path, exist_ok=True)
    g_llm_log_inited = True

init_llm_log_dir()

def get_next_llm_req_id():
    # 为每个llm请求按顺序分配一个id
    global g_llm_req_id_lock, g_llm_req_id
    llm_req_id = 0
    with g_llm_req_id_lock:
        llm_req_id = g_llm_req_id
        g_llm_req_id += 1
    return llm_req_id

def get_llm_response(prompt: str, **kwargs) -> str:
    global g_llm_log_path
    if config["ssl"] == 'enable':
        client = ChatOpenAI(
            openai_api_key=config["LLM_KEY"],
            openai_api_base=config["LLM_URL"],
            model_name=config["LLM_MODEL_NAME"],
            tiktoken_model_name="cl100k_base",
            max_tokens=config["LLM_MAX_TOKENS"],
            streaming=True
        )
    elif config["ssl"] == 'disable':
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

    llm_req_id = get_next_llm_req_id()
    time_start = time.time()
    result = client.invoke(input=prompt, **kwargs)
    time_end = time.time()
    time_cost = time_end - time_start

    match = re.search(r"<think>(.*?)</think>(.*)", result.content, flags=re.DOTALL)
    if match:
        thought_process = match.group(1).strip("\n")
        thought_result = match.group(2).strip("\n")
        output = thought_result
    else:
        output = result.content

    input_len = len(prompt)
    output_len = len(result.content)
    if config["llm_log_to_file"]:
        with open(os.path.join(g_llm_log_path, f"req-{llm_req_id}.log"), "w") as f:
            f.write(f"===== ask: ===== (request id {llm_req_id})\n")
            f.write(f"{prompt}\n")
            f.write(f"===== ans: ===== (input len {input_len}, output len {output_len}, use {time_cost:.2f}s)\n")
            f.write(f"{result.content}\n")
    if config["llm_log_to_console"]:
        logging.info("%sget_llm_response ask: (request id %d)\n%s%s", Fore.YELLOW, llm_req_id, prompt, Style.RESET_ALL)
        logging.info("%sget_llm_response ans: (request id %d) input len %d, output len %d, use %s\n%s%s", 
                     Fore.GREEN, llm_req_id, input_len, output_len, f"{time_cost:.2f}sec", result.content, Style.RESET_ALL)

    return output

def get_embedding(text: str) -> List[float]:
    data = {
        "model": config["REMOTE_EMBEDDING_MODEL_NAME"],
        "texts": [text]
    }
    res = requests.post(url=config['REMOTE_EMBEDDING_ENDPOINT'], json=data, verify=False)
    if res.status_code != 200:
        return []
    return res.json()[0]


if __name__ == "__main__":
    get_llm_response("introduce yourself")
    # get_llm_response("introduce yourself, reply in English.")
    # get_llm_response("introduce yourself, reply in Chinese.")
    # get_llm_response("介绍你自己")
    # get_llm_response("介绍你自己, 用英文回答")
    # get_llm_response("介绍你自己, 用中文回答")