"""
The insight agent: LLM + tools, traced in MLflow.

    result = run_insight_agent(portfolio_id)
    result["summary"], result["token_usage"], result["mlflow_trace_id"], ...

On failure it raises InsightAgentError with .error_type and .mlflow_trace_id,
so the caller can still save a FAILED run that links to the MLflow trace.
"""

import logging
import threading
import time

import mlflow
import mlflow.langchain
import openai
from langchain.agents import create_agent

from ai import config
from ai.llm import get_llm
from ai.prompts import (
    ASSISTANT_PROMPT, ASSISTANT_PROMPT_VERSION, PROMPT_VERSION, SYSTEM_PROMPT, user_message,
)
from ai.tools import ALL_TOOLS

logger = logging.getLogger(__name__)
_setup_lock = threading.Lock()
_agent = None
_mlflow_ready = False


class InsightAgentError(Exception):
    def __init__(self, error_type: str, message: str, mlflow_trace_id: str | None = None):
        super().__init__(message)
        self.error_type = error_type
        self.mlflow_trace_id = mlflow_trace_id


def setup_mlflow() -> None:
    """Point MLflow at the tracking store and turn on LangChain auto-tracing (LLM + tool spans).
    Must run BEFORE any traced function starts, or the root span goes to the default store."""
    global _mlflow_ready
    with _setup_lock:
        if _mlflow_ready:
            return
        try:
            mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
            mlflow.set_experiment(config.MLFLOW_EXPERIMENT)
            mlflow.langchain.autolog()
        except Exception as exc:   # tracing must never take the API down
            logger.warning("MLflow setup failed, continuing without tracing: %s", exc)
        _mlflow_ready = True


def _get_agent():
    global _agent
    with _setup_lock:
        if _agent is None:
            _agent = create_agent(model=get_llm(), tools=ALL_TOOLS, system_prompt=SYSTEM_PROMPT)
    return _agent


def _error_type(exc: Exception) -> str:
    if isinstance(exc, openai.APITimeoutError):
        return "TIMEOUT"
    if isinstance(exc, openai.RateLimitError):
        return "RATE_LIMIT"
    if isinstance(exc, (openai.AuthenticationError, openai.PermissionDeniedError)):
        return "AUTH_ERROR"
    if isinstance(exc, openai.APIError):
        return "MODEL_API_ERROR"
    return "AGENT_ERROR"


@mlflow.trace(name="insight_agent", span_type="AGENT")
def _traced_run(portfolio_id: int) -> dict:
    mlflow.update_current_trace(tags={
        "portfolio_id": str(portfolio_id),
        "model_id": config.MODEL_ID,
        "prompt_version": PROMPT_VERSION,
        "source": "wam-backend",
    })

    state = _get_agent().invoke({"messages": [{"role": "user", "content": user_message(portfolio_id)}]})
    messages = state["messages"]

    summary = messages[-1].content if messages else ""
    if isinstance(summary, list):  # some providers return content parts
        summary = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in summary)
    summary = summary.strip()
    if not summary:
        raise InsightAgentError("EMPTY_OUTPUT", "Model returned an empty summary")

    tokens = sum((getattr(m, "usage_metadata", None) or {}).get("total_tokens", 0) for m in messages)
    tools_called = [tc["name"] for m in messages for tc in (getattr(m, "tool_calls", None) or [])]

    return {"summary": summary, "token_usage": tokens, "tools_called": tools_called}


def run_insight_agent(portfolio_id: int) -> dict:
    setup_mlflow()
    start = time.perf_counter()
    try:
        result = _traced_run(portfolio_id)
    except Exception as exc:
        trace_id = mlflow.get_last_active_trace_id()
        if isinstance(exc, InsightAgentError):
            exc.mlflow_trace_id = trace_id
            raise
        raise InsightAgentError(_error_type(exc), str(exc), trace_id) from exc

    return {
        **result,
        "model_id": config.MODEL_ID,
        "prompt_version": PROMPT_VERSION,
        "latency_ms": int((time.perf_counter() - start) * 1000),
        "mlflow_trace_id": mlflow.get_last_active_trace_id(),
    }


# =====================================================
# Question-answering mode (any question; used by the evaluation)
# =====================================================

_qa_agent = None


def _get_qa_agent():
    global _qa_agent
    with _setup_lock:
        if _qa_agent is None:
            _qa_agent = create_agent(model=get_llm(), tools=ALL_TOOLS, system_prompt=ASSISTANT_PROMPT)
    return _qa_agent


def answer_question(question: str) -> str:
    """Answer one free-text question. Returns the answer text; the trace holds tools + tokens."""
    setup_mlflow()   # before the trace starts
    return _traced_answer(question)


@mlflow.trace(name="qa_agent", span_type="AGENT")
def _traced_answer(question: str) -> str:
    mlflow.update_current_trace(tags={
        "model_id": config.MODEL_ID,
        "prompt_version": ASSISTANT_PROMPT_VERSION,
        "source": "wam-backend",
    })
    state = _get_qa_agent().invoke({"messages": [{"role": "user", "content": question}]})
    content = state["messages"][-1].content
    if isinstance(content, list):
        content = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)
    return content.strip()


_experiment_id = None


def mlflow_trace_url(mlflow_trace_id: str | None) -> str | None:
    """Link that opens this trace in the MLflow UI, or None (old runs have no trace)."""
    global _experiment_id
    if not mlflow_trace_id:
        return None
    if _experiment_id is None:
        setup_mlflow()
        try:
            exp = mlflow.get_experiment_by_name(config.MLFLOW_EXPERIMENT)
            _experiment_id = exp.experiment_id if exp else None
        except Exception as exc:
            logger.warning("Could not look up MLflow experiment: %s", exc)
        if _experiment_id is None:
            return None
    return (f"{config.MLFLOW_UI_URL}/#/experiments/{_experiment_id}/traces"
            f"?selectedEvaluationId={mlflow_trace_id}&traceId={mlflow_trace_id}")


def tag_trace(mlflow_trace_id: str | None, **tags) -> None:
    """Add tags after the run, e.g. tag_trace(tid, run_id=42) once ai_runs has the row."""
    if not mlflow_trace_id:
        return
    setup_mlflow()
    try:
        for key, value in tags.items():
            mlflow.set_trace_tag(mlflow_trace_id, key, str(value))
    except Exception as exc:   # a missing tag must never fail the request
        logger.warning("Could not tag MLflow trace %s: %s", mlflow_trace_id, exc)
