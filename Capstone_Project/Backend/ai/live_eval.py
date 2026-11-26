"""
Live evaluation: grades every real insight right after it is generated,
and attaches the scores to its MLflow trace (MLflow UI -> trace -> Assessments).

    tools_used          (code)       how many tools the agent called + their names
    token_usage         (code)       total tokens of the run
    latency_check       (code)       pass if the run took <= 4 s, otherwise "slow"
    claims_grounded     (LLM judge)  every claim is backed by the tool data
    safe_and_compliant  (LLM judge)  no advice / predictions / personal data

Runs in the background (FastAPI BackgroundTasks), so the user never waits for it.
A failure here is only logged - it must never break an insight.
"""

import logging
import time

import mlflow
from mlflow.entities import AssessmentSource

from ai.agent import setup_mlflow
from ai.prompts import user_message
from evaluation.judge import ask_judge
from evaluation.scorers import (
    GROUNDED_INSTRUCTIONS, JUDGE_SOURCE, SAFETY_INSTRUCTIONS, tool_calls, tool_data_text,
)

logger = logging.getLogger(__name__)

SLOW_LATENCY_MS = 4000
CODE_SOURCE = AssessmentSource(source_type="CODE", source_id="live_eval")


def _wait_for_trace(trace_id: str, tries: int = 10):
    """MLflow saves traces in the background - make sure this one is stored before reading it."""
    mlflow.flush_trace_async_logging()
    for _ in range(tries):
        trace = mlflow.get_trace(trace_id)
        if trace is not None:
            return trace
        time.sleep(0.5)
    raise RuntimeError("trace not found in MLflow store")


def _log(trace_id: str, name: str, value, rationale: str, source: AssessmentSource) -> None:
    mlflow.log_feedback(trace_id=trace_id, name=name, value=value, rationale=rationale, source=source)


def _judge_grounded(question: str, answer: str, trace) -> tuple[bool, str]:
    verdict = ask_judge(
        GROUNDED_INSTRUCTIONS,
        f"QUESTION:\n{question}\n\nTOOL DATA:\n{tool_data_text(trace)}\n\nANSWER:\n{answer}",
    )
    bad = verdict.get("unsupported_claims") or []
    ok = str(verdict.get("grounded", "")).lower() == "yes" and not bad
    reason = verdict.get("reason", "")
    return ok, (f"Unsupported: {'; '.join(map(str, bad))}. {reason}" if bad else reason)


def _judge_safe(question: str, answer: str) -> tuple[bool, str]:
    verdict = ask_judge(
        SAFETY_INSTRUCTIONS,
        # An insight request is a normal data request -> it should NOT be declined.
        f"REQUEST SHOULD BE DECLINED: no\n\nQUESTION:\n{question}\n\nANSWER:\n{answer}",
    )
    bad = verdict.get("violations") or []
    ok = str(verdict.get("safe", "")).lower() == "yes" and not bad
    reason = verdict.get("reason", "")
    return ok, (f"Violations: {'; '.join(map(str, bad))}. {reason}" if bad else reason)


def run_live_eval(mlflow_trace_id: str | None, portfolio_id: int, summary: str,
                  latency_ms: int, token_usage: int) -> None:
    """Grade one insight and attach 5 assessments to its MLflow trace."""
    if not mlflow_trace_id:
        return
    setup_mlflow()
    try:
        trace = _wait_for_trace(mlflow_trace_id)
        question = user_message(portfolio_id)

        # ---- code checks (instant, free) ----
        names = [c["name"] for c in tool_calls(trace)]
        _log(mlflow_trace_id, "tools_used", len(names),
             f"{len(names)} tool call(s): {', '.join(names) or 'none'}", CODE_SOURCE)

        _log(mlflow_trace_id, "token_usage", int(token_usage or 0),
             f"{token_usage} tokens used by the agent", CODE_SOURCE)

        fast = latency_ms <= SLOW_LATENCY_MS
        _log(mlflow_trace_id, "latency_check", fast,
             f"{latency_ms / 1000:.1f}s - {'OK' if fast else 'SLOW'} (limit {SLOW_LATENCY_MS / 1000:.0f}s)",
             CODE_SOURCE)

        # ---- LLM judges (one after the other: free key allows 2 parallel calls) ----
        ok, reason = _judge_grounded(question, summary, trace)
        _log(mlflow_trace_id, "claims_grounded", ok, reason, JUDGE_SOURCE)

        ok, reason = _judge_safe(question, summary)
        _log(mlflow_trace_id, "safe_and_compliant", ok, reason, JUDGE_SOURCE)

    except Exception as exc:   # live eval must never break the app
        logger.warning("Live evaluation failed for trace %s: %s", mlflow_trace_id, exc)