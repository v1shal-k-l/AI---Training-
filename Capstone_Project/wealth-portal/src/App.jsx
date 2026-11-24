import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import PortfolioOverview from './pages/PortfolioOverview'
import HoldingsPage from './pages/HoldingsPage'
import InsightsPage from './pages/InsightsPage'
import DashboardPage from './pages/DashboardPage'
import TraceExplorer from './pages/TraceExplorer'
import FeedbackPage from './pages/FeedbackPage'


// Starting theme: the user's last choice, otherwise their OS setting
function initialTheme() {
  try {
    const saved = localStorage.getItem('theme')
    if (saved === 'light' || saved === 'dark') return saved
  } catch {
    // storage blocked (private window etc.) — fall through
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function App() {
  const [theme, setTheme] = useState(initialTheme)

  // Put the theme on <html data-theme="..."> so App.css can switch colors
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    try {
      localStorage.setItem('theme', theme)
    } catch {
      // not saved — the toggle still works for this visit
    }
  }, [theme])

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark')

  return (
    <BrowserRouter>
      <nav style={{ display: 'flex', gap: '16px', padding: '16px', 
                     borderBottom: '1px solid #e2e8f0' }}>
        <NavLink to="/">Portfolio</NavLink>
        <NavLink to="/holdings">Holdings</NavLink>
        <NavLink to="/insights">AI Insights</NavLink>
        <NavLink to="/dashboard">Observability</NavLink>
        <NavLink to="/trace">Trace Explorer</NavLink>
        <NavLink to="/feedback">Feedback</NavLink>
        <button
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </nav>

      <main style={{ padding: '24px' }}>
        <Routes>
          <Route path="/" element={<PortfolioOverview />} />
          <Route path="/feedback/:runId?" element={<FeedbackPage />} />
          <Route path="/holdings/:portfolioId?" element={<HoldingsPage />} />
          <Route path="/insights/:portfolioId?" element={<InsightsPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/trace/:runId?" element={<TraceExplorer />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App