import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getTraceEvents } from '../api/api'


function TraceExplorer() {

  const [trace, setTrace] = useState(null)
  // The trace data — starts as null

  // Run ID from the URL, e.g. /trace/1 → "1" (undefined on plain /trace)
  const { runId } = useParams()

  const [searchId, setSearchId] = useState(runId ?? '')
  // What the user types in the search box — starts with the URL's run ID if there is one

  const [loading, setLoading] = useState(false)

  const [error, setError] = useState(null)
  // Message shown when the run can't be loaded (e.g. "Run 999 not found")

  // Load the trace for one run ID
  const loadTrace = async (id) => {
    if (!id) return
    setLoading(true)
    setError(null)
    setTrace(null)
    try {
      const data = await getTraceEvents(id)
      setTrace(data)
    } catch {
      setError(`No run found with ID "${id}".`)
    } finally {
      setLoading(false)      // runs whether it worked or failed
    }
  }

  // Opened from a link like "View Trace" → load that run's trace straight away
  useEffect(() => {
    if (runId) loadTrace(runId)
  }, [runId])

    // When user clicks "Search" or presses Enter
  const handleSearch = () => loadTrace(searchId)
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const formatSpanName = (name) => {
    return name
      .split('_')              // ["api", "request", "received"]
      .map(word =>             // capitalize each word
        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        //   ↑ first letter big        ↑ rest small ("DATABASE" → "Database")
      )
      .join(' ')               // "Api Request Received"
  }

    return (
    <div>
      <h1>Trace Explorer</h1>

      {/* Search bar */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <input
          type="text"
          placeholder="Enter Run ID (e.g., 1)"
          value={searchId}
          onChange={(e) => setSearchId(e.target.value)}
          onKeyDown={handleKeyDown}
          style={{
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid #cbd5e0',
            fontSize: '14px',
            width: '300px'
          }}
        />

          <button
          onClick={handleSearch}
          disabled={!searchId || loading}
          style={{
            padding: '8px 24px',
            borderRadius: '6px',
            border: 'none',
            backgroundColor: !searchId || loading ? '#cbd5e0' : '#4299e1',
            color: 'white',
            cursor: !searchId || loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Loading...' : 'Search'}
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

      {trace && (
        <div style={{
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          overflow: 'hidden'
        }}>

          {/* Header with run metadata */}
          <div style={{
            padding: '16px 20px',
            backgroundColor: '#f7fafc',
            borderBottom: '1px solid #e2e8f0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '8px'
          }}>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <span style={badgeBlue}>Run: R-{trace.run_id}</span>
              <span style={badgeMono}>Trace: {trace.trace_id.slice(0, 8)}...</span>
              <span style={badgeGray}>{trace.model_id}</span>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <span style={{
                ...badgeStatus,
                backgroundColor: trace.status === 'SUCCESS' ? '#c6f6d5' : '#fed7d7',
                color: trace.status === 'SUCCESS' ? '#276749' : '#9b2c2c'
              }}>
                {trace.status}
              </span>
              <span style={badgeGray}>Total: {trace.latency_ms}ms</span>

              {/* Same run in the MLflow UI: prompts, tool calls, tokens.
                  Older runs (before the AI agent) have no MLflow trace → no link. */}
              {trace.mlflow_url ? (
                <a
                  href={trace.mlflow_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  title="Open the detailed AI trace in MLflow (MLflow UI must be running)"
                  style={mlflowButton}
                >
                  Open in MLflow ↗
                </a>
              ) : (
                <span style={badgeGray} title="This run was recorded before MLflow tracing was added">
                  No MLflow trace
                </span>
              )}
            </div>
          </div>

          {/* Stage waterfall */}
          <div style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '14px', color: '#4a5568', marginBottom: '16px' }}>
              Stage Waterfall
            </h3>

            {trace.stages.length === 0 && (
              <p style={{ color: '#718096', fontSize: '14px' }}>
                No trace steps were recorded for this run.
              </p>
            )}

            {trace.stages.map(stage => {
              const maxDuration = Math.max(
                ...trace.stages.map(s => s.duration_ms)
              )
              

              // Calculate bar width as percentage
              const barWidth = (stage.duration_ms / maxDuration) * 100
              //  45 / 1100 * 100 = 4.09%

              return (
                <div
                  key={stage.event_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    marginBottom: '12px',
                    gap: '12px'
                  }}
                >

                  {/* Stage name — fixed width so bars align */}
                  <div style={{
                    width: '180px',
                    fontSize: '13px',
                    color: '#4a5568',
                    flexShrink: 0
                    //  ↑ "don't squeeze this column even if space is tight"
                  }}>
                    {formatSpanName(stage.span_name)}
                  </div>

                  {/* The bar */}
                  <div style={{
                    flex: 1,
                    //  ↑ "take all remaining space"
                    backgroundColor: '#edf2f7',
                    borderRadius: '4px',
                    height: '28px',
                    position: 'relative'
                    //  ↑ needed so the inner bar can position itself inside
                  }}>
                    <div style={{
                      width: `${barWidth}%`,
                      //  ↑ template literal — same as Python f-string
                      //  f"{bar_width}%"
                      height: '100%',
                      backgroundColor: stage.status === 'SUCCESS' ? '#4299e1' : '#e53e3e',
                      //  Blue if success, red if failed
                      borderRadius: '4px',
                      minWidth: '2px'
                      //  ↑ so even tiny durations (5ms) show a visible sliver
                    }} />
                  </div>

                  {/* Duration label */}
                  <div style={{
                    width: '70px',
                    textAlign: 'right',
                    fontSize: '13px',
                    fontWeight: '600',
                    color: stage.duration_ms > 2000 ? '#e53e3e' : '#4a5568',
                    //  ↑ turns RED if stage took more than 2 seconds
                    //  Python: '#e53e3e' if duration > 2000 else '#4a5568'
                    flexShrink: 0
                  }}>
                    {stage.duration_ms}ms
                  </div>

                  {/* Status badge */}
                  <div style={{
                    width: '70px',
                    flexShrink: 0
                  }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      backgroundColor: stage.status === 'SUCCESS' ? '#c6f6d5' : '#fed7d7',
                      color: stage.status === 'SUCCESS' ? '#276749' : '#9b2c2c'
                    }}>
                      {stage.status}
                    </span>
                  </div>

                </div>
              )
            })}
          </div>
        </div>
      )}

    </div>
  )
}

const badgeBlue = {
  padding: '4px 10px', borderRadius: '4px', fontSize: '12px',
  backgroundColor: '#ebf8ff', color: '#2b6cb0'
}
const badgeMono = {
  padding: '4px 10px', borderRadius: '4px', fontSize: '12px',
  backgroundColor: '#e9d8fd', color: '#553c9a', fontFamily: 'monospace'
}
const badgeGray = {
  padding: '4px 10px', borderRadius: '4px', fontSize: '12px',
  backgroundColor: '#edf2f7', color: '#4a5568'
}
const mlflowButton = {
  padding: '4px 12px', borderRadius: '4px', fontSize: '12px', fontWeight: '600',
  backgroundColor: '#0194e2', color: 'white', textDecoration: 'none', whiteSpace: 'nowrap'
}
const badgeStatus = {
  padding: '4px 10px', borderRadius: '4px', fontSize: '12px',
  fontWeight: '600'
}

export default TraceExplorer