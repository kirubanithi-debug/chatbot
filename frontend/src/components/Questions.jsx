import { useState, useMemo } from 'react'

const questionCategories = [
  {
    id: 'general',
    title: 'General',
    emoji: '💬',
    gradient: 'from-slate-500 to-slate-600',
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    questions: ['Hi', 'What can you do?', 'Police emergency number?'],
  },
  {
    id: 'police',
    title: 'Police & FIR',
    emoji: '🚔',
    gradient: 'from-red-500 to-red-600',
    bg: 'bg-red-50',
    border: 'border-red-200',
    questions: ['How to file FIR?', 'Chain snatching complaint', 'Mobile stolen and SIM misuse'],
  },
  {
    id: 'women_child',
    title: 'Women & Child Safety',
    emoji: '🛡️',
    gradient: 'from-pink-500 to-pink-600',
    bg: 'bg-pink-50',
    border: 'border-pink-200',
    questions: [
      'Women helpline number?',
      'Women safety harassment complaint',
      'Bad touch complaint',
      'Child safety abuse complaint',
      'Marriage and dowry harassment',
    ],
  },
  {
    id: 'family',
    title: 'Family & Property',
    emoji: '🏠',
    gradient: 'from-blue-500 to-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    questions: [
      'Divorce case with husband/wife',
      'Family land dispute with brother',
      'Family vehicle ownership dispute',
      'Neighbor encroached my land',
      'Illegal construction near my home',
      'House owner forcing tenant to vacate',
      'House owner denied water supply',
    ],
  },
  {
    id: 'civic',
    title: 'Civic & Infrastructure',
    emoji: '🏗️',
    gradient: 'from-orange-500 to-orange-600',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    questions: [
      'No road in my street',
      'Drainage overflow near my house',
      'Street light not working in my area',
      'Water supply issue in my street',
      'Garbage was not collected complaint',
      'Drainage was not clean complaint',
    ],
  },
  {
    id: 'transport',
    title: 'Transport & Traffic',
    emoji: '🚌',
    gradient: 'from-yellow-500 to-yellow-600',
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    questions: [
      'Private bus overcharge complaint',
      'Government bus unsafe service',
      'Accident injury compensation',
      'No helmet traffic fine',
    ],
  },
  {
    id: 'cyber',
    title: 'Cyber & Fraud',
    emoji: '💻',
    gradient: 'from-indigo-500 to-indigo-600',
    bg: 'bg-indigo-50',
    border: 'border-indigo-200',
    questions: ['Cyber complaint website?'],
  },
  {
    id: 'electricity',
    title: 'Electricity & Telecom',
    emoji: '⚡',
    gradient: 'from-amber-500 to-amber-600',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    questions: [
      'Wrong EB electricity bill',
      'Frequent power cut in my area',
      'Low voltage in my street',
      'No signal and call drop complaint',
    ],
  },
  {
    id: 'health',
    title: 'Health & Education',
    emoji: '🏥',
    gradient: 'from-teal-500 to-teal-600',
    bg: 'bg-teal-50',
    border: 'border-teal-200',
    questions: [
      'Hospital denied treatment',
      'College fee paid but no facilities',
      'Fake doctor complaint',
      'Fake medicine complaint',
    ],
  },
  {
    id: 'government',
    title: 'Government & Legal',
    emoji: '🏛️',
    gradient: 'from-emerald-500 to-emerald-600',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    questions: [
      'Panchayat no water tank complaint',
      'Town municipality civic complaint',
      'City corporation civic complaint',
      'MLA/MP not responding complaint',
      'Political election threat complaint',
      'Temple trust money misuse complaint',
      'Temple religious insult complaint',
    ],
  },
  {
    id: 'environment',
    title: 'Environment',
    emoji: '🌿',
    gradient: 'from-green-500 to-green-600',
    bg: 'bg-green-50',
    border: 'border-green-200',
    questions: [
      'Noise pollution complaint',
      'Air pollution complaint',
      'Land pollution complaint',
      'Illegal tree cutting complaint',
      'Natural disaster relief complaint',
    ],
  },
  {
    id: 'finance',
    title: 'Finance & Employment',
    emoji: '💰',
    gradient: 'from-violet-500 to-violet-600',
    bg: 'bg-violet-50',
    border: 'border-violet-200',
    questions: [
      'Private company salary due',
      'Home loan not approved by bank',
      'Agriculture crop loss compensation',
    ],
  },
  {
    id: 'safety',
    title: 'Personal Safety',
    emoji: '⚖️',
    gradient: 'from-rose-500 to-rose-600',
    bg: 'bg-rose-50',
    border: 'border-rose-200',
    questions: [
      'Caste abuse in public place',
      'Elder safety maintenance complaint',
      'Men safety blackmail complaint',
    ],
  },
]

