import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts'

const PIE_COLORS = ['#1f6f58', '#f59e0b']

const BAR_COLORS = [
  '#1f6f58', '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#6366f1',
]

function StatCard({ label, value, icon, color, subtitle }) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
      <div className="flex items-center gap-3">
        <div className={`w-11 h-11 rounded-xl ${color} flex items-center justify-center`}>
          {icon}
        </div>
        <div>
          <p className="text-2xl font-bold text-slate-800">{value ?? '—'}</p>
          <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">{label}</p>
        </div>
      </div>
      {subtitle && <p className="mt-2 text-[11px] text-slate-400">{subtitle}</p>}
    </div>
  )
}

function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-slate-200 rounded-lg px-3 py-2 shadow-lg">
        <p className="text-xs font-semibold text-slate-700">{label}</p>
        <p className="text-xs text-legal-600">{payload[0].value} queries</p>
      </div>
    )
  }
  return null
}

export default function Analytics({ stats }) {
  const loading = !stats

  const pieData = loading
    ? []
    : [
        { name: 'Completed', value: stats.completed_queries || 0 },
        { name: 'Pending', value: stats.pending_queries || 0 },
      ]

  const dailyData = loading
    ? []
    : (stats.daily_queries || []).map((d) => ({
        date: new Date(d.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
        count: d.count,
      }))

  const intentData = loading ? [] : (stats.intent_distribution || [])

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-800">APRM Analytics</h2>
        <p className="text-sm text-slate-500 mt-1">
          System performance and usage insights
        </p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Sessions"
          value={stats?.total_sessions}
          color="bg-teal-50 text-teal-700"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          }
        />
        <StatCard
          label="Total Queries"
          value={stats?.total_queries}
          color="bg-blue-50 text-blue-700"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          }
        />
        <StatCard
          label="Completion Rate"
          value={stats ? `${stats.completion_rate}%` : undefined}
          color="bg-emerald-50 text-emerald-700"
          subtitle={stats ? `${stats.completed_queries} of ${stats.total_queries} completed` : undefined}
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <StatCard
          label="Pending"
          value={stats?.pending_queries}
          color="bg-amber-50 text-amber-700"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Queries Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <h3 className="font-bold text-sm text-slate-800 mb-4">Queries Over Time (7 Days)</h3>
          {loading ? (
            <div className="h-64 bg-slate-50 rounded-xl animate-pulse" />
          ) : dailyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={dailyData}>
                <defs>
                  <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1f6f58" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#1f6f58" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#1f6f58"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#colorQueries)"
                  dot={{ r: 4, fill: '#1f6f58', stroke: '#fff', strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: '#1f6f58', stroke: '#fff', strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-sm text-slate-400">
              No data in the last 7 days
            </div>
          )}
        </div>

        {/* Pie Chart - Completion Status */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <h3 className="font-bold text-sm text-slate-800 mb-4">Query Status</h3>
          {loading ? (
            <div className="h-64 bg-slate-50 rounded-xl animate-pulse" />
          ) : stats.total_queries > 0 ? (
            <div>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                    stroke="none"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value, name) => [`${value} queries`, name]}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px', border: '1px solid #e2e8f0' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-6 mt-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-legal-600" />
                  <span className="text-xs text-slate-600">Completed ({stats.completed_queries})</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-amber-500" />
                  <span className="text-xs text-slate-600">Pending ({stats.pending_queries})</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-sm text-slate-400">
              No queries yet
            </div>
          )}
        </div>
      </div>

      {/* Intent Distribution */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 className="font-bold text-sm text-slate-800 mb-1">Intent Distribution</h3>
        <p className="text-[11px] text-slate-400 mb-4">Top detected legal categories from APRM analysis</p>
        {loading ? (
          <div className="h-72 bg-slate-50 rounded-xl animate-pulse" />
        ) : intentData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={intentData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} allowDecimals={false} />
              <YAxis
                type="category"
                dataKey="intent"
                tick={{ fontSize: 11, fill: '#64748b' }}
                axisLine={false}
                tickLine={false}
                width={120}
              />
              <Tooltip
                formatter={(value) => [`${value} queries`, 'Count']}
                contentStyle={{ borderRadius: '8px', fontSize: '12px', border: '1px solid #e2e8f0' }}
              />
              <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={20}>
                {intentData.map((entry, index) => (
                  <Cell key={`bar-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-72 flex items-center justify-center text-sm text-slate-400">
            No intent data available yet. Ask some questions to see analytics!
          </div>
        )}
      </div>

      {/* APRM Pipeline Performance */}
      <div className="bg-gradient-to-br from-legal-700 via-legal-600 to-emerald-600 rounded-2xl p-6 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/3" />
        <h3 className="font-bold text-lg mb-4 relative z-10">APRM Pipeline Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
          {[
            { letter: 'A', title: 'Analyze', desc: 'Query normalization, typo fix, phrase alias expansion' },
            { letter: 'P', title: 'Process', desc: 'Intent detection across 30+ categories, entity extraction' },
            { letter: 'R', title: 'Retrieve', desc: 'ChromaDB vector search + keyword scoring' },
            { letter: 'M', title: 'Model', desc: 'Ollama LLM generates structured legal response' },
          ].map((step) => (
            <div key={step.letter} className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
              <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center text-lg font-bold mx-auto">
                {step.letter}
              </div>
              <p className="mt-2 font-bold text-sm">{step.title}</p>
              <p className="mt-1 text-[11px] text-white/70 leading-tight">{step.desc}</p>
            </div>
          ))}
        </div>
        {!loading && (
          <div className="mt-4 flex flex-wrap gap-4 relative z-10">
            <div className="bg-white/10 backdrop-blur rounded-lg px-4 py-2">
              <p className="text-[10px] text-white/60 uppercase font-bold tracking-wider">Avg Queries/Session</p>
              <p className="text-lg font-bold">
                {stats.total_sessions > 0
                  ? (stats.total_queries / stats.total_sessions).toFixed(1)
                  : '0'}
              </p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg px-4 py-2">
              <p className="text-[10px] text-white/60 uppercase font-bold tracking-wider">Success Rate</p>
              <p className="text-lg font-bold">{stats.completion_rate}%</p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg px-4 py-2">
              <p className="text-[10px] text-white/60 uppercase font-bold tracking-wider">Active Intents</p>
              <p className="text-lg font-bold">{intentData.length}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
