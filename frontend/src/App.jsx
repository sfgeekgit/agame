import { useState, useEffect, useCallback } from 'react'

const API_BASE = '/agame/api'
const CONTENT_BASE = '/agame/content'

function getCsrfToken() {
  const match = document.cookie.match(/agame_csrf=([^;]+)/)
  return match ? match[1] : ''
}

function App() {
  const [user, setUser] = useState(null)
  const [ui, setUi] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [clicking, setClicking] = useState(false)

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/user/me/`, { credentials: 'include' }).then(r => r.json()),
      fetch(`${CONTENT_BASE}/ui.json`).then(r => r.json()),
    ])
      .then(([userData, uiData]) => {
        setUser(userData)
        setUi(uiData)
        document.title = uiData.title
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const addPoints = useCallback(async (amount) => {
    setClicking(true)
    try {
      const res = await fetch(`${API_BASE}/user/me/points/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ amount }),
      })
      const data = await res.json()
      setUser(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setClicking(false)
    }
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <p className="text-xl">{ui?.loading ?? ''}</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-red-400">
        <p className="text-xl">{ui?.errorPrefix ?? 'Error:'} {error}</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center gap-8 p-4">
      <h1 className="text-4xl font-bold">{ui.title}</h1>

      <div className="text-6xl font-mono font-bold text-yellow-400">
        {user?.points ?? 0} {ui.pointsLabel}
      </div>

      <div className="flex gap-4 flex-wrap justify-center">
        {ui.buttons.map((btn) => (
          <button
            key={btn.amount}
            onClick={() => addPoints(btn.amount)}
            disabled={clicking}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-lg text-lg font-semibold transition-colors cursor-pointer"
          >
            {btn.label}
          </button>
        ))}
      </div>

      <p className="text-sm text-gray-500 mt-8">
        {ui.userLabel} {user?.user_id?.slice(0, 8)}...
      </p>
    </div>
  )
}

export default App
