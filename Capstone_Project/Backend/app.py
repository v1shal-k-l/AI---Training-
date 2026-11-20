import os
import psycopg2

from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    reviewer_comment: str

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
# GENERATE INSIGHT
# =====================================================

@app.post("/portfolios/{portfolio_id}/insights")
def generate_insight(portfolio_id: int):

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT
        ROUND(
            SUM(
                h.units *
                a.synthetic_reference_price
            ),
            2
        ) AS portfolio_value

    FROM holdings h

    JOIN assets a
    ON h.asset_id = a.asset_id

    WHERE h.portfolio_id = %s;
    """

    cur.execute(query, (portfolio_id,))
    portfolio = cur.fetchone()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    cur.execute("""
        SELECT
            a.symbol,
            ROUND(
                h.units * a.synthetic_reference_price,
                2
            ) AS value

        FROM holdings h

        JOIN assets a
        ON h.asset_id = a.asset_id

        WHERE h.portfolio_id = %s

        ORDER BY value DESC

        LIMIT 3;
    """, (portfolio_id,))

    top_assets = cur.fetchall()

    cur.close()
    conn.close()

    exposures = [asset["symbol"] for asset in top_assets]

    return {
        "run_id": 999,
        "trace_id": "demo-trace-id",
        "status": "SUCCESS",
        "review_status": "DRAFT",
        "model_name": "demo-model",
        "portfolio_summary": (
            f"Portfolio total value is "
            f"{portfolio['portfolio_value']} USD."
        ),
        "largest_exposures": exposures,
        "data_limitations":
            "This insight is generated using synthetic data only."
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
            trace_id,
            model_id,
            status,
            latency_ms,
            error_type,
            created_at

        FROM ai_runs

        ORDER BY created_at DESC;
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data

# =====================================================
# TRACE EXPLORER
# =====================================================

@app.get("/observability/runs/{run_id}")
def get_trace_events(run_id: int):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            span_name,
            duration_ms,
            status,
            started_at

        FROM trace_events

        WHERE run_id = %s

        ORDER BY started_at;
    """, (run_id,))

    results = cur.fetchall()

    cur.close()
    conn.close()

    return results

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

    cur.execute("""
        INSERT INTO ai_feedback
        (
            run_id,
            helpful,
            reviewer_comment
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
    """,
    (
        run_id,
        payload.helpful,
        payload.reviewer_comment
    ))

    conn.commit()

    cur.close()
    conn.close()

    return {
        "success": True,
        "message": "Feedback submitted successfully"
    }

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