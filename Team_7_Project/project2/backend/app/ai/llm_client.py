
import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.config import BASE_DIR

load_dotenv(BASE_DIR / ".env")

MODEL_NAME = os.getenv(
    "OPENROUTER_MODEL",
    "qwen/qwen-2.5-72b-instruct"
)


@lru_cache(maxsize=1)
def get_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    return ChatOpenAI(
        model=MODEL_NAME,
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        temperature=0.1,
        max_tokens=1500
    )
