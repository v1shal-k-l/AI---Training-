"""
Run the exam:   python -m evaluation.run_eval            (all cases)
                python -m evaluation.run_eval --pilot    (first 3 + 1 refusal, to check quickly)

Results: MLflow UI -> experiment "wealth-insights" -> Evaluations / Runs.
"""

import os
import sys

# Free Goedel key allows 2 requests at a time - keep MLflow under that
# (2 questions in parallel, their scorers one after another).
os.environ.setdefault("MLFLOW_GENAI_EVAL_MAX_WORKERS", "2")
os.environ.setdefault("MLFLOW_GENAI_EVAL_MAX_SCORER_WORKERS", "1")
os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")

import mlflow  # noqa: E402
import mlflow.genai  # noqa: E402

from ai.agent import answer_question, setup_mlflow  # noqa: E402
from ai.prompts import ASSISTANT_PROMPT_VERSION  # noqa: E402
from evaluation.dataset import get_cases  # noqa: E402
from evaluation.scorers import (  # noqa: E402
    claims_grounded, correct_answer, right_tools_used, safe_and_compliant,
)

SCORERS = [right_tools_used, correct_answer, claims_grounded, safe_and_compliant]
PILOT_ROWS = [0, 1, 7, 13]   # 2 answers, 1 refusal, 1 "portfolio 999"


def predict(question: str) -> str:
    return answer_question(question)


def main() -> None:
    pilot = "--pilot" in sys.argv
    cases = get_cases()
    data = [cases[i] for i in PILOT_ROWS] if pilot else cases

    setup_mlflow()
    run_name = f"{'pilot' if pilot else 'eval'}-{ASSISTANT_PROMPT_VERSION}"
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags({"prompt_version": ASSISTANT_PROMPT_VERSION, "cases": len(data)})
        results = mlflow.genai.evaluate(data=data, predict_fn=predict, scorers=SCORERS)

    # ---------- console scorecard ----------
    df = results.tables["eval_results"]
    print(f"\n=== {run_name}: {len(df)} questions ===")
    for s in SCORERS:
        col = f"{s.name}/value"
        if col not in df:
            print(f"{s.name}: NO SCORES (check errors in MLflow)")
            continue
        vals = df[col]
        scored = vals.notna().sum()
        passed = (vals == True).sum()  # noqa: E712
        print(f"{s.name:22} {passed}/{scored} passed   ({len(df) - scored} not applicable/not scored)")

    print("\nPer question:")
    for _, row in df.iterrows():
        req = row.get("request", row.get("inputs"))
        q = req.get("question", str(req)) if isinstance(req, dict) else str(req)
        print(f"\n  Q: {q}\n  A: {str(row.get('response', ''))[:300]}")
        for s in SCORERS:
            v = row.get(f"{s.name}/value")
            mark = "n/a " if v is None or v != v else ("PASS" if v == True else "FAIL")  # noqa: E712  (v != v: NaN)
            why = row.get(f"{s.name}/rationale")
            why = "not applicable to this question" if mark == "n/a " else (why if isinstance(why, str) else "")
            print(f"     [{mark}] {s.name:20} {why}")
    print(f"\nMLflow run id: {results.run_id}")


if __name__ == "__main__":
    main()
