import os
import time
import uuid
import psycopg2

from datetime import datetime
from typing import Literal

from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai import config as ai_config
from ai.agent import InsightAgentError, mlflow_trace_url, run_insight_agent, tag_trace
from ai.prompts import PROMPT_VERSION as INSIGHT_PROMPT_VERSION
from ai.live_eval import run_live_eval


load_dotenv()

# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="AI-Powered Wealth & Asset Management",
    description="WAM Observability Dashboard",
    version="1.0.0"
)

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# DATABASE
# =====================================================

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "wealth_observability_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        cursor_factory=RealDictCursor
    )

# =====================================================
# MODELS
# =====================================================

class FeedbackRequest(BaseModel):
    helpful: bool
    reviewer_comment: str | None = None


class TransactionRequest(BaseModel):
    asset_id: int
    txn_type: Literal["BUY", "SELL"]      # anything else → 422
    units: float = Field(gt=0)            # must be more than 0
    # No price here on purpose: the backend uses the asset's reference price,
    # so a client can't record a trade at a made-up price.

# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/")
def home():
    return {
        "message": "WAM Observability API Running"
    }

# =====================================================
# PORTFOLIOS
# =====================================================

@app.get("/portfolios")
def get_portfolios():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            portfolio_id,
            portfolio_name,
            investment_style,
            owner_code,
            base_currency,
            created_at
        FROM portfolios
        ORDER BY portfolio_id;
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data

# =====================================================
# HOLDINGS
# =====================================================

@app.get("/portfolios/{portfolio_id}/holdings")
def get_holdings(portfolio_id: int):

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT
        a.symbol,
        a.asset_name,
        h.holding_id,
        a.sector,
        a.symbol,
        a.asset_id,
        a.asset_class,
        h.units,
        a.synthetic_reference_price,

        ROUND(
            (h.units * a.synthetic_reference_price)::numeric,
            2
        ) AS market_value

    FROM holdings h

    JOIN assets a
        ON h.asset_id = a.asset_id

    WHERE h.portfolio_id = %s

    ORDER BY market_value DESC;
    """

    cur.execute(query, (portfolio_id,))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data

# =====================================================
# ASSETS
# =====================================================

@app.get("/assets")
def get_assets():
    """All assets — Holdings page dropdown and auto-filled price."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            asset_id,
            symbol,
            asset_name,
            asset_class,
            sector,
            synthetic_reference_price
        FROM assets
        ORDER BY asset_id;
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data

# =====================================================
# TRANSACTIONS
# =====================================================

