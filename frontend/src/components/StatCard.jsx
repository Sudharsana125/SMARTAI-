import { motion } from 'framer-motion'
import { useEffect, useRef, useState } from 'react'

function useCountUp(target, duration = 1200) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    const start = performance.now()
    const num = parseFloat(target) || 0
    const frame = (now) => {
      const p = Math.min((now - start) / duration, 1)
      const ease = 1 - Math.pow(1 - p, 3)
      setVal(Math.round(ease * num * 10) / 10)
      if (p < 1) requestAnimationFrame(frame)
    }
    requestAnimationFrame(frame)
  }, [target, duration])
  return val
}

export default function StatCard({ value, label, icon, color = 'cyan', suffix = '', delay = 0 }) {
  const numericPart = parseFloat(String(value).replace(/[^0-9.]/g, '')) || 0
  const counted = useCountUp(numericPart)
  const colorMap = {
    cyan: { main: 'var(--cyan)', dim: 'rgba(0,255,247,0.06)', border: 'rgba(0,255,247,0.14)', glow: 'rgba(0,255,247,0.12)' },
    purple: { main: 'var(--purple)', dim: 'rgba(191,0,255,0.06)', border: 'rgba(191,0,255,0.14)', glow: 'rgba(191,0,255,0.12)' },
    green: { main: 'var(--green)', dim: 'rgba(0,255,136,0.06)', border: 'rgba(0,255,136,0.14)', glow: 'rgba(0,255,136,0.12)' },
    red: { main: 'var(--red)', dim: 'rgba(255,68,102,0.06)', border: 'rgba(255,68,102,0.14)', glow: 'rgba(255,68,102,0.12)' },
  }
  const c = colorMap[color] || colorMap.cyan

  // Format display value
  const displayVal = () => {
    if (suffix === '%') return `${Math.round(counted)}%`
    if (suffix === 's') return `${counted.toFixed(1)}s`
    return `${Math.round(counted)}${suffix}`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, delay, ease: [0.175, 0.885, 0.32, 1.275] }}
      whileHover={{ y: -6, boxShadow: `0 0 40px ${c.glow}, 0 12px 40px rgba(0,0,0,0.4)` }}
      style={{
        background: `linear-gradient(135deg, ${c.dim}, rgba(255,255,255,0.01))`,
        border: `1px solid ${c.border}`,
        borderRadius: 'var(--radius-md)',
        padding: '24px 20px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
        cursor: 'default',
        transition: 'box-shadow 0.3s ease, transform 0.3s ease',
      }}
    >
      {/* Bottom glow line */}
      <motion.div
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: 2,
          background: `linear-gradient(90deg, transparent, ${c.main}, transparent)`,
        }}
      />

      {/* Corner accent */}
      <div style={{
        position: 'absolute', top: -20, right: -20,
        width: 60, height: 60, borderRadius: '50%',
        background: `${c.dim}`,
        filter: 'blur(20px)',
      }} />

      <div style={{ fontSize: '1.8rem', marginBottom: 8 }}>{icon}</div>

      <motion.div
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '2.2rem',
          fontWeight: 900,
          color: c.main,
          textShadow: `0 0 20px ${c.glow}`,
          lineHeight: 1,
          marginBottom: 8,
        }}
        animate={{ opacity: 1 }}
        initial={{ opacity: 0 }}
      >
        {displayVal()}
      </motion.div>

      <div style={{
        color: 'var(--text-muted)',
        fontSize: '0.7rem',
        textTransform: 'uppercase',
        letterSpacing: 2.5,
        fontWeight: 600,
      }}>
        {label}
      </div>
    </motion.div>
  )
}
