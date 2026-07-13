import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import StatCard from '../components/StatCard'
import { TrendingUp, Globe, ThumbsUp, Zap, MessageSquare, Tag, Activity, ThumbsDown } from 'lucide-react'

const PAGE_VARIANTS = {
  initial: { opacity: 0, x: 30 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -30 },
}

const CHART_TOOLTIP_STYLE = {
  backgroundColor: 'rgba(2,2,12,0.95)',
  border: '1px solid rgba(0,255,247,0.2)',
  borderRadius: 10,
  color: '#e2e8f0',
  fontSize: '0.82rem',
}

export default function AnalyticsDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('overview')

  const fetchData = async () => {
    setLoading(true)
    try {
      const r = await fetch('/api/analytics')
      const d = await r.json()
      if (d.ok) setData(d)
    } catch (_) {}
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [])

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh', gap: 16, flexDirection: 'column' }}>
        <div className="spinner spinner-lg" />
        <div style={{ color: 'var(--cyan)', fontFamily: 'var(--font-display)', letterSpacing: 2, fontSize: '0.85rem' }}>
          LOADING ANALYTICS...
        </div>
      </div>
    )
  }

  const { total_questions = 0, avg_response_time = 0, satisfaction_pct = 0,
    feedback_up = 0, feedback_down = 0, languages = [], topics = [],
    response_times = [], sessions = 0 } = data || {}

  const rtData = response_times.map((v, i) => ({ x: i + 1, 'Response Time (s)': v }))
  const langData = languages.map(l => ({ name: l.name, count: l.count }))
  const feedbackData = [
    { name: 'Positive', value: feedback_up, color: '#00ff88' },
    { name: 'Negative', value: feedback_down, color: '#ff4466' },
  ]

  const TABS = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'languages', label: 'Languages', icon: Globe },
    { id: 'feedback', label: 'Feedback', icon: ThumbsUp },
    { id: 'performance', label: 'Performance', icon: Zap },
  ]

  return (
    <motion.div
      variants={PAGE_VARIANTS}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.35, ease: 'easeOut' }}
    >
      {/* Page header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
        <div>
          <h2 className="section-head" style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, fontSize: '1.2rem' }}>
            <Activity size={20} color="var(--cyan)" />
            Analytics Dashboard
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.84rem' }}>
            Real-time insights from your AI conversations
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={fetchData}
          className="btn btn-ghost btn-sm"
        >
          Refresh
        </motion.button>
      </div>

      {/* KPI cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        <StatCard value={total_questions} label="Questions Asked" icon={<MessageSquare size={26} color="var(--cyan)" />} color="cyan" delay={0} />
        <StatCard value={avg_response_time} label="Avg Response Time" icon={<Zap size={26} color="var(--purple)" />} color="purple" suffix="s" delay={0.1} />
        <StatCard value={satisfaction_pct} label="Satisfaction Rate" icon={<ThumbsUp size={26} color="var(--green)" />} color="green" suffix="%" delay={0.2} />
        <StatCard value={sessions} label="Total Sessions" icon={<TrendingUp size={26} color="var(--purple)" />} color="purple" delay={0.3} />
      </div>

      {/* Tab navigation */}
      <div style={{
        display: 'flex', gap: 4,
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 'var(--radius-full)',
        padding: 4,
        marginBottom: 24,
        width: 'fit-content',
      }}>
        {TABS.map(({ id, label, icon: Icon }) => (
          <motion.button
            key={id}
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => setTab(id)}
            style={{
              display: 'flex', alignItems: 'center', gap: 7,
              padding: '9px 20px', borderRadius: 'var(--radius-full)',
              border: 'none', cursor: 'pointer', fontSize: '0.83rem',
              fontWeight: tab === id ? 700 : 500,
              background: tab === id
                ? 'linear-gradient(135deg, var(--cyan), #00aacc, var(--purple))'
                : 'transparent',
              color: tab === id ? '#000' : 'var(--text-secondary)',
              transition: 'all 0.25s ease',
              fontFamily: 'var(--font-body)',
            }}
          >
            <Icon size={14} />
            {label}
          </motion.button>
        ))}
      </div>

      {/* Tab content */}
      <motion.div
        key={tab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
      >
        {/* Overview tab */}
        {tab === 'overview' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            {/* Response time chart */}
            <div className="card" style={{ padding: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--cyan)', fontSize: '0.75rem', letterSpacing: 2, marginBottom: 16, fontWeight: 600 }}>
                <Zap size={14} /> RESPONSE TIME TREND
              </div>
              {rtData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={rtData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis dataKey="x" stroke="var(--text-dim)" tick={{ fontSize: 11 }} />
                    <YAxis stroke="var(--text-dim)" tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                    <Line type="monotone" dataKey="Response Time (s)" stroke="var(--cyan)"
                      strokeWidth={2} dot={{ fill: 'var(--cyan)', r: 3 }}
                      activeDot={{ r: 6, fill: 'var(--cyan)', boxShadow: '0 0 10px var(--cyan)' }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState text="Send messages to see response trends" />
              )}
            </div>

            {/* Language bar chart */}
            <div className="card" style={{ padding: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--cyan)', fontSize: '0.75rem', letterSpacing: 2, marginBottom: 16, fontWeight: 600 }}>
                <Globe size={14} /> LANGUAGES DISTRIBUTION
              </div>
              {langData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={langData} barSize={30}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis dataKey="name" stroke="var(--text-dim)" tick={{ fontSize: 11 }} />
                    <YAxis stroke="var(--text-dim)" tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                    <Bar dataKey="count" fill="url(#barGrad)" radius={[6, 6, 0, 0]} />
                    <defs>
                      <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--cyan)" stopOpacity={0.9} />
                        <stop offset="100%" stopColor="var(--purple)" stopOpacity={0.7} />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState text="Chat to see language breakdown" />
              )}
            </div>
          </div>
        )}

        {/* Languages tab */}
        {tab === 'languages' && (
          <div className="card" style={{ padding: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--cyan)', fontSize: '0.75rem', letterSpacing: 2, marginBottom: 20, fontWeight: 600 }}>
              <Globe size={14} /> LANGUAGES USED
            </div>
            {languages.length > 0 ? (
              languages.map((l, i) => {
                const pct = Math.round((l.count / Math.max(total_questions, 1)) * 100)
                return (
                  <motion.div
                    key={l.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.06 }}
                    className="progress-wrap"
                  >
                    <div className="progress-label">
                      <span>{l.name}</span>
                      <span style={{ color: 'var(--cyan)' }}>{l.count} ({pct}%)</span>
                    </div>
                    <div className="progress-track">
                      <motion.div
                        className="progress-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: 1, delay: i * 0.08 }}
                      />
                    </div>
                  </motion.div>
                )
              })
            ) : <EmptyState text="Start chatting to see language data" />}
          </div>
        )}

        {/* Feedback tab */}
        {tab === 'feedback' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            <div className="card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--cyan)', fontSize: '0.75rem', letterSpacing: 2, marginBottom: 16, fontWeight: 600 }}>
                <ThumbsUp size={14} /> FEEDBACK BREAKDOWN
              </div>
              {feedback_up + feedback_down > 0 ? (
                <>
                  {[
                    { label: 'Positive', count: feedback_up, pct: Math.round(feedback_up / Math.max(feedback_up + feedback_down, 1) * 100), cls: 'green', icon: ThumbsUp },
                    { label: 'Negative', count: feedback_down, pct: Math.round(feedback_down / Math.max(feedback_up + feedback_down, 1) * 100), cls: 'red', icon: ThumbsDown },
                  ].map((item, i) => (
                    <motion.div key={item.label} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.1 }} className="progress-wrap">
                      <div className="progress-label">
                        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}><item.icon size={12}/> {item.label}</span>
                        <span style={{ color: item.cls === 'green' ? 'var(--green)' : 'var(--red)' }}>
                          {item.count} ({item.pct}%)
                        </span>
                      </div>
                      <div className="progress-track">
                        <motion.div className={`progress-fill ${item.cls}`}
                          initial={{ width: 0 }} animate={{ width: `${item.pct}%` }} transition={{ duration: 1, delay: 0.2 }} />
                      </div>
                    </motion.div>
                  ))}
                </>
              ) : <EmptyState text="Rate answers to see feedback" />}
            </div>

            <div className="card" style={{ padding: 24, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              {feedback_up + feedback_down > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie data={feedbackData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={4} dataKey="value">
                        {feedbackData.map((e, i) => (
                          <Cell key={i} fill={e.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                      <Legend wrapperStyle={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div style={{ textAlign: 'center', marginTop: 12 }}>
                    <div style={{
                      fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 900,
                      color: 'var(--green)', textShadow: '0 0 20px rgba(0,255,136,0.5)',
                    }}>
                      {satisfaction_pct}%
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', letterSpacing: 2 }}>SATISFACTION RATE</div>
                  </div>
                </>
              ) : <EmptyState text="No feedback yet" />}
            </div>
          </div>
        )}

        {/* Performance tab */}
        {tab === 'performance' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Response time detail */}
            <div className="card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--cyan)', fontSize: '0.75rem', letterSpacing: 2, marginBottom: 16, fontWeight: 600 }}>
                <Zap size={14} /> RESPONSE TIMES (last 20 queries)
              </div>
              {rtData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={rtData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis dataKey="x" stroke="var(--text-dim)" tick={{ fontSize: 11 }} label={{ value: 'Query #', position: 'insideBottom', fill: 'var(--text-dim)', fontSize: 11 }} />
                    <YAxis stroke="var(--text-dim)" tick={{ fontSize: 11 }} unit="s" />
                    <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                    <Line type="monotone" dataKey="Response Time (s)" stroke="var(--cyan)"
                      strokeWidth={2.5} dot={{ fill: 'var(--cyan)', r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : <EmptyState text="Start chatting to see performance data" />}
            </div>

            {/* Trending topics */}
            <div className="card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--purple)', fontSize: '0.75rem', letterSpacing: 2, marginBottom: 16, fontWeight: 600 }}>
                <Tag size={14} /> TRENDING TOPICS
              </div>
              {topics.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                  {topics.map((t, i) => (
                    <motion.div
                      key={t.name}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.06, type: 'spring', stiffness: 200 }}
                      whileHover={{ scale: 1.08, y: -3 }}
                      style={{
                        background: 'rgba(191,0,255,0.08)',
                        border: '1px solid rgba(191,0,255,0.2)',
                        borderRadius: 'var(--radius-md)',
                        padding: '12px 18px',
                        textAlign: 'center',
                        minWidth: 90,
                      }}
                    >
                      <div style={{
                        fontFamily: 'var(--font-display)', fontSize: '1.4rem', fontWeight: 900,
                        color: 'var(--purple)', textShadow: '0 0 12px rgba(191,0,255,0.5)',
                      }}>
                        {t.count}
                      </div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginTop: 4 }}>{t.name}</div>
                    </motion.div>
                  ))}
                </div>
              ) : <EmptyState text="Topics appear as you chat" />}
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  )
}

function EmptyState({ text }) {
  return (
    <div style={{ padding: '32px 0', textAlign: 'center' }}>
      <div style={{ marginBottom: 10, opacity: 0.4, display: 'flex', justifyContent: 'center' }}>
        <Activity size={40} color="var(--text-muted)" />
      </div>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>{text}</div>
    </div>
  )
}
