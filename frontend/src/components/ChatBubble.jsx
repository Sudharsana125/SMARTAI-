import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { ChevronDown, ExternalLink, User, Bot, ThumbsUp, ThumbsDown, Globe, Copy, Check, Volume2, RefreshCcw } from 'lucide-react'

export function UserBubble({ content, ts }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 40, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={{ duration: 0.4, type: 'spring', bounce: 0.3 }}
      style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 20 }}
    >
      <div style={{ maxWidth: '75%', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
        <div style={{
          background: 'linear-gradient(135deg, rgba(191,0,255,0.2), rgba(100,0,180,0.1))',
          border: '1px solid rgba(191,0,255,0.3)',
          borderRadius: '24px 24px 4px 24px',
          padding: '14px 20px',
          color: '#f0e6ff',
          fontSize: '0.96rem',
          lineHeight: 1.6,
          boxShadow: '0 8px 32px rgba(191,0,255,0.15)',
          backdropFilter: 'blur(8px)',
        }}>
          {content}
        </div>
        {ts && (
          <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', marginTop: 6, paddingRight: 8, letterSpacing: 1 }}>
            {new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>
      <div style={{
        width: 36, height: 36, borderRadius: '50%', flexShrink: 0, marginLeft: 12,
        background: 'linear-gradient(135deg, rgba(191,0,255,0.4), rgba(100,0,180,0.2))',
        border: '1px solid rgba(191,0,255,0.4)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 0 15px rgba(191,0,255,0.2)',
      }}>
        <User size={18} color="#fff" />
      </div>
    </motion.div>
  )
}

export function BotBubble({ content, sources, languageName, ts, onFeedback, feedbackState }) {
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -40, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={{ duration: 0.4, type: 'spring', bounce: 0.3 }}
      style={{ display: 'flex', alignItems: 'flex-start', marginBottom: 24 }}
    >
      <motion.div
        animate={{ y: [0, -4, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          width: 36, height: 36, borderRadius: '50%', flexShrink: 0, marginRight: 12,
          background: 'linear-gradient(135deg, rgba(0,255,247,0.3), rgba(0,100,200,0.2))',
          border: '1px solid rgba(0,255,247,0.4)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 15px rgba(0,255,247,0.2)',
        }}
      >
        <Bot size={20} color="#fff" />
      </motion.div>

      <div style={{ maxWidth: '82%', width: '100%' }}>
        <div style={{
          background: 'rgba(10, 15, 30, 0.6)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(0,255,247,0.15)',
          borderRadius: '24px 24px 24px 4px',
          padding: '16px 22px',
          color: '#e0f7fa',
          fontSize: '0.96rem',
          lineHeight: 1.7,
          boxShadow: '0 8px 32px rgba(0,255,247,0.08)',
          position: 'relative',
          overflow: 'hidden',
        }}>
          {/* Animated top glow line */}
          <motion.div
            animate={{ left: ['-100%', '100%'] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            style={{
              position: 'absolute', top: 0, height: '1px', width: '40%',
              background: 'linear-gradient(90deg, transparent, rgba(0,255,247,0.6), transparent)',
            }}
          />
          <div style={{ whiteSpace: 'pre-wrap', position: 'relative', zIndex: 1 }}>{content}</div>
        </div>

        {/* Action & Meta Row */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          marginTop: 8, flexWrap: 'wrap', gap: 10, paddingLeft: 8
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {ts && (
              <span style={{ fontSize: '0.65rem', color: 'var(--text-dim)', letterSpacing: 1 }}>
                {new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}
            {languageName && (
              <span style={{
                display: 'flex', alignItems: 'center', gap: 4,
                fontSize: '0.7rem', color: 'var(--cyan)',
                background: 'rgba(0,255,247,0.05)',
                border: '1px solid rgba(0,255,247,0.15)',
                borderRadius: 20, padding: '2px 10px',
              }}>
                <Globe size={10} /> {languageName}
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {/* Utility Actions */}
            <div style={{ display: 'flex', gap: 4, marginRight: 8, borderRight: '1px solid rgba(255,255,255,0.1)', paddingRight: 8 }}>
              <motion.button whileHover={{ scale: 1.1, color: 'var(--cyan)' }} whileTap={{ scale: 0.9 }} onClick={handleCopy}
                style={{ background: 'none', border: 'none', color: copied ? 'var(--cyan)' : 'var(--text-muted)', cursor: 'pointer', padding: 4 }}>
                {copied ? <Check size={14} /> : <Copy size={14} />}
              </motion.button>
              <motion.button whileHover={{ scale: 1.1, color: 'var(--purple)' }} whileTap={{ scale: 0.9 }}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 4 }}>
                <Volume2 size={14} />
              </motion.button>
            </div>

            {/* Feedback */}
            {onFeedback && (
              <div style={{ display: 'flex', gap: 6 }}>
                <motion.button
                  whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={() => onFeedback('up')}
                  style={{
                    background: feedbackState === 'up' ? 'rgba(0,255,136,0.15)' : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${feedbackState === 'up' ? 'rgba(0,255,136,0.4)' : 'rgba(255,255,255,0.08)'}`,
                    borderRadius: 8, padding: '4px 10px', cursor: 'pointer',
                    color: feedbackState === 'up' ? '#00ff88' : 'var(--text-muted)',
                    transition: 'all 0.2s', display: 'flex', alignItems: 'center',
                  }}
                >
                  <ThumbsUp size={14} />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={() => onFeedback('down')}
                  style={{
                    background: feedbackState === 'down' ? 'rgba(255,68,102,0.15)' : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${feedbackState === 'down' ? 'rgba(255,68,102,0.4)' : 'rgba(255,255,255,0.08)'}`,
                    borderRadius: 8, padding: '4px 10px', cursor: 'pointer',
                    color: feedbackState === 'down' ? '#ff4466' : 'var(--text-muted)',
                    transition: 'all 0.2s', display: 'flex', alignItems: 'center',
                  }}
                >
                  <ThumbsDown size={14} />
                </motion.button>
              </div>
            )}
          </div>
        </div>

        {/* Sources Accordion */}
        {sources?.length > 0 && (
          <motion.div style={{ marginTop: 12 }}>
            <motion.button
              whileHover={{ background: 'rgba(0,255,247,0.08)' }}
              onClick={() => setSourcesOpen(o => !o)}
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                background: sourcesOpen ? 'rgba(0,255,247,0.08)' : 'rgba(0,255,247,0.03)',
                border: '1px solid rgba(0,255,247,0.2)',
                borderRadius: 12, padding: '6px 14px',
                color: 'var(--cyan)', fontSize: '0.8rem', cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              <ExternalLink size={14} />
              View {sources.length} Cited Source{sources.length > 1 ? 's' : ''}
              <motion.span animate={{ rotate: sourcesOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
                <ChevronDown size={14} />
              </motion.span>
            </motion.button>

            <AnimatePresence>
              {sourcesOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  style={{ overflow: 'hidden' }}
                >
                  <div style={{ paddingTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {sources.map((ch, i) => {
                      const sc = ch.score > 0.6 ? 'var(--cyan)' : ch.score > 0.4 ? 'var(--purple)' : 'var(--text-muted)'
                      return (
                        <motion.div 
                          key={i} 
                          initial={{ x: -10, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: i * 0.05 }}
                          whileHover={{ scale: 1.01, borderLeftWidth: 4 }}
                          style={{
                          padding: '12px 16px',
                          background: 'rgba(0,0,0,0.3)',
                          border: '1px solid rgba(255,255,255,0.05)',
                          borderLeft: `2px solid ${sc}`,
                          borderRadius: 8,
                          transition: 'all 0.2s'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                            <div style={{ color: sc, fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                              <ExternalLink size={12} />
                              {ch.source}{ch.page ? ` (Page ${ch.page})` : ''}
                            </div>
                            <span style={{ background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: 12, fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                              {Math.round(ch.score * 100)}% Match
                            </span>
                          </div>
                          <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', lineHeight: 1.6 }}>
                            "{ch.text?.slice(0, 250)}..."
                          </div>
                        </motion.div>
                      )
                    })}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10, scale: 0.9 }}
      style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}
    >
      <div style={{
        width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
        background: 'linear-gradient(135deg, rgba(0,255,247,0.3), rgba(0,100,200,0.2))',
        border: '1px solid rgba(0,255,247,0.4)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 0 15px rgba(0,255,247,0.2)',
      }}>
        <Bot size={20} color="#fff" />
      </div>
      <div style={{
        background: 'rgba(0,255,247,0.03)',
        border: '1px solid rgba(0,255,247,0.15)',
        borderRadius: '20px 20px 20px 4px',
        padding: '16px 24px',
        display: 'flex', gap: 6,
      }}>
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            animate={{ y: [0, -8, 0], opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
            style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--cyan)' }}
          />
        ))}
      </div>
    </motion.div>
  )
}
