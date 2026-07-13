import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Trash2, MessageSquare, Mic, Sparkles, Paperclip, MessageCircleQuestion } from 'lucide-react'
import { UserBubble, BotBubble, TypingIndicator } from '../components/ChatBubble'

const SUGGESTED = [
  'What is your return policy?',
  'What are the shipping charges?',
  'How do I track my order?',
  'Do you offer EMI options?',
  'How to contact customer support?',
  'Can I exchange a product?',
]

const PAGE_VARIANTS = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -30 },
}

export default function UserPortal() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const [feedbacks, setFeedbacks] = useState({})
  const [clearing, setClearing] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  // Load existing messages on mount
  useEffect(() => {
    fetch('/api/messages').then(r => r.json()).then(d => {
      if (d.ok && d.messages.length) setMessages(d.messages)
    }).catch(() => {})
  }, [])

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typing])

  const sendMessage = async (text) => {
    const msg = (text || input).trim()
    if (!msg || typing) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg, ts: new Date().toISOString() }])
    setTyping(true)

    try {
      const r = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg }),
      })
      const d = await r.json()
      if (d.ok) {
        setMessages(prev => [...prev, d.message])
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant', content: `Error: ${d.error || 'Something went wrong.'}`,
          ts: new Date().toISOString(),
        }])
      }
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant', content: `Cannot reach the API server. Is it running on port 5000?`,
        ts: new Date().toISOString(),
      }])
    } finally {
      setTyping(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  const handleFeedback = async (msgIdx, vote) => {
    if (feedbacks[msgIdx]) return // already voted
    setFeedbacks(f => ({ ...f, [msgIdx]: vote }))
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vote }),
      })
    } catch (_) {}
  }

  const handleClear = async () => {
    setClearing(true)
    try {
      await fetch('/api/clear', { method: 'POST' })
      setMessages([])
      setFeedbacks({})
    } catch (_) {}
    setClearing(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <motion.div
      variants={PAGE_VARIANTS}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.4, ease: 'easeOut' }}
      style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - var(--navbar-h) - 64px)', maxWidth: 1000, margin: '0 auto', position: 'relative' }}
    >
      {/* Dynamic Background Glow */}
      <div style={{
        position: 'absolute', top: '20%', left: '30%', width: '40%', height: '40%',
        background: 'radial-gradient(circle, rgba(0,255,247,0.03) 0%, transparent 70%)',
        zIndex: -1, pointerEvents: 'none'
      }} />

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          background: 'rgba(10, 15, 30, 0.4)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(0,255,247,0.15)',
          borderRadius: 'var(--radius-lg)',
          padding: '24px 32px',
          marginBottom: 24,
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
        }}
      >
        <motion.div
          animate={{ left: ['-100%', '100%'] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
          style={{
            position: 'absolute', top: 0, height: '2px', width: '40%',
            background: 'linear-gradient(90deg, transparent, var(--cyan), var(--purple), transparent)',
          }}
        />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, marginBottom: 8 }}>
          <motion.div animate={{ rotate: [0, 5, -5, 0] }} transition={{ duration: 3, repeat: Infinity }}>
            <MessageSquare size={24} color="var(--cyan)" />
          </motion.div>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.6rem', fontWeight: 800,
            background: 'linear-gradient(90deg, var(--cyan), var(--purple))',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            letterSpacing: 1
          }}>
            AI Support Workspace
          </h2>
        </div>
        <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', letterSpacing: 2, textTransform: 'uppercase' }}>
          Context-Aware • 50+ Languages • Zero Hallucination
        </div>

        {/* Clear button */}
        <motion.button
          whileHover={{ scale: 1.05, background: 'rgba(255,68,102,0.15)' }}
          whileTap={{ scale: 0.95 }}
          onClick={handleClear}
          disabled={clearing || !messages.length}
          style={{
            position: 'absolute', top: '50%', right: 20, transform: 'translateY(-50%)',
            background: 'rgba(255,68,102,0.05)',
            border: '1px solid rgba(255,68,102,0.2)',
            borderRadius: 8, padding: '8px 16px',
            color: 'var(--red)', cursor: 'pointer', fontSize: '0.8rem',
            display: 'flex', alignItems: 'center', gap: 6,
            opacity: messages.length ? 1 : 0.4,
            transition: 'all 0.2s'
          }}
        >
          <Trash2 size={14} /> {clearing ? 'Saving...' : 'Clear Session'}
        </motion.button>
      </motion.div>

      {/* Chat messages */}
      <div style={{
        flex: 1, overflowY: 'auto', padding: '10px 20px',
        display: 'flex', flexDirection: 'column',
      }}>
        {/* Suggested questions Empty State */}
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9, filter: 'blur(10px)' }}
              style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 30, fontSize: '0.8rem' }}>
                <Sparkles size={14} /> Suggested Questions
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, justifyContent: 'center', maxWidth: 600 }}>
                {SUGGESTED.map((s, i) => (
                  <motion.button
                    key={s}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1, type: 'spring' }}
                    whileHover={{ scale: 1.05, y: -4, boxShadow: '0 10px 20px rgba(0,255,247,0.1)' }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => sendMessage(s)}
                    style={{
                      background: 'rgba(0,255,247,0.03)',
                      border: '1px solid rgba(0,255,247,0.15)',
                      borderRadius: 16,
                      padding: '12px 20px',
                      color: 'var(--cyan)',
                      fontSize: '0.9rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      transition: 'border-color 0.2s'
                    }}
                    onHoverStart={(e) => e.currentTarget.style.borderColor = 'rgba(0,255,247,0.4)'}
                    onHoverEnd={(e) => e.currentTarget.style.borderColor = 'rgba(0,255,247,0.15)'}
                  >
                    <MessageCircleQuestion size={16} /> {s}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence initial={false}>
          {messages.map((msg, idx) =>
            msg.role === 'user' ? (
              <UserBubble key={idx} content={msg.content} ts={msg.ts} />
            ) : (
              <BotBubble
                key={idx}
                content={msg.content}
                sources={msg.sources}
                languageName={msg.language_name}
                ts={msg.ts}
                feedbackState={feedbacks[idx]}
                onFeedback={(vote) => handleFeedback(idx, vote)}
              />
            )
          )}
        </AnimatePresence>

        <AnimatePresence>
          {typing && <TypingIndicator key="typing" />}
        </AnimatePresence>

        <div ref={bottomRef} style={{ height: 20 }} />
      </div>

      {/* Input area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        style={{
          marginTop: 16,
          background: 'rgba(10, 15, 30, 0.6)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(0,255,247,0.25)',
          borderRadius: 24,
          padding: '16px 24px',
          display: 'flex',
          alignItems: 'flex-end',
          gap: 12,
          boxShadow: '0 10px 40px rgba(0,0,0,0.4)',
          position: 'relative',
          zIndex: 10
        }}
      >
        <motion.button
          whileHover={{ scale: 1.1, color: 'var(--cyan)' }}
          whileTap={{ scale: 0.9 }}
          style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', paddingBottom: 4 }}
        >
          <Paperclip size={20} />
        </motion.button>

        <textarea
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about products, policies, shipping, returns..."
          disabled={typing}
          rows={1}
          style={{
            flex: 1, background: 'transparent', border: 'none', outline: 'none',
            color: '#fff', fontFamily: 'var(--font-body)',
            fontSize: '1rem', resize: 'none', lineHeight: 1.5,
            maxHeight: 150, overflowY: 'auto',
            minHeight: 24,
            padding: '2px 0'
          }}
          onInput={(e) => {
            e.target.style.height = 'auto'
            e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px'
          }}
        />

        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexShrink: 0 }}>
          {/* Char count */}
          {input.length > 0 && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{input.length}</span>
          )}

          {/* Voice button */}
          <motion.button
            whileHover={{ scale: 1.1, background: 'rgba(191,0,255,0.15)' }}
            whileTap={{ scale: 0.9 }}
            style={{
              background: 'rgba(191,0,255,0.08)',
              border: '1px solid rgba(191,0,255,0.2)',
              borderRadius: '50%',
              width: 36, height: 36,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--purple)', cursor: 'pointer', transition: 'all 0.2s'
            }}
            data-tooltip="Voice Input"
          >
            <Mic size={18} />
          </motion.button>

          {/* Send button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => sendMessage()}
            disabled={!input.trim() || typing}
            style={{
              background: input.trim() && !typing
                ? 'linear-gradient(135deg, var(--cyan), #00aacc, var(--purple))'
                : 'rgba(255,255,255,0.05)',
              border: 'none',
              borderRadius: '50%',
              width: 38, height: 38,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: input.trim() && !typing ? 'pointer' : 'default',
              color: input.trim() && !typing ? '#000' : 'var(--text-dim)',
              transition: 'all 0.3s ease',
              boxShadow: input.trim() && !typing ? '0 0 20px rgba(0,255,247,0.4)' : 'none',
            }}
          >
            {typing ? <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> : <Send size={18} style={{ marginLeft: 2 }} />}
          </motion.button>
        </div>
      </motion.div>

      <div style={{
        textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-dim)',
        marginTop: 12, letterSpacing: 0.5
      }}>
        Press <kbd style={{ background: 'rgba(255,255,255,0.08)', padding: '2px 6px', borderRadius: 6, fontSize: '0.85em', border: '1px solid rgba(255,255,255,0.1)' }}>Enter</kbd> to send • 
        <kbd style={{ background: 'rgba(255,255,255,0.08)', padding: '2px 6px', borderRadius: 6, fontSize: '0.85em', marginLeft: 6, border: '1px solid rgba(255,255,255,0.1)' }}>Shift+Enter</kbd> for new line
      </div>
    </motion.div>
  )
}
