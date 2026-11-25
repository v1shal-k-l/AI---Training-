import { useState, useEffect, useRef } from 'react'
import { getPortfolios, getHoldings } from '../api/api'
import Donut from '../components/Donut'
import { Link } from 'react-router-dom'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip
} from 'recharts'

// One color per slice (same blue/green/orange/purple/red as before, plus 3 more for sectors)
const COLORS = ['#4299e1', '#48bb78', '#ed8936', '#9f7aea', '#f56565', '#38b2ac', '#ecc94b', '#ed64a6']

// Add up weight_pct by a field ("asset_class" or "sector") → donut slices, biggest first
//   Python equivalent: df.groupby(field)["weight_pct"].sum().sort_values(ascending=False)
function groupWeights(holdings, field) {
  const totals = {}
  holdings.forEach(h => {
    const key = h[field] || 'Other'
    totals[key] = (totals[key] || 0) + h.weight_pct
  })
  return Object.entries(totals)
    .sort((a, b) => b[1] - a[1])
    .map(([name, value], i) => ({
      name,
      value: Math.round(value * 10) / 10,
      color: COLORS[i % COLORS.length]
    }))
}

const money = v => `$${Number(v).toLocaleString()}`
const percent = v => `${v}%`


function PortfolioOverview() {
  const [portfolios, setPortfolios] = useState([])
  const [selectedId, setSelectedId] = useState('')
  //  ↑ portfolio picked in the dropdown ('' = nothing picked yet)

  const [holdings, setHoldings] = useState(null)
  const [loading, setLoading] = useState(true)                  // portfolio list
  const [holdingsLoading, setHoldingsLoading] = useState(false) // one portfolio's holdings

  // Remembers the latest pick, so a slow older request can't overwrite a newer one
  const latestPick = useRef('')

  useEffect(() => {
    getPortfolios().then(data => {
      setPortfolios(data)
      setLoading(false)
    })
  }, [])

  // When the user picks a portfolio from the dropdown
  const handleSelect = async (id) => {
    setSelectedId(id)
    latestPick.current = id
    setHoldings(null)

    if (!id) {                 // "-- Select a portfolio --" picked
      setHoldingsLoading(false)
      return
    }

    setHoldingsLoading(true)
    const data = await getHoldings(id)
    if (latestPick.current !== id) return   // user already picked another one
    setHoldings(data)
    setHoldingsLoading(false)
  }

  if (loading) return <p>Loading portfolios...</p>

  // Full details of the picked portfolio (undefined if none picked)
  const selected = portfolios.find(p => p.portfolio_id === Number(selectedId))

  // --- Numbers for the stat cards and charts (only once holdings are loaded) ---
  const rows = holdings ? [...holdings.holdings].sort((a, b) => b.value - a.value) : []
  //  ↑ largest position first
  const largest = rows[0]
  const top3Pct = Math.round(rows.slice(0, 3).reduce((sum, h) => sum + h.weight_pct, 0) * 10) / 10
  const classSlices = groupWeights(rows, 'asset_class')
  const sectorSlices = groupWeights(rows, 'sector')

  return (
    <div>
      <h1>Portfolios</h1>

      {/* --- Portfolio dropdown --- */}
      <label className="field-label" htmlFor="portfolio-select">
        Select a portfolio
      </label>
      <select
        id="portfolio-select"
        className="portfolio-select"
        value={selectedId}
        onChange={(e) => handleSelect(e.target.value)}
      >
        <option value="">-- Select a portfolio --</option>
        {portfolios.map(p => (
          <option key={p.portfolio_id} value={p.portfolio_id}>
            {p.portfolio_name} — {p.investment_style} · {p.base_currency}
          </option>
        ))}
      </select>

      {/* Hint before anything is picked */}
      {!selected && (
        <p className="empty-hint">
          Choose one of your {portfolios.length} portfolios to see its holdings and asset allocation.
        </p>
      )}

      {/* --- Summary card for the picked portfolio --- */}
      {selected && (
        <div className="portfolio-card">
          <div>
            <div className="portfolio-card-name">{selected.portfolio_name}</div>
            <div className="portfolio-card-meta">
              <span className="chip">{selected.investment_style}</span>
              <span className="chip">{selected.base_currency}</span>
              <span>Owner: {selected.owner_code}</span>
              <span>Since {new Date(selected.created_at).toLocaleDateString()}</span>
            </div>
          </div>

          {holdings && (
            <div className="portfolio-card-total">
              <div className="portfolio-card-total-label">Total value</div>
              <div className="portfolio-card-total-value">
                ${holdings.total_value.toLocaleString()}
              </div>
            </div>
          )}

          <div className="footer-actions">
            <Link to={`/holdings/${selected.portfolio_id}`} className="btn-secondary">
              Holdings
            </Link>
            <Link to={`/insights/${selected.portfolio_id}`} className="btn-primary">
              ✨ AI Insights
            </Link>
            {/*
              to={`/holdings/${selected.portfolio_id}`}
              If portfolio_id is 1, this becomes: /holdings/1
              The Holdings page reads "1" from the URL and loads that portfolio.
              Python equivalent: f"/holdings/{portfolio_id}"
            */}
          </div>
        </div>
      )}

      {holdingsLoading && <p>Loading holdings...</p>}

      {/* --- Stat cards, charts, holdings table --- */}
      {holdings && rows.length === 0 && (
        <p className="empty-hint">This portfolio has no holdings yet.</p>
      )}

      {holdings && rows.length > 0 && (
        <div style={{ marginTop: '24px' }}>

          {/* 1. Stat cards */}
          <div className="stat-row">
            <div className="stat-card">
              <div className="stat-label">Holdings</div>
              <div className="stat-value">{rows.length}</div>
              <div className="stat-sub">positions</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Largest position</div>
              <div className="stat-value">{largest.weight_pct}%</div>
              <div className="stat-sub">{largest.symbol} · {money(largest.value)}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Top 3 combined</div>
              <div className="stat-value">{top3Pct}%</div>
              <div className="stat-sub">{rows.slice(0, 3).map(h => h.symbol).join(', ')}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Sectors</div>
              <div className="stat-value">{sectorSlices.length}</div>
              <div className="stat-sub">{classSlices.length} asset classes</div>
            </div>
          </div>

          {/* 3. Asset class + sector donuts, side by side */}
          <div className="chart-row">
            <div className="chart-panel">
              <h3 className="chart-title">Asset Allocation</h3>
              <p className="chart-caption">Share of total value by asset class</p>
              <Donut
                data={classSlices}
                centerValue={classSlices.length}
                centerLabel="asset classes"
                format={percent}
              />
            </div>
            <div className="chart-panel">
              <h3 className="chart-title">Sector Breakdown</h3>
              <p className="chart-caption">Share of total value by sector</p>
              <Donut
                data={sectorSlices}
                centerValue={sectorSlices.length}
                centerLabel="sectors"
                format={percent}
              />
            </div>
          </div>

          {/* 2. Top holdings bar chart */}
          <div className="chart-panel">
            <h3 className="chart-title">Top Holdings</h3>
            <p className="chart-caption">Market value per position, largest first</p>
            <ResponsiveContainer width="100%" height={rows.length * 44 + 40}>
              {/*  ↑ grows with the number of holdings so bars never get squashed */}
              <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 24 }}>
                {/*  layout="vertical" = horizontal bars (categories go down the Y axis) */}
                <CartesianGrid horizontal={false} strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={v => `$${(v / 1000).toLocaleString()}k`} />
                <YAxis type="category" dataKey="symbol" width={64} />
                <Tooltip
                  formatter={(v, _name, item) => [`${money(v)} (${item.payload.weight_pct}%)`, 'Value']}
                />
                <Bar dataKey="value" fill={COLORS[0]} radius={[0, 6, 6, 0]} barSize={22} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <h2>Holdings</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                <th style={{ padding: '8px' }}>Symbol</th>
                <th>Asset Class</th>
                <th>Units</th>
                <th>Value</th>
                <th>Weight</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(h => (
                <tr key={h.holding_id}
                    style={{ borderBottom: '1px solid #f0f0f0' }}>
                  <td style={{ padding: '8px' }}>{h.symbol}</td>
                  <td>{h.asset_class}</td>
                  <td>{h.units}</td>
                  <td>${h.value.toLocaleString()}</td>
                  <td>{h.weight_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default PortfolioOverview
