"""
LLM-as-judge helper: one model call that must return a JSON verdict.

Uses the OpenAI SDK directly (not LangChain), so judge calls are NOT recorded as
agent traces - only the agent's own work shows up in the traces being graded.

Note: the judge is the same model as the agent (only one model is available on the key),
so it may be lenient on its own mistakes. test_scorers.py checks it catches planted errors.
"""

import json
import re

from openai import OpenAI

from ai import config

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=config.GOEDEL_BASE_URL,
            api_key=config.require_api_key(),
            timeout=90,
            max_retries=3,   # also waits on 429 (rate limit) using Retry-After
        )
    return _client


def ask_judge(instructions: str, material: str) -> dict:
    """Return the judge's verdict as a dict. Raises if it doesn't answer in JSON (never silently passes)."""
    resp = _get_client().chat.completions.create(
        model=config.MODEL_ID,
        temperature=0,
        max_tokens=600,
        extra_body={"chat_template_kwargs": {"thinking": False}},
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": material},
        ],
    )
    text = (resp.choices[0].message.content or "").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)   # tolerate ```json fences or extra words
    if not match:
        raise ValueError(f"Judge did not return JSON: {text[:200]}")
    return json.loads(match.group(0))
