import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { MessageSquare, BarChart2, Clock, Home, Menu, X, Zap } from 'lucide-react'

const NAV_ITEMS = [
  { to: '/chat', icon: MessageSquare, label: 'User Portal' },
  { to: '/analytics', icon: BarChart2, label: 'Analytics' },
  { to: '/history', icon: Clock, label: 'History' },
]

export default function Navbar({ sidebarOpen, onToggleSidebar, kbStatus, onHome }) {
  const location = useLocation()

  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      style={{
        position: 'fixed', top: 0, left: 0, right: 0,
        height: 'var(--navbar-h)',
        display: 'flex', alignItems: 'center',
        padding: '0 24px',
        background: 'rgba(2, 2, 9, 0.92)',
        backdropFilter: 'blur(24px)',
        borderBottom: '1px solid rgba(0,255,247,0.08)',
        zIndex: 1000,
        gap: 16,
      }}
    >
      {/* Sidebar toggle */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={onToggleSidebar}
        className="btn btn-icon btn-ghost"
        style={{ flexShrink: 0 }}
      >
        {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
      </motion.button>

      {/* Brand */}
      <motion.div
        style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0, cursor: 'pointer' }}
        onClick={onHome}
        whileHover={{ scale: 1.03 }}
      >
        <motion.div
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          style={{
            width: 32, height: 32,
            background: 'linear-gradient(135deg, var(--cyan), var(--purple))',
            borderRadius: '10px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <Zap size={16} color="#000" fill="#000" />
        </motion.div>
        <div>
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.78rem', fontWeight: 700,
            background: 'linear-gradient(90deg, var(--cyan), var(--purple))',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            letterSpacing: 2,
          }}>AI SUPPORT</div>
          <div style={{ fontSize: '0.6rem', color: 'var(--text-dim)', letterSpacing: 1 }}>CONTROL CENTER</div>
        </div>
      </motion.div>

      {/* Nav links */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 4,
        marginLeft: 'auto',
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 'var(--radius-full)',
        padding: '4px',
      }}>
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => {
          const active = location.pathname === to
          return (
            <NavLink key={to} to={to} style={{ textDecoration: 'none', position: 'relative' }}>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.97 }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 7,
                  padding: '8px 18px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.84rem', fontWeight: active ? 700 : 500,
                  color: active ? '#000' : 'var(--text-secondary)',
                  background: active
                    ? 'linear-gradient(135deg, var(--cyan), #00aacc, var(--purple))'
                    : 'transparent',
                  boxShadow: active ? '0 0 20px rgba(0,255,247,0.3)' : 'none',
                  transition: 'all 0.25s ease',
                }}
              >
                <Icon size={15} />
                {label}
              </motion.div>
            </NavLink>
          )
        })}
      </div>

      {/* KB Status */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '6px 14px',
          background: 'rgba(255,255,255,0.03)',
          border: `1px solid ${kbStatus.online ? 'rgba(0,255,136,0.2)' : 'rgba(255,68,102,0.2)'}`,
          borderRadius: 'var(--radius-full)',
          flexShrink: 0,
        }}
      >
        <span className={`status-dot ${kbStatus.online ? 'online' : 'offline'}`} />
        <span style={{
          fontSize: '0.72rem',
          fontFamily: 'var(--font-display)',
          letterSpacing: 1.5,
          color: kbStatus.online ? 'var(--green)' : 'var(--red)',
        }}>
          {kbStatus.online ? `${kbStatus.chunks} CHUNKS` : 'NO DATA'}
        </span>
      </motion.div>

      {/* Home button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onHome}
        className="btn btn-ghost btn-sm"
        style={{ flexShrink: 0 }}
        title="Back to Home"
      >
        <Home size={14} />
      </motion.button>
    </motion.nav>
  )
}
