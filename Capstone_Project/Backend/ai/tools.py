"""
Tools the agent can call. All read-only.

The plain functions (load_holdings, compute_allocation, compute_concentration) do the real work,
so the same numbers can be reused later by the evaluation scorers to check the AI's text.
The @tool wrappers are what the LLM sees; MLflow autolog records each call as a TOOL span.
"""

from langchain_core.tools import tool

from ai import config  # noqa: F401  (loads Backend/.env before database reads DB_* vars)
from database import get_db_connection

CONCENTRATION_LIMIT_PCT = 20.0


# ---------- plain functions ----------

def load_holdings(portfolio_id: int) -> dict:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT portfolio_id, portfolio_name, investment_style, base_currency
            FROM portfolios WHERE portfolio_id = %s;
        """, (portfolio_id,))
        portfolio = cur.fetchone()
        if not portfolio:
            return {"error": f"Portfolio {portfolio_id} not found"}

        cur.execute("""
            SELECT a.symbol, a.asset_name, a.asset_class, a.sector,
                   h.units::float AS units,
                   (h.units * a.synthetic_reference_price)::float AS value
            FROM holdings h
            JOIN assets a ON h.asset_id = a.asset_id
            WHERE h.portfolio_id = %s AND h.units > 0
            ORDER BY value DESC;
        """, (portfolio_id,))
        holdings = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    return {**dict(portfolio), "holdings": [dict(h) for h in holdings]}


def compute_allocation(portfolio_id: int) -> dict:
    data = load_holdings(portfolio_id)
    if "error" in data:
        return data
    holdings = data["holdings"]
    if not holdings:
        return {"error": "Portfolio has no holdings"}

    total = sum(h["value"] for h in holdings)
    by_class: dict[str, float] = {}
    for h in holdings:
        by_class[h["asset_class"]] = by_class.get(h["asset_class"], 0) + h["value"]

    return {
        "portfolio_name": data["portfolio_name"],
        "investment_style": data["investment_style"],
        "total_value": round(total, 2),
        "position_count": len(holdings),
        "asset_allocation": sorted(
            ({"asset_class": c, "weight_pct": round(v / total * 100, 1)} for c, v in by_class.items()),
            key=lambda a: a["weight_pct"], reverse=True,
        ),
        "positions": [
            {"symbol": h["symbol"], "value": round(h["value"], 2),
             "weight_pct": round(h["value"] / total * 100, 1)}
            for h in holdings
        ],
    }


def compute_concentration(portfolio_id: int) -> dict:
    alloc = compute_allocation(portfolio_id)
    if "error" in alloc:
        return alloc
    positions = alloc["positions"]
    top3 = positions[:3]
    return {
        "largest_position": positions[0],
        "top3": top3,
        "top3_share_pct": round(sum(p["weight_pct"] for p in top3), 1),
        "positions_above_limit": [p for p in positions if p["weight_pct"] > CONCENTRATION_LIMIT_PCT],
        "limit_pct": CONCENTRATION_LIMIT_PCT,
    }


def load_portfolios() -> list[dict]:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT portfolio_id, portfolio_name, investment_style, base_currency
            FROM portfolios ORDER BY portfolio_id;
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


# ---------- tools for the agent ----------

@tool
def list_portfolios() -> list[dict]:
    """List all portfolios with their id, name, investment style and currency."""
    return load_portfolios()


@tool
def get_portfolio_holdings(portfolio_id: int) -> dict:
    """Get a portfolio's name, style and every holding (symbol, asset class, sector, units, market value)."""
    return load_holdings(portfolio_id)


@tool
def calculate_allocation(portfolio_id: int) -> dict:
    """Get total value, number of positions, weight % of each position and of each asset class."""
    return compute_allocation(portfolio_id)


@tool
def check_concentration(portfolio_id: int) -> dict:
    """Get the largest position, top-3 positions and their combined share, and positions above the 20% limit."""
    return compute_concentration(portfolio_id)


@tool
def get_recent_transactions(portfolio_id: int, limit: int = 5) -> list[dict]:
    """Get the most recent buy/sell transactions of a portfolio (newest first)."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.symbol, t.txn_type, t.units::float AS units,
                   t.transaction_value::float AS value, t.occurred_at::text AS occurred_at
            FROM transactions t
            JOIN assets a ON t.asset_id = a.asset_id
            WHERE t.portfolio_id = %s
            ORDER BY t.occurred_at DESC, t.txn_id DESC
            LIMIT %s;
        """, (portfolio_id, max(1, min(limit, 20))))
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


ALL_TOOLS = [list_portfolios, get_portfolio_holdings, calculate_allocation, check_concentration, get_recent_transactions]