@app.get("/portfolios/{portfolio_id}/transactions")
def get_transactions(portfolio_id: int):
    """One portfolio's buys and sells, newest first."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM portfolios WHERE portfolio_id = %s;", (portfolio_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Portfolio not found")

    cur.execute("""
        SELECT
            t.txn_id,
            t.portfolio_id,
            t.asset_id,
            a.symbol,
            t.txn_type,
            t.units,
            t.unit_price,
            t.transaction_value,
            t.occurred_at
        FROM transactions t
        JOIN assets a ON t.asset_id = a.asset_id
        WHERE t.portfolio_id = %s
        ORDER BY t.occurred_at DESC, t.txn_id DESC;
    """, (portfolio_id,))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


@app.post("/portfolios/{portfolio_id}/transactions", status_code=201)
def create_transaction(portfolio_id: int, payload: TransactionRequest):
    """
    Records a BUY or SELL and updates the holding, all in one database transaction:
      - inserts a row in transactions (price = the asset's reference price)
      - BUY  → adds units to the holding (creates it if new)
      - SELL → removes units (deletes the holding when it reaches 0)
      - logs an audit_events row
    """

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Portfolio must exist (owner_code is used for the audit log)
        cur.execute(
            "SELECT owner_code FROM portfolios WHERE portfolio_id = %s;",
            (portfolio_id,)
        )
        portfolio = cur.fetchone()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        # Asset must exist — its reference price is the trade price
        cur.execute(
            "SELECT symbol, synthetic_reference_price FROM assets WHERE asset_id = %s;",
            (payload.asset_id,)
        )
        asset = cur.fetchone()
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # Current holding, locked so two sells at once can't both pass the check
        cur.execute("""
            SELECT units::float AS units
            FROM holdings
            WHERE portfolio_id = %s AND asset_id = %s
            FOR UPDATE;
        """, (portfolio_id, payload.asset_id))
        holding = cur.fetchone()
        owned = holding["units"] if holding else 0

        if payload.txn_type == "SELL":
            if owned == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"This portfolio doesn't own any {asset['symbol']}"
                )
            if payload.units > owned:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot sell {payload.units:g} units of {asset['symbol']} — only {owned:g} owned"
                )

        # 1. The transaction itself (transaction_value is calculated by the database)
        cur.execute("""
            INSERT INTO transactions (portfolio_id, asset_id, txn_type, units, unit_price)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING txn_id, portfolio_id, asset_id, txn_type, units, unit_price,
                      transaction_value, occurred_at;
        """, (
            portfolio_id, payload.asset_id, payload.txn_type,
            payload.units, asset["synthetic_reference_price"]
        ))
        txn = cur.fetchone()

        # 2. Update the holding
        if payload.txn_type == "BUY":
            cur.execute("""
                INSERT INTO holdings (portfolio_id, asset_id, units)
                VALUES (%s, %s, %s)
                ON CONFLICT (portfolio_id, asset_id) DO UPDATE
                    SET units = holdings.units + EXCLUDED.units,
                        updated_at = CURRENT_TIMESTAMP;
            """, (portfolio_id, payload.asset_id, payload.units))
            units_after = owned + payload.units
        else:
            units_after = owned - payload.units
            if units_after <= 0:
                cur.execute("""
                    DELETE FROM holdings
                    WHERE portfolio_id = %s AND asset_id = %s;
                """, (portfolio_id, payload.asset_id))
                units_after = 0
            else:
                cur.execute("""
                    UPDATE holdings
                    SET units = units - %s, updated_at = CURRENT_TIMESTAMP
                    WHERE portfolio_id = %s AND asset_id = %s;
                """, (payload.units, portfolio_id, payload.asset_id))

        # 3. Audit log (same format as the sample data in db.sql)
        cur.execute("""
            INSERT INTO audit_events (actor_code, entity_type, entity_id, action)
            VALUES (%s, 'TRANSACTION', %s, %s);
        """, (portfolio["owner_code"], txn["txn_id"], payload.txn_type))

        conn.commit()   # all three changes are saved together, or none

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

    return {
        **txn,
        "symbol": asset["symbol"],
        "units_owned_after": units_after,
    }

# =====================================================
# GENERATE INSIGHT
# =====================================================

# Step 3 (AI_INFERENCE) calls the LangChain agent in ai/agent.py: an LLM on the Goedel API
# that reads the numbers through tools. Each call is also traced in MLflow, and its
# mlflow_trace_id is saved in ai_runs so a run can be opened in the MLflow UI.
# Model id and prompt version come from the agent (ai/config.py, ai/prompts.py).

DATA_LIMITATIONS = (
    "Educational draft based on synthetic data and reference prices only "
    "— not investment advice."
)


def elapsed_ms(start):
    """Milliseconds since a time.perf_counter() start point."""
    return int(round((time.perf_counter() - start) * 1000))


def save_trace_events(cur, run_id, stages):
    """stages: (span_name, started_at, duration_ms[, status]) - status defaults to SUCCESS."""
    for span_name, step_started_at, duration_ms, *rest in stages:
        cur.execute("""
            INSERT INTO trace_events (run_id, span_name, started_at, duration_ms, status)
            VALUES (%s, %s, %s, %s, %s);
        """, (run_id, span_name, step_started_at, duration_ms, rest[0] if rest else "SUCCESS"))


def save_failed_run(cur, portfolio_id, error_type, latency_ms, mlflow_trace_id, stages):
    """Record a failed AI call as a FAILED run with its steps; returns the new run_id."""
    cur.execute("""
        INSERT INTO ai_runs (
            portfolio_id, trace_id, model_id, prompt_version,
            status, latency_ms, token_usage, error_type, generated_summary, mlflow_trace_id
        )
        VALUES (%s, %s, %s, %s, 'FAILED', %s, NULL, %s, NULL, %s)
        RETURNING run_id;
    """, (
        portfolio_id, str(uuid.uuid4()), ai_config.MODEL_ID, INSIGHT_PROMPT_VERSION,
        latency_ms, error_type, mlflow_trace_id
    ))
    run_id = cur.fetchone()["run_id"]
    save_trace_events(cur, run_id, stages)
    return run_id


@app.post("/portfolios/{portfolio_id}/insights")
def generate_insight(portfolio_id: int,background_tasks: BackgroundTasks):
    """
    Generates an insight AND records it:
      - one row in ai_runs   (the run itself → real run_id and trace_id)
      - one row per step in trace_events (so Trace Explorer can show it)
    """

    run_start = time.perf_counter()
    stages = []   # (span_name, started_at, duration_ms) for each step

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # ---------- Step 1: DATABASE_READ ----------
        step_start, started_at = time.perf_counter(), datetime.now()

        cur.execute("""
            SELECT portfolio_id, portfolio_name, investment_style
            FROM portfolios
            WHERE portfolio_id = %s;
        """, (portfolio_id,))
        portfolio = cur.fetchone()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        cur.execute("""
            SELECT
                a.symbol,
                a.asset_class,
                (h.units * a.synthetic_reference_price)::float AS value
            FROM holdings h
            JOIN assets a ON h.asset_id = a.asset_id
            WHERE h.portfolio_id = %s
            ORDER BY value DESC;
        """, (portfolio_id,))
        holdings = cur.fetchall()

        stages.append(("DATABASE_READ", started_at, elapsed_ms(step_start)))

        if not holdings:
            raise HTTPException(
                status_code=400,
                detail="Portfolio has no holdings to analyse"
            )

        # ---------- Step 2: ALLOCATION_CALCULATION ----------
        step_start, started_at = time.perf_counter(), datetime.now()

        total_value = sum(h["value"] for h in holdings)

        by_class = {}
        for h in holdings:
            by_class[h["asset_class"]] = by_class.get(h["asset_class"], 0) + h["value"]

        allocation = sorted(
            (
                {"asset_class": cls, "weight_pct": round(value / total_value * 100, 1)}
                for cls, value in by_class.items()
            ),
            key=lambda a: a["weight_pct"],
            reverse=True,
        )

        top3 = [
            {"symbol": h["symbol"], "weight_pct": round(h["value"] / total_value * 100, 1)}
            for h in holdings[:3]
        ]
        top3_share = round(sum(h["value"] for h in holdings[:3]) / total_value * 100, 1)

        stages.append(("ALLOCATION_CALCULATION", started_at, elapsed_ms(step_start)))

        # ---------- Step 3: AI_INFERENCE (LangChain agent + tools, traced in MLflow) ----------
        step_start, started_at = time.perf_counter(), datetime.now()

        try:
            ai = run_insight_agent(portfolio_id)
        except InsightAgentError as e:
            # Save the FAILED run (and its trace link) so error rate and Trace Explorer stay real.
            stages.append(("AI_INFERENCE", started_at, elapsed_ms(step_start), "FAILED"))
            failed_run_id = save_failed_run(
                cur, portfolio_id, e.error_type, elapsed_ms(run_start), e.mlflow_trace_id, stages
            )
            conn.commit()
            tag_trace(e.mlflow_trace_id, run_id=failed_run_id)
            raise HTTPException(
                status_code=502,
                detail=f"AI insight failed ({e.error_type}). Run {failed_run_id} was saved as FAILED.",
            )

        summary = ai["summary"]

        stages.append(("AI_INFERENCE", started_at, elapsed_ms(step_start)))

        # ---------- Step 4: OUTPUT_VALIDATION ----------
        step_start, started_at = time.perf_counter(), datetime.now()

        if not summary.strip() or len(summary) > 2000:
            raise HTTPException(status_code=500, detail="Generated summary failed validation")

        stages.append(("OUTPUT_VALIDATION", started_at, elapsed_ms(step_start)))

        # ---------- Save the run and its trace ----------
        latency_ms = elapsed_ms(run_start)
        trace_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO ai_runs (
                portfolio_id, trace_id, model_id, prompt_version,
                status, latency_ms, token_usage, error_type, generated_summary, mlflow_trace_id
            )
            VALUES (%s, %s, %s, %s, 'SUCCESS', %s, %s, NULL, %s, %s)
            RETURNING run_id, created_at;
        """, (
            portfolio_id, trace_id, ai["model_id"], ai["prompt_version"],
            latency_ms, ai["token_usage"], summary, ai["mlflow_trace_id"]
        ))
        run = cur.fetchone()

        save_trace_events(cur, run["run_id"], stages)

        conn.commit()   # run + all its steps are saved together, or not at all

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

    # Lets you search the MLflow UI by our run id (tags.run_id = '42').
    tag_trace(ai["mlflow_trace_id"], run_id=run["run_id"])
    background_tasks.add_task(
        run_live_eval, ai["mlflow_trace_id"], portfolio_id, summary, latency_ms, ai["token_usage"]
    )
    return {
        "run_id": run["run_id"],
        "trace_id": trace_id,
        "mlflow_trace_id": ai["mlflow_trace_id"],
        "mlflow_url": mlflow_trace_url(ai["mlflow_trace_id"]),
        "portfolio_id": portfolio_id,
        "status": "SUCCESS",
        "review_status": "DRAFT",
        "model_id": ai["model_id"],
        "prompt_version": ai["prompt_version"],
        "latency_ms": latency_ms,
        "token_usage": ai["token_usage"],
        "tools_called": ai["tools_called"],
        "generated_summary": summary,
        "largest_exposures": top3,
        "asset_allocation": allocation,
        "data_limitations": DATA_LIMITATIONS,
        "created_at": run["created_at"],
    }