export default function Questions({ askQuestion }) {
  const [search, setSearch] = useState('')
  const [expandedCategories, setExpandedCategories] = useState(new Set(questionCategories.map((c) => c.id)))

  const filteredCategories = useMemo(() => {
    if (!search.trim()) return questionCategories
    const term = search.toLowerCase()
    return questionCategories
      .map((cat) => ({
        ...cat,
        questions: cat.questions.filter((q) => q.toLowerCase().includes(term)),
      }))
      .filter((cat) => cat.questions.length > 0)
  }, [search])

  const toggleCategory = (id) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const totalQuestions = questionCategories.reduce((sum, c) => sum + c.questions.length, 0)

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">APRM Questions</h2>
          <p className="text-sm text-slate-500 mt-1">
            {totalQuestions} pre-built legal questions across {questionCategories.length} categories
          </p>
        </div>
        <div className="relative">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search questions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:ring-2 ring-legal-600/20 focus:border-legal-400 outline-none w-full sm:w-72 shadow-sm"
          />
        </div>
      </div>

      {/* APRM Explanation Banner */}
      <div className="bg-gradient-to-r from-legal-700 via-legal-600 to-emerald-600 rounded-2xl p-5 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/4" />
        <div className="relative z-10 flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center text-sm font-bold">A</span>
            <span className="text-xs font-medium">Analyze</span>
          </div>
          <svg className="w-4 h-4 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center text-sm font-bold">P</span>
            <span className="text-xs font-medium">Process</span>
          </div>
          <svg className="w-4 h-4 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center text-sm font-bold">R</span>
            <span className="text-xs font-medium">Retrieve</span>
          </div>
          <svg className="w-4 h-4 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center text-sm font-bold">M</span>
            <span className="text-xs font-medium">Model</span>
          </div>
          <p className="w-full mt-2 text-xs text-white/70">
            Click any question below — it will be processed through the full APRM pipeline to generate a legal response.
          </p>
        </div>
      </div>

      {/* Category Grid */}
      {filteredCategories.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-slate-400 text-sm">No questions matching "{search}"</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredCategories.map((cat) => {
            const isExpanded = expandedCategories.has(cat.id)
            return (
              <div
                key={cat.id}
                className={`bg-white rounded-2xl border ${cat.border} shadow-sm hover:shadow-md transition-all overflow-hidden`}
              >
                {/* Category Header */}
                <button
                  onClick={() => toggleCategory(cat.id)}
                  className="w-full flex items-center gap-3 p-4 text-left"
                >
                  <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${cat.gradient} flex items-center justify-center text-lg shadow-sm`}>
                    {cat.emoji}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-sm text-slate-800">{cat.title}</h3>
                    <p className="text-[11px] text-slate-400">{cat.questions.length} questions</p>
                  </div>
                  <svg
                    className={`w-4 h-4 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Questions List */}
                {isExpanded && (
                  <div className={`px-4 pb-4 space-y-1.5`}>
                    {cat.questions.map((q) => (
                      <button
                        key={q}
                        onClick={() => askQuestion(q)}
                        className={`w-full text-left px-3 py-2.5 rounded-xl ${cat.bg} hover:ring-2 ring-legal-600/20 text-xs font-medium text-slate-700 hover:text-legal-700 transition-all flex items-center gap-2 group`}
                      >
                        <svg className="w-3.5 h-3.5 text-slate-400 group-hover:text-legal-600 flex-shrink-0 transition" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <span className="flex-1">{q}</span>
                        <svg className="w-3 h-3 text-slate-300 group-hover:text-legal-600 opacity-0 group-hover:opacity-100 transition" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    ))}
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
