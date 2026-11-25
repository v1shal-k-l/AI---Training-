import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getPortfolios, generateInsight } from '../api/api'

function InsightsPage() {
    const [portfolios, setPortfolios] = useState([])
  // List of portfolios for the dropdown

    const [selectedId, setSelectedId] = useState('')
    const [insight, setInsight] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    // Message shown if generating fails (backend down, portfolio has no holdings…)

    const { portfolioId } = useParams()


    useEffect(() => {
    getPortfolios().then(data => {
      setPortfolios(data)

      // If portfolio ID is in URL, pre-select it
      if (portfolioId) {
        setSelectedId(portfolioId)
      }
    })
  }, [portfolioId])
  const handleGenerate = async () => {
    if (!selectedId) return
    setLoading(true)        // show spinner
    setInsight(null)
    setError(null)
    try {
      const data = await generateInsight(selectedId)
      setInsight(data)      // save the AI response
    } catch {
      setError('Could not generate an insight. Check that the backend is running and try again.')
    } finally {
      setLoading(false)     // hide spinner, whether it worked or failed
    }
  }
  return (
    <div>
      <h1>AI Insights</h1>

      {/* Disclaimer banner — required by the rubric */}
      <div style={{
        padding: '12px 16px',
        backgroundColor: '#fffbeb',
        border: '1px solid #f6e05e',
        borderRadius: '8px',
        marginBottom: '24px',
        fontSize: '14px',
        color: '#741f10'
      }}>
        ⚠️ Educational draft based on synthetic data — not investment advice.
      </div>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <select
          value={selectedId}
          onChange={(e) => {
            setSelectedId(e.target.value)
            setInsight(null)     // old insight belonged to the previous portfolio
            setError(null)
          }}
          style={{
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid #cbd5e0',
            fontSize: '14px',
            minWidth: '250px'
          }}
        >
          <option value="">-- Select a portfolio --</option>
          {portfolios.map(p => (
            <option key={p.portfolio_id} value={p.portfolio_id}>
              {p.portfolio_name}
            </option>
          ))}
          </select>
          <button
          onClick={handleGenerate}
          disabled={!selectedId || loading}
          style={{
            padding: '8px 24px',
            borderRadius: '6px',
            border: 'none',
            backgroundColor: !selectedId || loading ? '#cbd5e0' : '#4299e1',
            color: 'white',
            fontSize: '14px',
            cursor: !selectedId || loading ? 'not-allowed' : 'pointer'
          }}
        >{loading ? 'Generating...' : 'Generate Insight'}
          {/*  ↑ Button text changes based on loading state
              Python equivalent:
              "Generating..." if loading else "Generate Insight"
          */}
        </button>
      </div>

      {error && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '8px',
          marginBottom: '16px',
          backgroundColor: '#fed7d7',
          color: '#9b2c2c',
          fontSize: '14px'
        }}>
          {error}
        </div>
      )}

      {insight && (
        <div style={{
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          overflow: 'hidden'
        }}>
        <div style={{
            display: 'flex',
            gap: '10px',
            flexWrap: 'wrap',
            padding: '16px',
            backgroundColor: '#f7fafc',
            borderBottom: '1px solid #e2e8f0'
          }}>
          
          <span style={badgeBlue}>Run: R-{insight.run_id}</span>
            <span style={badgePurple}>Trace: {insight.trace_id.slice(0, 8)}...</span>
            {/*                                 ↑ show first 8 chars only
                trace IDs are long UUIDs — no need to show all 36 chars */}
            <span style={badgeYellow}>DRAFT</span>
            <span style={badgeGray}>{insight.latency_ms}ms</span>
            <span style={badgeGray}>{insight.model_id}</span>
          </div>

          {/* AI generated content */}
          <div style={{ padding: '20px' }}>

            {/* Section 1: Portfolio Summary */}
            <h3 style={sectionTitle}>Portfolio Summary</h3>
            <p style={sectionText}>{insight.generated_summary}</p>

            {/* Section 2: Status */}
            <h3 style={sectionTitle}>Status</h3>
            <span style={{
              padding: '4px 12px',
              borderRadius: '4px',
              fontSize: '13px',
              backgroundColor: insight.status === 'SUCCESS' ? '#c6f6d5' : '#fed7d7',
              color: insight.status === 'SUCCESS' ? '#276749' : '#9b2c2c'
            }}>
              {insight.status}
            </span>

            {/* Section 3: Token usage (if available) */}
            {insight.token_usage && (
              <div style={{ marginTop: '16px' }}>
                <h3 style={sectionTitle}>Token Usage</h3>
                <p style={sectionText}>{insight.token_usage} tokens</p>
              </div>
            )}

          </div>

          {/* Footer: next steps for this run */}
          <div className="insight-footer">
            <span>Check how this insight was produced, or rate it.</span>
            <div className="footer-actions">
              <Link to={`/feedback/${insight.run_id}`} className="btn-secondary">
                💬 Give Feedback
              </Link>
              <Link to={`/trace/${insight.run_id}`} className="btn-primary">
                🔍 View Trace for R-{insight.run_id} →
              </Link>
            </div>
            {/*
              Both links carry the run ID in the URL (/feedback/1, /trace/1).
              Feedback pre-selects that run; Trace Explorer loads its trace.
            */}
          </div>
        </div>
      )}

    </div>
  )
}


// Badge styles — small colored labels
const badgeBlue = {
  padding: '4px 10px', borderRadius: '4px', fontSize: '12px',
  backgroundColor: '#ebf8ff', color: '#2b6cb0'
}
const badgePurple = {
  padding: '4px 10px', borderRadius: '4px', fontSize: '12px',
  backgroundColor: '#e9d8fd', color: '#553c9a', fontFamily: 'monospace'
}
const badgeYellow = {
  padding: '4px 10px', borderRadius: '4px', fontSize: '12px',
  backgroundColor: '#fefcbf', color: '#744210', fontWeight: 'bold'
}
const badgeGray = {
  padding: '4px 10px', borderRadius: '4px', fontSize: '12px',
  backgroundColor: '#edf2f7', color: '#4a5568'
}

// Section styles
const sectionTitle = {
  fontSize: '14px', fontWeight: '600', color: '#4a5568',
  marginBottom: '6px', marginTop: '16px'
}
const sectionText = {
  fontSize: '15px', color: '#1a202c', lineHeight: '1.6',
  margin: '0'
}

export default InsightsPage
