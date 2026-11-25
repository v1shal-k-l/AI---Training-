import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getRuns, getFeedback, submitFeedback } from '../api/api'

function FeedbackPage() {

  // --- Data states ---
  const [runs, setRuns] = useState([])
  const [feedbackList, setFeedbackList] = useState([])
  //  ↑ "feedbackList" not "feedback" — because "feedback"
  //  could clash with the form state below

  // --- Form states ---
  // Run ID from the URL, e.g. /feedback/1 → "1" (undefined on plain /feedback)
  const { runId } = useParams()

  const [selectedRunId, setSelectedRunId] = useState(runId ?? '')
  //  ↑ opened from "Give Feedback" on the Insights page → that run is pre-selected
  const [helpful, setHelpful] = useState(null)
  //  ↑ null = not chosen yet
  //  true = helpful, false = not helpful
  //  Three possible values, not just two!

  const [comment, setComment] = useState('')

  // --- UI states ---
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState(null)

    useEffect(() => {
    async function loadData() {
      const [runsData, feedbackData] = await Promise.all([
        getRuns(),
        getFeedback()
      ])
      setRuns(runsData)
      setFeedbackList(feedbackData)
      setLoading(false)
    }
    loadData()
  }, [])

  const handleSubmit = async () => {
    // Validate
    if (!selectedRunId) {
      setMessage({ type: 'error', text: 'Please select a run to review.' })
      return
    }
    if (helpful === null) {
      setMessage({ type: 'error', text: 'Please select Helpful or Not Helpful.' })
      return
    }

    let saved
    try {
      saved = await submitFeedback(selectedRunId, {
        helpful: helpful,
        reviewer_comment: comment || null
      })
    } catch {
      setMessage({ type: 'error', text: 'Could not save feedback. Check that the backend is running.' })
      return
    }

    // Show the saved review at the top. If this run was reviewed before,
    // drop the old entry — the backend replaced it.
    setFeedbackList([saved, ...feedbackList.filter(f => f.run_id !== saved.run_id)])

    // Show success and reset form
    setMessage({ type: 'success', text: 'Feedback submitted! Thank you.' })
    setSelectedRunId('')
    setHelpful(null)
    setComment('')

    setTimeout(() => setMessage(null), 3000)
  }

    if (loading) return <p>Loading feedback data...</p>

  return (
    <div>
      <h1>Reviewer Feedback</h1>


            {/* ========= FEEDBACK FORM ========= */}
      <div style={{
        padding: '24px',
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        backgroundColor: '#f7fafc',
        marginBottom: '32px'
      }}>
        <h2 style={{ marginTop: 0 }}>Review an AI Run</h2>

        {/* Alert message */}
        {message && (
          <div style={{
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '16px',
            backgroundColor: message.type === 'success' ? '#c6f6d5' : '#fed7d7',
            color: message.type === 'success' ? '#276749' : '#9b2c2c',
            fontSize: '14px'
          }}>
            {message.text}
          </div>
        )}

        {/* Run selector — only show successful runs (no point reviewing failures) */}
        <div style={{ marginBottom: '16px' }}>
          <label style={labelStyle}>Select AI Run</label>
          <select
            value={selectedRunId}
            onChange={(e) => setSelectedRunId(e.target.value)}
            style={{ ...selectStyle, width: '100%' }}
          >
            <option value="">-- Pick a run to review --</option>
            {runs
              .filter(r => r.status === 'SUCCESS')
              //  ↑
              //  .filter() keeps only items that match
              //  Python equivalent:
              //  [r for r in runs if r['status'] == 'SUCCESS']
              //
              //  We only show successful runs — failed runs
              //  have no AI output to review!
              .map(r => (
                <option key={r.run_id} value={r.run_id}>
                  Run R-{r.run_id} · {r.model_id} · {r.latency_ms}ms ·{' '}
                  {new Date(r.created_at).toLocaleDateString()}
                </option>
              ))
            }
          </select>
        </div>

        {/* Helpful / Not Helpful buttons */}
        <div style={{ marginBottom: '16px' }}>
          <label style={labelStyle}>Was this insight helpful?</label>
          <div style={{ display: 'flex', gap: '12px' }}>

            <button
              onClick={() => setHelpful(true)}
              style={{
                padding: '10px 24px',
                borderRadius: '8px',
                border: '2px solid',
                fontSize: '14px',
                cursor: 'pointer',
                borderColor: helpful === true ? '#38a169' : '#e2e8f0',
                backgroundColor: helpful === true ? '#c6f6d5' : 'white',
                color: helpful === true ? '#276749' : '#4a5568'
        
              }}
            >
              👍 Helpful
            </button>

            <button
              onClick={() => setHelpful(false)}
              style={{
                padding: '10px 24px',
                borderRadius: '8px',
                border: '2px solid',
                fontSize: '14px',
                cursor: 'pointer',
                borderColor: helpful === false ? '#e53e3e' : '#e2e8f0',
                backgroundColor: helpful === false ? '#fed7d7' : 'white',
                color: helpful === false ? '#9b2c2c' : '#4a5568'
              }}
            >
              👎 Not Helpful
            </button>
          </div>
        </div>

        {/* Comment textarea */}
        <div style={{ marginBottom: '16px' }}>
          <label style={labelStyle}>Correction note (optional)</label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="e.g., Allocation percentages didn't match the chart..."
            rows={3}
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: '6px',
              border: '1px solid #cbd5e0',
              fontSize: '14px',
              resize: 'vertical',
              fontFamily: 'inherit'
            }}
          />

        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          style={{
            padding: '10px 32px',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: '#4299e1',
            color: 'white',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          Submit Feedback
        </button>
      </div>

      {/* ========= FEEDBACK HISTORY ========= */}
      <h2>Feedback History</h2>

      {feedbackList.length === 0 ? (
        <p style={{ color: '#a0aec0' }}>No feedback recorded yet.</p>
      ) : (
        //  ↑
        //  This is a TERNARY used as conditional rendering
        //  condition ? (show this) : (show that)
        //
        //  Python equivalent:
        //  if len(feedback_list) == 0:
        //      show "No feedback yet"
        //  else:
        //      show the table

        <table style={tableStyle}>
          <thead>
            <tr style={headerRow}>
              <th style={cellStyle}>Run ID</th>
              <th style={cellStyle}>Rating</th>
              <th style={cellStyle}>Comment</th>
              <th style={cellStyle}>Reviewed</th>
            </tr>
          </thead>
          <tbody>
            {feedbackList.map(fb => (
              <tr key={fb.feedback_id} style={bodyRow}>
                <td style={{ ...cellStyle, fontWeight: '600' }}>R-{fb.run_id}</td>
                <td style={cellStyle}>
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: '600',
                    backgroundColor: fb.helpful ? '#c6f6d5' : '#fed7d7',
                    color: fb.helpful ? '#276749' : '#9b2c2c'
                  }}>
                    {fb.helpful ? '👍 Helpful' : '👎 Not Helpful'}
                  </span>
                </td>
                <td style={{ ...cellStyle, color: fb.reviewer_comment ? '#1a202c' : '#a0aec0' }}>
                  {fb.reviewer_comment || '— no comment —'}
                  {/*
                    ↑ If comment is null, show placeholder text
                    || means "if left side is falsy, use right side"
                    
                    null is falsy, so null || "— no comment —"
                    gives us "— no comment —"
                    
                    Python equivalent:
                    fb.reviewer_comment or "— no comment —"
                  */}
                </td>
                <td style={{ ...cellStyle, color: '#718096', fontSize: '13px' }}>
                  {new Date(fb.reviewed_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

    </div>
  )
}


const selectStyle = {
  padding: '8px 12px',
  borderRadius: '6px',
  border: '1px solid #cbd5e0',
  fontSize: '14px',
}
const labelStyle = {
  display: 'block',
  fontSize: '13px',
  color: '#718096',
  marginBottom: '6px',
  fontWeight: '500'
}
const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
}
const headerRow = {
  borderBottom: '2px solid #e2e8f0',
  textAlign: 'left',
}
const bodyRow = {
  borderBottom: '1px solid #f0f0f0',
}
const cellStyle = {
  padding: '10px 8px',
  fontSize: '14px',
}

export default FeedbackPage
