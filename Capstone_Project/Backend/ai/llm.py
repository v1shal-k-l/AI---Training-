from langchain_openai import ChatOpenAI

from ai import config


def get_llm() -> ChatOpenAI:
    """Chat model for the agent. Both providers speak the OpenAI format, so ChatOpenAI works for both."""
    common = dict(
        model=config.MODEL_ID,
        base_url=config.LLM_BASE_URL,
        api_key=config.require_api_key(),
        max_tokens=config.MODEL_MAX_TOKENS,
        timeout=config.MODEL_TIMEOUT_S,
        max_retries=1,
    )

    if config.IS_AZURE:
        # gpt-6-astra is a reasoning model: no temperature, and tool calling only works
        # through the Responses API (/v1/responses), not /v1/chat/completions.
        return ChatOpenAI(
            **common,
            use_responses_api=True,
            reasoning={"effort": config.REASONING_EFFORT},
        )

    return ChatOpenAI(
        **common,
        temperature=config.MODEL_TEMPERATURE,
        # Goedel's model "thinks" by default; off = faster and fewer tokens for short summaries.
        extra_body={"chat_template_kwargs": {"thinking": False}},
    )