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

const statCards = [
  {
    key: 'total_sessions',
    label: 'Total Sessions',
    color: 'from-teal-500 to-teal-600',
    bg: 'bg-teal-50',
    text: 'text-teal-700',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
  {
    key: 'total_queries',
    label: 'Total Queries',
    color: 'from-blue-500 to-blue-600',
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
  },
  {
    key: 'completed_queries',
    label: 'Completed',
    color: 'from-emerald-500 to-emerald-600',
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    key: 'pending_queries',
    label: 'Pending',
    color: 'from-amber-500 to-amber-600',
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
]

const aprmSteps = [
  { letter: 'A', title: 'Analyze', desc: 'Parse user query, fix typos, detect intent', color: 'from-rose-500 to-rose-600' },
  { letter: 'P', title: 'Process', desc: 'Enrich query with entities & keywords', color: 'from-amber-500 to-amber-600' },
  { letter: 'R', title: 'Retrieve', desc: 'Vector search ChromaDB + keyword match', color: 'from-blue-500 to-blue-600' },
  { letter: 'M', title: 'Model', desc: 'LLM generates structured legal response', color: 'from-emerald-500 to-emerald-600' },
]

export default function Dashboard({ stats, setCurrentPage, askQuestion }) {
  const loading = !stats

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden bg-gradient-to-br from-legal-700 via-legal-600 to-emerald-600 rounded-2xl p-6 md:p-8 text-white">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/4" />
        <div className="relative z-10">
          <h2 className="text-2xl md:text-3xl font-bold">Welcome to Legal AI Dashboard</h2>
          <p className="mt-2 text-white/70 text-sm md:text-base max-w-xl">
            APRM-powered Indian Law Guidance System — Ask any legal question and get instant guidance with relevant laws, sections, and next steps.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <button
              onClick={() => setCurrentPage('chat')}
              className="px-5 py-2.5 bg-white text-legal-700 rounded-xl text-sm font-semibold hover:bg-legal-50 transition shadow-lg"
            >
              Start New Chat
            </button>
            <button
              onClick={() => setCurrentPage('questions')}
              className="px-5 py-2.5 bg-white/15 text-white rounded-xl text-sm font-semibold hover:bg-white/25 transition backdrop-blur"
            >
              Browse Questions
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <div key={card.key} className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className={`w-11 h-11 rounded-xl ${card.bg} ${card.text} flex items-center justify-center`}>
                {card.icon}
              </div>
              <span className={`text-2xl md:text-3xl font-bold ${card.text}`}>
                {loading ? '—' : (stats[card.key] ?? 0)}
              </span>
            </div>
            <p className="mt-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{card.label}</p>
            {!loading && card.key === 'completed_queries' && (
              <div className="mt-2 w-full bg-slate-100 rounded-full h-1.5">
                <div
                  className="bg-emerald-500 h-1.5 rounded-full transition-all"
                  style={{ width: `${stats.completion_rate || 0}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* APRM Pipeline */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 className="text-lg font-bold text-slate-800 mb-4">APRM Pipeline</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {aprmSteps.map((step, i) => (
            <div key={step.letter} className="relative">
              <div className="flex flex-col items-center text-center p-4 rounded-xl bg-slate-50 border border-slate-100">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${step.color} text-white flex items-center justify-center text-xl font-bold shadow-lg`}>
                  {step.letter}
                </div>
                <p className="mt-3 font-bold text-sm text-slate-800">{step.title}</p>
                <p className="mt-1 text-[11px] text-slate-500 leading-tight">{step.desc}</p>
              </div>
              {i < 3 && (
                <div className="hidden md:block absolute top-1/2 -right-3 -translate-y-1/2 text-slate-300 text-lg z-10">→</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity + Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Queries */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-800">Recent Queries</h3>
            <button
              onClick={() => setCurrentPage('history')}
              className="text-xs font-semibold text-legal-600 hover:text-legal-700"
            >
              View All →
            </button>
          </div>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-14 bg-slate-50 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : stats.recent_queries?.length > 0 ? (
            <div className="space-y-2">
              {stats.recent_queries.slice(0, 5).map((q) => (
                <div
                  key={q.id}
                  className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition cursor-pointer"
                  onClick={() => askQuestion(q.user_query)}
                >
                  <div
                    className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      q.status === 'completed' ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'
                    }`}
                  />
                  <p className="text-sm text-slate-700 font-medium truncate flex-1">{q.user_query}</p>
                  <span className="text-[11px] text-slate-400 whitespace-nowrap">{timeAgo(q.created_at)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center py-8">No queries yet. Start a conversation!</p>
          )}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            {[
              { label: 'New Chat Session', page: 'chat', emoji: '💬' },
              { label: 'Browse APRM Questions', page: 'questions', emoji: '❓' },
              { label: 'View History', page: 'history', emoji: '📋' },
              { label: 'Analytics Dashboard', page: 'analytics', emoji: '📊' },
            ].map((action) => (
              <button
                key={action.page}
                onClick={() => setCurrentPage(action.page)}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-50 hover:bg-legal-50 hover:border-legal-200 border border-slate-100 text-sm font-medium text-slate-700 transition-all"
              >
                <span className="text-lg">{action.emoji}</span>
                {action.label}
                <svg className="w-4 h-4 ml-auto text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            ))}
          </div>

          {/* Completion Rate */}
          {!loading && (
            <div className="mt-6 p-4 rounded-xl bg-gradient-to-br from-legal-50 to-emerald-50 border border-legal-100">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wide">Completion Rate</p>
              <p className="mt-1 text-3xl font-bold text-legal-700">{stats.completion_rate || 0}%</p>
              <div className="mt-2 w-full bg-white rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-legal-600 to-emerald-500 h-2 rounded-full transition-all"
                  style={{ width: `${stats.completion_rate || 0}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
