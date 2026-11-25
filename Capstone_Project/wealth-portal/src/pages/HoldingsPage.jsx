import { useState, useEffect } from 'react'
import { getPortfolios, getHoldings, getAssets, getTransactions, createTransaction } from '../api/api'
import { useParams } from 'react-router-dom'

//                                     ↑          ↑
//                              two new imports we just added

function HoldingsPage() {
  const [portfolios, setPortfolios] = useState([])
  const [selectedId, setSelectedId] = useState('')
  const [holdings, setHoldings] = useState(null)
  const [assets, setAssets] = useState([])
  const [transactions, setTransactions] = useState([])

    const [formAssetId, setFormAssetId] = useState('')
  //  Which asset the user picked in the form dropdown

  const [formType, setFormType] = useState('BUY')
  //  BUY or SELL — defaults to BUY

  const [formUnits, setFormUnits] = useState('')

  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  //  true while a transaction is being saved — stops double-clicks
  const { portfolioId } = useParams()



    useEffect(() => {
    async function loadInitial() {
      const [portfolioData, assetData] = await Promise.all([
        getPortfolios(),
        getAssets()
      ])

      setPortfolios(portfolioData)
      setAssets(assetData)

      // If portfolio ID is in the URL, auto-load it
      if (portfolioId) {
        setSelectedId(portfolioId)
        const [holdingsData, txnData] = await Promise.all([
          getHoldings(portfolioId),
          getTransactions(portfolioId)
        ])
        setHoldings(holdingsData)
        setTransactions(txnData)
      }
    }
    loadInitial()
  }, [portfolioId])

    // When user picks a portfolio from dropdown
  const loadPortfolioData = async (id) => {
    setSelectedId(id)

    if (!id) {
      // User selected "-- Select --" (empty option)
      setHoldings(null)
      setTransactions([])
      return
    }

    setLoading(true)

    const [holdingsData, txnData] = await Promise.all([
      getHoldings(id),
      getTransactions(id)
    ])

    setHoldings(holdingsData)
    setTransactions(txnData)
    setLoading(false)
  }

    // When user clicks "Submit Transaction"
  const handleSubmit = async () => {
    if (submitting) return


    if (!formAssetId || !formUnits) {
      setMessage({ type: 'error', text: 'Please fill all fields.' })
      return
    }

    const unitsNum = parseFloat(formUnits)


    if (unitsNum <= 0) {
      setMessage({ type: 'error', text: 'Units must be greater than zero.' })
      return
    }


    if (formType === 'SELL' && holdings) {
      const currentHolding = holdings.holdings.find(
        h => h.asset_id === parseInt(formAssetId)
      )


      if (!currentHolding) {
        setMessage({ type: 'error', text: "You don't own this asset!" })
        return
      }

      if (unitsNum > currentHolding.units) {
        setMessage({
          type: 'error',
          text: `Cannot sell ${unitsNum} units. You only own ${currentHolding.units}.`
        })
        return
      }
    }

    // --- Save it ---
    // The backend sets the price, records the transaction and updates the holding
    setSubmitting(true)
    let saved
    try {
      saved = await createTransaction(selectedId, {
        asset_id: parseInt(formAssetId),
        txn_type: formType,
        units: unitsNum
      })
    } catch (err) {
      // Backend's own reason, e.g. "Cannot sell 999 units of NVDA — only 50 owned"
      setMessage({ type: 'error', text: err.message })
      setSubmitting(false)
      return
    }

    // Reload holdings + history so units, values, weights and total are all up to date
    const [holdingsData, txnData] = await Promise.all([
      getHoldings(selectedId),
      getTransactions(selectedId)
    ])
    setHoldings(holdingsData)
    setTransactions(txnData)
    setSubmitting(false)

    setMessage({
      type: 'success',
      text: `${saved.txn_type} ${saved.units} units of ${saved.symbol} at $${saved.unit_price.toLocaleString()} recorded!`
    })

    // Reset form
    setFormAssetId('')
    setFormUnits('')

    // Clear message after 3 seconds
    setTimeout(() => setMessage(null), 3000)
  }
    return (
    <div>
      <h1>Holdings & Transactions</h1>

      {/* Portfolio selector — same as Insights page */}
      <select
        value={selectedId}
        onChange={(e) => loadPortfolioData(e.target.value)}
        style={selectStyle}
      >
        <option value="">-- Select a portfolio --</option>
        {portfolios.map(p => (
          <option key={p.portfolio_id} value={p.portfolio_id}>
            {p.portfolio_name}
          </option>
        ))}
      </select>

      {/* Alert message — appears after submitting a transaction */}
      {message && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '8px',
          marginTop: '16px',
          backgroundColor: message.type === 'success' ? '#c6f6d5' : '#fed7d7',
          color: message.type === 'success' ? '#276749' : '#9b2c2c',
          fontSize: '14px'
        }}>
          {message.text}
        </div>
      )}

      {loading && <p>Loading...</p>}

            {/* ========= SECTION 1: Current Holdings ========= */}
      {holdings && (
        <div style={{ marginTop: '24px' }}>
          <h2>
            Current Holdings
            <span style={{ fontSize: '16px', color: '#718096', marginLeft: '12px' }}>
              Total: ${holdings.total_value.toLocaleString()}
            </span>
            {/*
              .toLocaleString() turns 148255 into "148,255"
              Python equivalent: f"{148255:,}"
            */}
          </h2>

          <table style={tableStyle}>
            <thead>
              <tr style={headerRow}>
                <th style={cellStyle}>Symbol</th>
                <th style={cellStyle}>Name</th>
                <th style={cellStyle}>Class</th>
                <th style={cellStyle}>Units</th>
                <th style={cellStyle}>Price</th>
                <th style={cellStyle}>Value</th>
                <th style={cellStyle}>Weight</th>
              </tr>
            </thead>
            <tbody>
              {holdings.holdings.map(h => (
                <tr key={h.holding_id} style={bodyRow}>
                  <td style={{ ...cellStyle, fontWeight: '600' }}>{h.symbol}</td>
                  <td style={cellStyle}>{h.asset_name}</td>
                  <td style={cellStyle}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      backgroundColor: '#edf2f7',
                      color: '#4a5568'
                    }}>
                      {h.asset_class}
                    </span>
                  </td>
                  <td style={cellStyle}>{h.units}</td>
                  <td style={cellStyle}>${h.synthetic_reference_price.toLocaleString()}</td>
                  <td style={cellStyle}>${h.value.toLocaleString()}</td>
                  <td style={{ ...cellStyle, fontWeight: '600' }}>{h.weight_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

            {/* ========= SECTION 2: Transaction Form ========= */}
      {selectedId && (
        <div style={{
          marginTop: '32px',
          padding: '20px',
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          backgroundColor: '#f7fafc'
        }}>
          <h2 style={{ marginTop: 0 }}>New Transaction</h2>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            {/*
              "flex-end" aligns all items to the BOTTOM of the row
              so the button lines up with the input fields even though
              labels make some items taller
            */}

            {/* Asset dropdown */}
            <div>
              <label style={labelStyle}>Asset</label>
              <select
                value={formAssetId}
                onChange={(e) => setFormAssetId(e.target.value)}
                style={selectStyle}
              >
                <option value="">-- Pick asset --</option>
                {assets.map(a => (
                  <option key={a.asset_id} value={a.asset_id}>
                    {a.symbol} — {a.asset_name}
                  </option>
                ))}
              </select>
            </div>

            {/* BUY / SELL selector */}
            <div>
              <label style={labelStyle}>Type</label>
              <select
                value={formType}
                onChange={(e) => setFormType(e.target.value)}
                style={selectStyle}
              >
                <option value="BUY">BUY</option>
                <option value="SELL">SELL</option>
              </select>
            </div>

            {/* Units input */}
            <div>
              <label style={labelStyle}>Units</label>
              <input
                type="number"
                min="0"
                step="0.01"
                placeholder="e.g. 50"
                value={formUnits}
                onChange={(e) => setFormUnits(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #cbd5e0',
                  fontSize: '14px',
                  width: '120px'
                }}
              />
              {/*
                type="number" — only allows digits
                min="0" — no negative numbers
                step="0.01" — allows decimals like 2.5
              */}
            </div>

            {/* Price display — auto-filled, not editable */}
            <div>
              <label style={labelStyle}>Price (auto)</label>
              <div style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #e2e8f0',
                backgroundColor: '#edf2f7',
                fontSize: '14px',
                color: '#718096',
                minWidth: '100px'
              }}>
                {formAssetId
                  ? `$${assets.find(a => a.asset_id === parseInt(formAssetId))
                      ?.synthetic_reference_price.toLocaleString()}`
                  : '—'
                }
              </div>
              {/*
                ↑ This is a "computed display" — not an input
                
                When user picks AAPL, it shows "$189.50" automatically
                The ?. is called "optional chaining":
                
                assets.find(...)?.synthetic_reference_price
                
                means: "if find() returns something, get its price"
                        "if find() returns nothing, don't crash"
                
                Python equivalent:
                asset = next((a for a in assets if ...), None)
                price = asset.synthetic_reference_price if asset else '—'
              */}
            </div>

            {/* Submit button */}
            <button
              onClick={handleSubmit}
              disabled={submitting}
              style={{
                padding: '8px 24px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: formType === 'BUY' ? '#38a169' : '#e53e3e',
                //  Green for BUY, Red for SELL — visual cue!
                color: 'white',
                fontSize: '14px',
                cursor: 'pointer',
                height: '38px'
              }}
            >
              {submitting ? 'Saving...' : formType === 'BUY' ? '📈 Buy' : '📉 Sell'}
            </button>
          </div>
        </div>
      )}


            {/* ========= SECTION 3: Transaction History ========= */}
      {transactions.length > 0 && (
        <div style={{ marginTop: '32px' }}>
          <h2>Transaction History</h2>

          <table style={tableStyle}>
            <thead>
              <tr style={headerRow}>
                <th style={cellStyle}>Date</th>
                <th style={cellStyle}>Asset</th>
                <th style={cellStyle}>Type</th>
                <th style={cellStyle}>Units</th>
                <th style={cellStyle}>Price</th>
                <th style={cellStyle}>Value</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(txn => (
                <tr key={txn.txn_id} style={bodyRow}>
                  <td style={cellStyle}>
                    {new Date(txn.occurred_at).toLocaleDateString()}
                    {/*
                      Turns "2026-02-10T10:00:00" into "2/10/2026"
                      
                      Python equivalent:
                      datetime.fromisoformat(txn['occurred_at']).strftime('%m/%d/%Y')
                    */}
                  </td>
                  <td style={{ ...cellStyle, fontWeight: '600' }}>{txn.symbol}</td>
                  <td style={cellStyle}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: '600',
                      backgroundColor: txn.txn_type === 'BUY' ? '#c6f6d5' : '#fed7d7',
                      color: txn.txn_type === 'BUY' ? '#276749' : '#9b2c2c'
                    }}>
                      {txn.txn_type}
                    </span>
                  </td>
                  <td style={cellStyle}>{txn.units}</td>
                  <td style={cellStyle}>${txn.unit_price.toLocaleString()}</td>
                  <td style={{ ...cellStyle, fontWeight: '600' }}>
                    ${txn.transaction_value.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </div>
  )
}

// Styles
const selectStyle = {
  padding: '8px 12px',
  borderRadius: '6px',
  border: '1px solid #cbd5e0',
  fontSize: '14px',
}
const labelStyle = {
  display: 'block',
  fontSize: '12px',
  color: '#718096',
  marginBottom: '4px'
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

export default HoldingsPage