# =====================================================
# OBSERVABILITY METRICS
# =====================================================

@app.get("/observability/metrics")
def get_metrics():

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT

        COUNT(*) total_runs,

        SUM(
            CASE
                WHEN status='SUCCESS'
                THEN 1
                ELSE 0
            END
        ) successful_runs,

        SUM(
            CASE
                WHEN status='FAILED'
                THEN 1
                ELSE 0
            END
        ) failed_runs,

        ROUND(
            AVG(latency_ms),
            2
        ) average_latency,

        ROUND(
            (
                SUM(
                    CASE
                        WHEN status='FAILED'
                        THEN 1
                        ELSE 0
                    END
                ) * 100.0
            ) / COUNT(*),
            2
        ) error_rate,

        ROUND(
            PERCENTILE_CONT(0.95)
            WITHIN GROUP (
                ORDER BY latency_ms
            )::numeric,
            2
        ) AS p95_latency

    FROM ai_runs;
    """

    cur.execute(query)

    metrics = cur.fetchone()

    cur.close()
    conn.close()

    return metrics

# =====================================================
# OBSERVABILITY RUNS
# =====================================================

@app.get("/observability/runs")
def get_runs():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            run_id,
            portfolio_id,
            trace_id,
            model_id,
            status,
            latency_ms,
            error_type,
            mlflow_trace_id,
            created_at

        FROM ai_runs

        ORDER BY created_at DESC,run_id DESC;
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return [{**r, "mlflow_url": mlflow_trace_url(r["mlflow_trace_id"])} for r in data]

# =====================================================
# TRACE EXPLORER
# =====================================================

@app.get("/observability/runs/{run_id}")
def get_trace_events(run_id: int):

    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Run details for the header
    cur.execute("""
        SELECT
            run_id,
            portfolio_id,
            trace_id,
            model_id,
            status,
            latency_ms,
            error_type,
            mlflow_trace_id,
            created_at
        FROM ai_runs
        WHERE run_id = %s;
    """, (run_id,))

    run = cur.fetchone()

    if not run:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # 2. The steps of that run, in order
    cur.execute("""
        SELECT
            event_id,
            span_name,
            duration_ms,
            status,
            started_at
        FROM trace_events
        WHERE run_id = %s
        ORDER BY started_at, event_id;
    """, (run_id,))

    stages = cur.fetchall()

    cur.close()
    conn.close()

    # Run details + its steps in one object (+ link to the same run in the MLflow UI)
    return {**run, "mlflow_url": mlflow_trace_url(run["mlflow_trace_id"]), "stages": stages}
# =====================================================
# FEEDBACK
# =====================================================

@app.post("/insights/{run_id}/feedback")
def submit_feedback(
    run_id: int,
    payload: FeedbackRequest
):

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # The run must exist (otherwise 404 instead of a database error)
        cur.execute("SELECT 1 FROM ai_runs WHERE run_id = %s;", (run_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

        # One review per run: a second review of the same run UPDATES the first
        cur.execute("""
            INSERT INTO ai_feedback (run_id, helpful, reviewer_comment)
            VALUES (%s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE
                SET helpful = EXCLUDED.helpful,
                    reviewer_comment = EXCLUDED.reviewer_comment,
                    reviewed_at = CURRENT_TIMESTAMP
            RETURNING feedback_id, run_id, helpful, reviewer_comment, reviewed_at;
        """, (
            run_id,
            payload.helpful,
            payload.reviewer_comment
        ))

        saved = cur.fetchone()
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

    # The saved row — the page shows it in the history straight away
    return saved


@app.get("/feedback")
def get_feedback():
    """All reviewer feedback, newest first (Feedback page + dashboard donut)."""

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            feedback_id,
            run_id,
            helpful,
            reviewer_comment,
            reviewed_at
        FROM ai_feedback
        ORDER BY reviewed_at DESC, feedback_id DESC;
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data

# =====================================================
# DASHBOARD SUMMARY
# =====================================================

@app.get("/dashboard/summary")
def dashboard_summary():

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT

        (SELECT COUNT(*) FROM portfolios)
        AS total_portfolios,

        (SELECT COUNT(*) FROM assets)
        AS total_assets,

        (SELECT COUNT(*) FROM transactions)
        AS total_transactions,

        (SELECT COUNT(*) FROM ai_runs)
        AS total_ai_runs,

        (
            SELECT ROUND(
                SUM(
                    h.units *
                    a.synthetic_reference_price
                ),
                2
            )
            FROM holdings h
            JOIN assets a
            ON h.asset_id = a.asset_id
        ) AS total_aum;
    """

    cur.execute(query)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

# =====================================================
# PORTFOLIO VALUES
# =====================================================

@app.get("/dashboard/portfolio-values")
def portfolio_values():

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT

        p.portfolio_name,

        ROUND(
            SUM(
                h.units *
                a.synthetic_reference_price
            ),
            2
        ) AS portfolio_value

    FROM portfolios p

    JOIN holdings h
    ON p.portfolio_id = h.portfolio_id

    JOIN assets a
    ON h.asset_id = a.asset_id

    GROUP BY p.portfolio_name

    ORDER BY portfolio_value DESC;
    """

    cur.execute(query)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data

# =====================================================
# ASSET ALLOCATION
# =====================================================

@app.get("/dashboard/asset-allocation")
def asset_allocation():

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT

        asset_class,

        ROUND(
            SUM(
                h.units *
                a.synthetic_reference_price
            ),
            2
        ) AS value

    FROM holdings h

    JOIN assets a
    ON h.asset_id = a.asset_id

    GROUP BY asset_class

    ORDER BY value DESC;
    """

    cur.execute(query)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data