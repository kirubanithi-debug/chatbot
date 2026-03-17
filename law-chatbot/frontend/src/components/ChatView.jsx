import { useEffect, useRef, useState } from 'react'

const popularQuestions = [
  'How to file FIR?',
  'Cyber complaint website?',
  'Police emergency number?',
  'Women helpline number?',
  'Bike stolen complaint',
  'Salary not paid',
  'Land encroachment',
  'Domestic violence help',
]

function parseAIResponse(text) {
  if (!text) return null
  const fields = {}
  const lines = text.split('\n')
  for (const line of lines) {
    const match = line.match(/^(LAW|SECTION|PUNISHMENT|NEXT STEPS|DISCLAIMER):\s*(.+)/i)
    if (match) {
      fields[match[1].toUpperCase()] = match[2].trim()
    }
  }
  return Object.keys(fields).length >= 2 ? fields : null
}

const fieldConfig = {
  LAW: { label: 'Law', color: 'bg-blue-50 text-blue-700 border-blue-200', icon: '📜' },
  SECTION: { label: 'Section', color: 'bg-purple-50 text-purple-700 border-purple-200', icon: '📋' },
  PUNISHMENT: { label: 'Punishment', color: 'bg-red-50 text-red-700 border-red-200', icon: '⚖️' },
  'NEXT STEPS': { label: 'Next Steps', color: 'bg-emerald-50 text-emerald-700 border-emerald-200', icon: '✅' },
  DISCLAIMER: { label: 'Disclaimer', color: 'bg-amber-50 text-amber-700 border-amber-200', icon: '⚠️' },
}

function AIResponseCard({ text }) {
  const parsed = parseAIResponse(text)

  if (!parsed) {
    return <pre className="whitespace-pre-wrap text-sm text-slate-700 leading-relaxed">{text}</pre>
  }

  return (
    <div className="space-y-2">
      {Object.entries(parsed).map(([key, value]) => {
        const config = fieldConfig[key] || { label: key, color: 'bg-slate-50 text-slate-700 border-slate-200', icon: '📌' }
        return (
          <div key={key} className={`flex items-start gap-2 p-2.5 rounded-lg border ${config.color}`}>
            <span className="text-sm mt-0.5">{config.icon}</span>
            <div className="min-w-0 flex-1">
              <span className="text-[10px] font-bold uppercase tracking-wider opacity-70">{config.label}</span>
              <p className="text-sm font-medium leading-snug mt-0.5">{value}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default function ChatView({ messages, sendQuery, submitting, hasPending, error, autoSubmit, setAutoSubmit, sessionId }) {
  const [query, setQuery] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle auto-submit from Questions page
  useEffect(() => {
    if (autoSubmit && sessionId && !submitting) {
      sendQuery(autoSubmit)
      setAutoSubmit(null)
    }
  }, [autoSubmit, sessionId, submitting, sendQuery, setAutoSubmit])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!query.trim()) return
    sendQuery(query.trim())
    setQuery('')
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto rounded-2xl bg-white border border-slate-200 shadow-sm">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-6 py-12">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-legal-600 to-emerald-500 flex items-center justify-center mb-5 shadow-lg shadow-legal-600/20">
              <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-slate-800">Indian Legal AI Assistant</h3>
            <p className="mt-2 text-sm text-slate-500 max-w-md">
              Ask any legal question and get guidance with relevant Indian laws, sections, punishments, and next steps.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2 max-w-lg">
              {popularQuestions.map((q) => (
                <button
                  key={q}
                  onClick={() => sendQuery(q)}
                  disabled={submitting}
                  className="px-3 py-1.5 rounded-full bg-legal-50 border border-legal-100 text-xs font-semibold text-legal-700 hover:bg-legal-100 hover:border-legal-200 transition disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-4 space-y-4">
            {messages.map((m) => (
              <div key={m.id} className="space-y-3">
                {/* User Message */}
                <div className="flex justify-end">
                  <div className="max-w-[80%] flex items-start gap-2">
                    <div className="bg-gradient-to-br from-legal-600 to-legal-700 text-white px-4 py-3 rounded-2xl rounded-tr-md shadow-sm">
                      <p className="text-sm font-medium">{m.user_query}</p>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-legal-100 flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-legal-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                  </div>
                </div>

                {/* AI Response */}
                <div className="flex justify-start">
                  <div className="max-w-[85%] flex items-start gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-legal-600 to-emerald-500 flex items-center justify-center flex-shrink-0 shadow-sm">
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                      </svg>
                    </div>
                    <div className="bg-white border border-slate-200 px-4 py-3 rounded-2xl rounded-tl-md shadow-sm">
                      {m.status === 'pending' ? (
                        <div className="flex items-center gap-2">
                          <div className="flex gap-1">
                            <div className="w-2 h-2 rounded-full bg-legal-600 animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 rounded-full bg-legal-600 animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 rounded-full bg-legal-600 animate-bounce" style={{ animationDelay: '300ms' }} />
                          </div>
                          <span className="text-xs text-amber-600 font-medium">Analyzing with APRM + RAG...</span>
                        </div>
                      ) : (
                        <AIResponseCard text={m.ai_response} />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="mt-4">
        {hasPending && (
          <div className="mb-2 flex items-center gap-2 px-1">
            <div className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
            <p className="text-xs text-slate-500">AI is processing your query...</p>
          </div>
        )}
        {error && (
          <div className="mb-2 px-3 py-2 rounded-lg bg-red-50 border border-red-200">
            <p className="text-xs text-red-700">{error}</p>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            ref={inputRef}
            className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none ring-legal-600/30 focus:ring-2 focus:border-legal-400 shadow-sm transition placeholder:text-slate-400"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type your legal question here..."
            disabled={submitting || !sessionId}
          />
          <button
            type="submit"
            disabled={submitting || !sessionId || !query.trim()}
            className="px-5 py-3 bg-gradient-to-r from-legal-600 to-legal-700 text-white rounded-xl font-semibold text-sm shadow-lg shadow-legal-600/20 hover:shadow-legal-600/30 disabled:from-slate-300 disabled:to-slate-400 disabled:shadow-none transition-all flex items-center gap-2"
          >
            {submitting ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Sending
              </>
            ) : (
              <>
                Send
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
