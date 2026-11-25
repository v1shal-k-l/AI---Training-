const BASE_URL = 'http://localhost:8000'

// Mock or real API — switched ONE ENDPOINT AT A TIME while we connect the backend.
//   true  = read the JSON file in /mock
//   false = call the FastAPI backend at BASE_URL
const MOCK = {
  portfolios: false,   // ✅ step 1 — GET /portfolios
  holdings: false,     // ✅ step 2 — GET /portfolios/{id}/holdings
  insight: false,      // ✅ step 6 — POST /portfolios/{id}/insights
  metrics: false,      // ✅ step 4 — GET /observability/metrics
  runs: false,         // ✅ step 3 — GET /observability/runs
  traceEvents: false,  // ✅ step 5 — GET /observability/runs/{id}
  submitFeedback: false, // ✅ step 7 — POST /insights/{id}/feedback
  assets: false,       // ✅ step 9 — GET /assets (new endpoint)
  transactions: false, // ✅ step 10 — GET /portfolios/{id}/transactions (new endpoint)
  feedback: false,     // ✅ step 8 — GET /feedback (new endpoint)
  createTransaction: false, // ✅ step 11 — POST /portfolios/{id}/transactions (new endpoint)
}

// GET/POST to the backend; throws a readable error instead of failing silently.
// If the backend explains the problem (FastAPI's "detail", e.g.
// "Cannot sell 999 units of NVDA — only 50 owned"), that becomes the error message.
async function apiFetch(path, options) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const detail = typeof body?.detail === 'string' ? body.detail : null
    throw new Error(detail ?? `API ${options?.method ?? 'GET'} ${path} failed: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export async function getPortfolios() {
  if (MOCK.portfolios) {
    const res = await fetch('/mock/portfolios.json')
    return res.json()
  }
  // Backend returns exactly the fields the pages use — no conversion needed
  return apiFetch('/portfolios')
}

export async function getHoldings(portfolioId) {
  if (MOCK.holdings) {
    const res = await fetch('/mock/holdings.json')
    const all = await res.json()
    // Pick the holdings for the clicked portfolio (the real API filters by id)
    return all.find(p => p.portfolio_id === Number(portfolioId))
      ?? { portfolio_id: portfolioId, total_value: 0, holdings: [] }
  }
  const rows = await apiFetch(`/portfolios/${portfolioId}/holdings`)


  const total = rows.reduce((sum, h) => sum + h.market_value, 0)

  return {
    portfolio_id: Number(portfolioId),
    total_value: Math.round(total * 100) / 100,
    holdings: rows.map(h => ({
      ...h,                       // keep all backend fields
      value: h.market_value,      // pages read "value"
      weight_pct: total ? Math.round((h.market_value / total) * 1000) / 10 : 0
      //  ↑ share of the total, 1 decimal — e.g. 21.6
    }))
  }
}

export async function generateInsight(portfolioId) {
  if (MOCK.insight) {
    const res = await fetch('/mock/insight.json')
    return res.json()
  }
  // Backend creates a real run (saved in ai_runs + trace_events) and returns it
  // with the field names the page uses — no conversion needed
  return apiFetch(`/portfolios/${portfolioId}/insights`, { method: 'POST' })
}

export async function getMetrics() {
  if (MOCK.metrics) {
    const res = await fetch('/mock/metrics.json')
    return res.json()
  }
    // Rename backend fields to the names the dashboard uses
  const m = await apiFetch('/observability/metrics')
  return {
    total_runs: m.total_runs,
    successes: m.successful_runs,
    failures: m.failed_runs,
    error_rate: m.error_rate,
    p95_latency_ms: m.p95_latency,
    average_latency_ms: m.average_latency    // extra — available if we want a card for it
  }
}

export async function getRuns() {
  if (MOCK.runs) {
    const res = await fetch('/mock/runs.json')
    return res.json()
  }
  // const res = await fetch(`${BASE_URL}/observability/runs`)
  return apiFetch('/observability/runs')

}

export async function getTraceEvents(runId) {
  if (MOCK.traceEvents) {
    const res = await fetch('/mock/trace_events.json')
    return res.json()
  }
  // Backend returns { run_id, trace_id, model_id, status, latency_ms, stages }
  return apiFetch(`/observability/runs/${runId}`)
}

export async function submitFeedback(runId, feedback) {
  if (MOCK.submitFeedback) {
    // Pretend-save: return a row shaped like the backend's
    return {
      feedback_id: Date.now(),
      run_id: Number(runId),
      ...feedback,
      reviewed_at: new Date().toISOString()
    }
  }
  // Backend returns the saved row: { feedback_id, run_id, helpful, reviewer_comment, reviewed_at }
  return apiFetch(`/insights/${runId}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedback)
  })
}

export async function getAssets() {
  if (MOCK.assets) {
    const res = await fetch('/mock/assets.json')
    return res.json()
  }
  // Backend returns exactly the fields the pages use — no conversion needed
  return apiFetch('/assets')
}

export async function getTransactions(portfolioId) {
  if (MOCK.transactions) {
    const res = await fetch('/mock/transactions.json')
    const all = await res.json()
    // Only this portfolio's transactions (the real API filters by id)
    return all.filter(t => t.portfolio_id === Number(portfolioId))
  }
  // Backend filters by portfolio and returns the fields the page uses
  return apiFetch(`/portfolios/${portfolioId}/transactions`)
}

// Save a BUY or SELL. txn = { asset_id, txn_type: 'BUY' | 'SELL', units }
// The backend sets the price, updates the holding, and returns the saved transaction.
export async function createTransaction(portfolioId, txn) {
  if (MOCK.createTransaction) {
    // Pretend-save (nothing changes on refresh)
    return { txn_id: Date.now(), portfolio_id: Number(portfolioId), ...txn }
  }
  return apiFetch(`/portfolios/${portfolioId}/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(txn)
  })
}

export async function getFeedback() {
  if (MOCK.feedback) {
    const res = await fetch('/mock/feedback.json')
    return res.json()
  }
  // Backend returns exactly the fields the pages use — no conversion needed
  return apiFetch('/feedback')
}