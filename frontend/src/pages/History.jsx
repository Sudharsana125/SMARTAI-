import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Clock, RotateCcw, ChevronDown, ChevronUp, MessageSquare, Save } from 'lucide-react'

const PAGE_VARIANTS = {
  initial: { opacity: 0, x: 30 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -30 },
}

export default function History() {
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)
  const [restoring, setRestoring] = useState(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const fetchHistory = async () => {
    setLoading(true)
    try {
      const r = await fetch('/api/history')
      const d = await r.json()
      if (d.ok) setConversations(d.conversations)
    } catch (_) {}
    setLoading(false)
  }

  useEffect(() => { fetchHistory() }, [])

  const handleSaveCurrent = async () => {
    setSaving(true)
    try {
      await fetch('/api/clear', { method: 'POST' })
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
      fetchHistory()
    } catch (_) {}
    setSaving(false)
  }

  const handleRestore = async (idx) => {
    setRestoring(idx)
    try {
      await fetch('/api/history/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index: idx }),
      })
      window.location.href = '/chat'
    } catch (_) {}
    setRestoring(null)
  }

  return (
    <motion.div
      variants={PAGE_VARIANTS}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.35, ease: 'easeOut' }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
        <div>
          <h2 className="section-head" style={{ marginBottom: 4, fontSize: '1.1rem' }}>
            🕐 Conversation History
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.84rem' }}>
            {conversations.length} saved session{conversations.length !== 1 ? 's' : ''}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSaveCurrent}
            disabled={saving}
            className="btn btn-ghost btn-sm"
          >
            {saving ? <div className="spinner" /> : saved ? '✅' : <Save size={14} />}
            {saved ? 'Saved!' : 'Save Current Session'}
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={fetchHistory}
            className="btn btn-ghost btn-sm"
          >
            ↻ Refresh
          </motion.button>
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
          <div className="spinner spinner-lg" />
        </div>
      ) : conversations.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          style={{ textAlign: 'center', padding: '80px 20px' }}
        >
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
            style={{ fontSize: '4rem', marginBottom: 20 }}
          >
            🕐
          </motion.div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', fontWeight: 600, marginBottom: 10 }}>
            No conversations saved yet
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            Chat and click "Save Current Session" or "Clear" to save sessions here
          </div>
        </motion.div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {conversations.map((conv, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.06 }}
              className="card"
              style={{
                overflow: 'hidden',
                border: expanded === idx ? '1px solid rgba(0,255,247,0.2)' : undefined,
              }}
            >
              {/* Conversation header row */}
              <motion.div
                onClick={() => setExpanded(expanded === idx ? null : idx)}
                whileHover={{ background: 'rgba(0,255,247,0.03)' }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 14,
                  padding: '16px 20px', cursor: 'pointer',
                }}
              >
                {/* Icon */}
                <div style={{
                  width: 40, height: 40, borderRadius: '50%', flexShrink: 0,
                  background: 'linear-gradient(135deg, rgba(0,255,247,0.12), rgba(191,0,255,0.12))',
                  border: '1px solid rgba(0,255,247,0.15)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <MessageSquare size={18} color="var(--cyan)" />
                </div>

                {/* Title */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)',
                    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                  }}>
                    {conv.title}
                  </div>
                  <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                    <span style={{ fontSize: '0.73rem', color: 'var(--text-dim)' }}>
                      📅 {conv.time}
                    </span>
                    <span className="badge badge-cyan" style={{ padding: '1px 8px', fontSize: '0.7rem' }}>
                      {conv.count} Q&A
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <motion.button
                    whileHover={{ scale: 1.08 }}
                    whileTap={{ scale: 0.92 }}
                    onClick={(e) => { e.stopPropagation(); handleRestore(idx) }}
                    disabled={restoring === idx}
                    className="btn btn-ghost btn-sm"
                  >
                    {restoring === idx ? <div className="spinner" /> : <RotateCcw size={13} />}
                    Restore
                  </motion.button>
                  <motion.div animate={{ rotate: expanded === idx ? 180 : 0 }} transition={{ duration: 0.25 }}>
                    <ChevronDown size={18} color="var(--text-muted)" />
                  </motion.div>
                </div>
              </motion.div>

              {/* Expanded messages */}
              <AnimatePresence>
                {expanded === idx && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    style={{ overflow: 'hidden' }}
                  >
                    <div style={{
                      padding: '0 20px 20px 20px',
                      borderTop: '1px solid rgba(0,255,247,0.06)',
                      maxHeight: 380, overflowY: 'auto',
                    }}>
                      <div style={{ height: 12 }} />
                      {conv.messages.map((msg, mi) => (
                        <div
                          key={mi}
                          style={{
                            marginBottom: 8,
                            background: msg.role === 'user'
                              ? 'rgba(191,0,255,0.06)'
                              : 'rgba(0,255,247,0.04)',
                            border: `1px solid ${msg.role === 'user' ? 'rgba(191,0,255,0.14)' : 'rgba(0,255,247,0.1)'}`,
                            borderRadius: msg.role === 'user' ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                            padding: '9px 14px',
                            fontSize: '0.84rem',
                            color: msg.role === 'user' ? '#e2d0ff' : '#cce8f0',
                            lineHeight: 1.55,
                          }}
                        >
                          <span style={{ opacity: 0.6, marginRight: 6 }}>
                            {msg.role === 'user' ? '👤' : '🤖'}
                          </span>
                          {msg.role === 'user'
                            ? msg.content
                            : msg.content.slice(0, 300) + (msg.content.length > 300 ? '...' : '')}
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  )
}
