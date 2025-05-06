from typing import List
import requests
from src.config import config
from langchain_openai import ChatOpenAI


def get_llm_response(prompt: str) -> str:
    client = ChatOpenAI(
        openai_api_key=config["LLM_KEY"],
        openai_api_base=config["LLM_URL"],
        model_name=config["LLM_MODEL_NAME"],
        tiktoken_model_name="cl100k_base",
        max_tokens=config["LLM_MAX_TOKENS"],
        streaming=True
    )
    result = client.invoke(input=prompt)
    return result.content


def get_embedding(text: str) -> List[float]:
    data = {
        "texts": [text]
    }
    res = requests.post(url=config['REMOTE_EMBEDDING_ENDPOINT'], json=data, verify=False)
    if res.status_code != 200:
        return []
    return res.json()[0]

  