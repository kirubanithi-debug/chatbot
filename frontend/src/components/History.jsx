import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/chat',
  timeout: 120000,
})

function timeAgo(date) {
  if (!date) return ''
  const seconds = Math.floor((new Date() - new Date(date)) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function History({ sessions, loadSession }) {
  const [expandedSession, setExpandedSession] = useState(null)
  const [sessionMessages, setSessionMessages] = useState({})
  const [loadingMessages, setLoadingMessages] = useState(null)
  const [search, setSearch] = useState('')

  const fetchSessionMessages = useCallback(async (sessionId) => {
    if (sessionMessages[sessionId]) return
    setLoadingMessages(sessionId)
    try {
      const { data } = await api.get(`/${sessionId}/`)
      setSessionMessages((prev) => ({ ...prev, [sessionId]: data.messages || [] }))
    } catch {
      // Silently fail
    } finally {
      setLoadingMessages(null)
    }
  }, [sessionMessages])

  const toggleSession = (id) => {
    if (expandedSession === id) {
      setExpandedSession(null)
    } else {
      setExpandedSession(id)
      fetchSessionMessages(id)
    }
  }

  const filteredSessions = sessions.filter((s) => {
    if (!search.trim()) return true
    const term = search.toLowerCase()
    return (
      s.last_query?.toLowerCase().includes(term) ||
      `session #${s.id}`.includes(term)
    )
  })

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">APRM History</h2>
          <p className="text-sm text-slate-500 mt-1">
            {sessions.length} total sessions
          </p>
        </div>
        <div className="relative">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search sessions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:ring-2 ring-legal-600/20 focus:border-legal-400 outline-none w-full sm:w-72 shadow-sm"
          />
        </div>
      </div>

      {/* Sessions List */}
      {filteredSessions.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-slate-200">
          <svg className="w-16 h-16 mx-auto text-slate-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="mt-4 text-slate-400 text-sm">
            {search ? `No sessions matching "${search}"` : 'No chat sessions yet. Start a new chat!'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredSessions.map((session) => {
            const isExpanded = expandedSession === session.id
            const msgs = sessionMessages[session.id] || []
            const isLoading = loadingMessages === session.id

            return (
              <div
                key={session.id}
                className={`bg-white rounded-2xl border transition-all overflow-hidden ${
                  isExpanded ? 'border-legal-200 shadow-md' : 'border-slate-200 shadow-sm hover:shadow-md'
                }`}
              >
                {/* Session Header */}
                <button
                  onClick={() => toggleSession(session.id)}
                  className="w-full flex items-center gap-4 p-4 text-left"
                >
                  <div className={`w-11 h-11 rounded-xl flex items-center justify-center text-sm font-bold ${
                    session.pending_count > 0
                      ? 'bg-amber-50 text-amber-700'
                      : 'bg-legal-50 text-legal-700'
                  }`}>
                    #{session.id}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-sm text-slate-800 truncate">
                        {session.last_query || 'Empty session'}
                      </h3>
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-[11px] text-slate-400">{timeAgo(session.created_at)}</span>
                      <span className="text-[11px] text-slate-300">•</span>
                      <span className="text-[11px] text-slate-500">{session.query_count} queries</span>
                      <span className="text-[11px] text-slate-300">•</span>
                      <span className={`text-[11px] font-semibold ${
                        session.pending_count > 0 ? 'text-amber-600' : 'text-emerald-600'
                      }`}>
                        {session.pending_count > 0 ? `${session.pending_count} pending` : 'All completed'}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        loadSession(session.id)
                      }}
                      className="px-3 py-1.5 bg-legal-50 text-legal-700 text-[11px] font-bold rounded-lg hover:bg-legal-100 transition"
                    >
                      Load
                    </button>
                    <svg
                      className={`w-4 h-4 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>

                {/* Expanded Messages */}
                {isExpanded && (
                  <div className="border-t border-slate-100 bg-slate-50/50 px-4 py-3">
                    {isLoading ? (
                      <div className="space-y-2">
                        {[1, 2].map((i) => (
                          <div key={i} className="h-16 bg-slate-100 rounded-xl animate-pulse" />
                        ))}
                      </div>
                    ) : msgs.length === 0 ? (
                      <p className="text-xs text-slate-400 text-center py-4">No messages in this session</p>
                    ) : (
                      <div className="space-y-2">
                        {msgs.map((m) => (
                          <div key={m.id} className="bg-white rounded-xl p-3 border border-slate-100">
                            <div className="flex items-start justify-between gap-2">
                              <p className="text-xs font-semibold text-legal-700">{m.user_query}</p>
                              <div className="flex items-center gap-1.5 flex-shrink-0">
                                <div className={`w-1.5 h-1.5 rounded-full ${
                                  m.status === 'completed' ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'
                                }`} />
                                <span className="text-[10px] text-slate-400">{timeAgo(m.created_at)}</span>
                              </div>
                            </div>
                            {m.ai_response && (
                              <pre className="mt-2 whitespace-pre-wrap text-[11px] text-slate-600 leading-relaxed bg-slate-50 rounded-lg p-2">
                                {m.ai_response}
                              </pre>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="mt-3 flex items-center justify-between">
                      <span className="text-[10px] text-slate-400">Session created: {formatDate(session.created_at)}</span>
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 text-[10px] font-bold text-emerald-700">
                          {session.completed_count} done
                        </span>
                        {session.pending_count > 0 && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-50 text-[10px] font-bold text-amber-700">
                            {session.pending_count} pending
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
