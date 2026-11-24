"""
AI layer for the WAM backend.

    config.py   - settings (model, API key, MLflow) read from Backend/.env
    llm.py      - the chat model client (Goedel, OpenAI-compatible API)
    tools.py    - tools the agent can call (read-only DB queries + calculations)
    prompts.py  - system prompt, versioned
    agent.py    - run_insight_agent(): builds the agent, runs it, traces it in MLflow

app.py only needs:  from ai.agent import run_insight_agent
"""
