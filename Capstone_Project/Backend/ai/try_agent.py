"""
Manual check, run from the Backend folder:

    python -m ai.try_agent 1

Then view the trace:  mlflow ui --backend-store-uri sqlite:///mlflow.db   ->  http://localhost:5000
"""

import json
import sys

import mlflow

from ai.agent import InsightAgentError, run_insight_agent

portfolio_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1

try:
    result = run_insight_agent(portfolio_id)
    print(json.dumps(result, indent=2))
except InsightAgentError as e:
    print(f"FAILED [{e.error_type}] {e}  (mlflow trace: {e.mlflow_trace_id})")
finally:
    mlflow.flush_trace_async_logging()
