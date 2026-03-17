import { useEffect, useMemo, useState, useCallback } from 'react'
import axios from 'axios'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import ChatView from './components/ChatView'
import Questions from './components/Questions'
import History from './components/History'
import Analytics from './components/Analytics'

const api = axios.create({
  baseURL: '/api/chat',
  timeout: 120000,
})

const PAGE_TITLES = {
  dashboard: 'Dashboard',
  chat: 'Chat',
  questions: 'APRM Questions',
  history: 'APRM History',
  analytics: 'APRM Analytics',
}

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Chat state
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  // Auto-submit from Questions page
  const [autoSubmit, setAutoSubmit] = useState(null)

  // Analytics & History state
  const [stats, setStats] = useState(null)
  const [sessions, setSessions] = useState([])

  const hasPending = useMemo(
    () => messages.some((m) => m.status === 'pending'),
    [messages],
  )

  // Create session on mount
  useEffect(() => {
    const createSession = async () => {
      try {
        const { data } = await api.post('/sessions/', {})
        setSessionId(data.session_id)
      } catch {
        setError('Could not start chat session. Ensure backend is running.')
      }
    }
    createSession()
  }, [])

  // Poll messages for current session
  useEffect(() => {
    if (!sessionId) return
    const poll = async () => {
      try {
        const { data } = await api.get(`/${sessionId}/`)
        setMessages(data.messages || [])
      } catch {
        /* silent */
      }
    }
    poll()
    const timer = setInterval(poll, 2000)
    return () => clearInterval(timer)
  }, [sessionId])

  // Fetch analytics
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const { data } = await api.get('/analytics/')
        setStats(data)
      } catch {
        /* silent */
      }
    }
    fetchStats()
    const timer = setInterval(fetchStats, 10000)
    return () => clearInterval(timer)
  }, [])

  // Fetch all sessions for history
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const { data } = await api.get('/sessions/all/')
        setSessions(data.sessions || [])
      } catch {
        /* silent */
      }
    }
    fetchSessions()
    const timer = setInterval(fetchSessions, 10000)
    return () => clearInterval(timer)
  }, [])

  // Submit query
  const sendQuery = useCallback(
    async (text) => {
      if (!text.trim() || !sessionId) return
      setSubmitting(true)
      setError('')
      try {
        await api.post('/query/', { session_id: sessionId, user_query: text.trim() })
      } catch {
        setError('Failed to submit query.')
      } finally {
        setSubmitting(false)
      }
    },
    [sessionId],
  )

  // Navigate to chat with a question (from Questions or Dashboard)
  const askQuestion = useCallback((text) => {
    setCurrentPage('chat')
    setAutoSubmit(text)
  }, [])

  // Load a historical session
  const loadSession = useCallback((id) => {
    setSessionId(id)
    setMessages([])
    setCurrentPage('chat')
  }, [])

  // New session
  const newSession = useCallback(async () => {
    try {
      const { data } = await api.post('/sessions/', {})
      setSessionId(data.session_id)
      setMessages([])
      setCurrentPage('chat')
    } catch {
      setError('Could not create session.')
    }
  }, [])

  return (
    <div className="flex h-screen bg-content">
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />

      {/* Main content */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-slate-200/80 px-4 md:px-6 py-3.5 flex items-center gap-4">
          <button
            className="lg:hidden p-2 rounded-xl hover:bg-slate-100 transition"
            onClick={() => setSidebarOpen(true)}
          >
            <svg className="w-5 h-5 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex-1">
            <h2 className="text-lg font-bold text-slate-800">{PAGE_TITLES[currentPage] || currentPage}</h2>
          </div>

          {currentPage === 'chat' && (
            <button
              onClick={newSession}
              className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-legal-600 to-legal-700 text-white text-xs font-bold rounded-xl hover:shadow-lg hover:shadow-legal-600/20 transition-all"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>
          )}

          {/* Session indicator */}
          {sessionId && (
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-legal-50 border border-legal-100">
              <div className="w-2 h-2 rounded-full bg-legal-600 animate-pulse" />
              <span className="text-[11px] font-semibold text-legal-700">Session #{sessionId}</span>
            </div>
          )}
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {currentPage === 'dashboard' && (
            <Dashboard stats={stats} setCurrentPage={setCurrentPage} askQuestion={askQuestion} />
          )}
          {currentPage === 'chat' && (
            <ChatView
              messages={messages}
              sendQuery={sendQuery}
              submitting={submitting}
              hasPending={hasPending}
              error={error}
              autoSubmit={autoSubmit}
              setAutoSubmit={setAutoSubmit}
              sessionId={sessionId}
            />
          )}
          {currentPage === 'questions' && <Questions askQuestion={askQuestion} />}
          {currentPage === 'history' && <History sessions={sessions} loadSession={loadSession} />}
          {currentPage === 'analytics' && <Analytics stats={stats} />}
        </main>
      </div>
    </div>
  )
}

export default App
