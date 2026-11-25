from langchain_openai import ChatOpenAI

from ai import config


def get_llm() -> ChatOpenAI:
    """Chat model on the Goedel API (it speaks the OpenAI format, so ChatOpenAI works)."""
    return ChatOpenAI(
        model=config.MODEL_ID,
        base_url=config.GOEDEL_BASE_URL,
        api_key=config.require_api_key(),
        temperature=config.MODEL_TEMPERATURE,
        max_tokens=config.MODEL_MAX_TOKENS,
        timeout=config.MODEL_TIMEOUT_S,
        max_retries=1,
        # The model "thinks" by default; off = faster and fewer tokens for short summaries.
        extra_body={"chat_template_kwargs": {"thinking": False}},
    )
