import { useState, useEffect } from 'react'    // React hooks
import { getMetrics, getRuns, getFeedback } from '../api/api' // our data functions
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, Cell
} from 'recharts'
import Donut from '../components/Donut'   // shared with the Portfolio page

// Chart colors (same palette as the Portfolio charts)
const BLUE = '#4299e1'
const GREEN = '#48bb78'
const RED = '#f56565'

function DashboardPage() {
  const [metrics, setMetrics] = useState(null)
  const [runs, setRuns] = useState([])
  const [feedback, setFeedback] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      // Load all three at the same time
      const [metricsData, runsData, feedbackData] = await Promise.all([
        getMetrics(),
        getRuns(),
        getFeedback()
      ])
      setMetrics(metricsData)
      setRuns(runsData)
      setFeedback(feedbackData)
      setLoading(false)   // data arrived, stop loading
    }
    loadData()
  }, [])

  if (loading) {
    return <p>Loading dashboard...</p>
  }

  // --- Feedback summary ---
  const helpfulCount = feedback.filter(f => f.helpful).length
  const notHelpfulCount = feedback.length - helpfulCount
  const helpfulRate = feedback.length
    ? ((helpfulCount / feedback.length) * 100).toFixed(1)
    : 0

  // Look up the feedback for a run (undefined if nobody reviewed it)
  const feedbackForRun = (runId) => feedback.find(f => f.run_id === runId)

  // --- Chart data ---
  const p95 = metrics.p95_latency_ms

  // One bar per run
  const latencyData = runs.map(run => ({
    name: `R-${run.run_id}`,
    latency: run.latency_ms,
    status: run.status
  }))

  // Y axis goes a bit above the tallest bar OR the p95 line, whichever is higher,
  // rounded up to a whole second so the line is never cut off
  const yMax = (dataMax) => Math.ceil((Math.max(dataMax, p95) * 1.1) / 1000) * 1000

  const successRate = metrics.total_runs
    ? ((metrics.successes / metrics.total_runs) * 100).toFixed(1)
    : 0

  const statusData = [
    { name: 'Success', value: metrics.successes, color: GREEN },
    { name: 'Failed', value: metrics.failures, color: RED }
  ]

  const feedbackData = [
    { name: '👍 Helpful', value: helpfulCount, color: GREEN },
    { name: '👎 Not helpful', value: notHelpfulCount, color: RED }
  ]

  return (
    <div>
      <h1>Observability Dashboard</h1>

      {/* --- Metric Cards Row --- */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '16px',
        marginBottom: '32px'
      }}>

        {/* Each card is a div with a number and label */}
        <div style={cardStyle}>
          <div style={cardLabel}>Total Runs</div>
          <div style={cardValue}>{metrics.total_runs}</div>
        </div>

        <div style={cardStyle}>
          <div style={cardLabel}>Successes</div>
          <div style={{ ...cardValue, color: '#38a169' }}>
            {metrics.successes}
          </div>
        </div>

        <div style={cardStyle}>
          <div style={cardLabel}>Failures</div>
          <div style={{ ...cardValue, color: '#e53e3e' }}>
            {metrics.failures}
          </div>
        </div>

        <div style={cardStyle}>
          <div style={cardLabel}>Error Rate</div>
          <div style={{ ...cardValue, color: '#d69e2e' }}>
            {metrics.error_rate}%
          </div>
        </div>
      </div>

      {/* --- Latency per run --- */}
      <h2>Latency per Run</h2>
      <div className="chart-panel">
        <p className="chart-caption">
          Time each AI run took. Red bars are failed runs; the dashed line is the p95 target ({p95.toLocaleString()} ms).
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={latencyData} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tickLine={false} />
            <YAxis
              domain={[0, yMax]}
              tickFormatter={v => `${(v / 1000).toFixed(1)}s`}
              tickLine={false}
              axisLine={false}
              width={48}
            />
            <Tooltip formatter={(value) => [`${value.toLocaleString()} ms`, 'Latency']} />
            <ReferenceLine
              y={p95}
              stroke={RED}
              strokeDasharray="6 4"
              strokeWidth={2}
              label={{ value: `p95 ${p95.toLocaleString()} ms`, position: 'insideTopRight', fill: RED, fontSize: 12, fontWeight: 600 }}
            />
            <Bar dataKey="latency" radius={[6, 6, 0, 0]} maxBarSize={56}>
              {latencyData.map(d => (
                <Cell key={d.name} fill={d.status === 'SUCCESS' ? BLUE : RED} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* --- Two donuts side by side --- */}
      <div className="chart-row">
        <div className="chart-panel">
          <h3 className="chart-title">Run Status</h3>
          <Donut
            data={statusData}
            centerValue={`${successRate}%`}
            centerLabel="success rate"
          />
        </div>

        <div className="chart-panel">
          <h3 className="chart-title">Reviewer Feedback</h3>
          {feedback.length === 0 ? (
            <p className="chart-caption">No feedback recorded yet.</p>
          ) : (
            <Donut
              data={feedbackData}
              centerValue={`${helpfulRate}%`}
              centerLabel={`helpful · ${feedback.length} reviews`}
            />
          )}
        </div>
      </div>

      {/* --- Recent Runs Table --- */}
      <h2>Recent AI Runs</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
            <th style={{ padding: '8px' }}>Run ID</th>
            <th>Trace ID</th>
            <th>Model</th>
            <th>Status</th>
            <th>Latency</th>
            <th>Feedback</th>
          </tr>
        </thead>
        <tbody>
          {runs.map(run => (
            <tr key={run.run_id} style={{ borderBottom: '1px solid #f0f0f0' }}>
              <td style={{ padding: '8px' }}>R-{run.run_id}</td>
              <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                {run.trace_id.slice(0, 8)}...
              </td>
              <td>{run.model_id}</td>
              <td>
                <span style={{
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  backgroundColor: run.status === 'SUCCESS' ? '#c6f6d5' : '#fed7d7',
                  color: run.status === 'SUCCESS' ? '#276749' : '#9b2c2c'
                }}>
                  {run.status}
                </span>
              </td>
              <td>{run.latency_ms}ms</td>
              <td title={feedbackForRun(run.run_id)?.reviewer_comment || ''}>
                {feedbackForRun(run.run_id)
                  ? (feedbackForRun(run.run_id).helpful ? '👍' : '👎')
                  : <span style={{ color: '#a0aec0' }}>—</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
      
const cardStyle = {
  padding: '20px',
  borderRadius: '8px',
  border: '1px solid #e2e8f0',
  backgroundColor: '#f7fafc',
}

const cardLabel = {
  fontSize: '14px',
  color: '#718096',
  marginBottom: '4px',
}

const cardValue = {
  fontSize: '28px',
  fontWeight: 'bold',
  color: '#1a202c',
}

export default DashboardPage

