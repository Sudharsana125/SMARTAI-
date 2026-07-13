import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { LogIn, Mail, Lock, Sparkles, ArrowRight } from 'lucide-react'

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleLogin = (e) => {
    e.preventDefault()
    if (!email || !password) return
    setIsLoading(true)
    
    // Simulate authentication delay
    setTimeout(() => {
      setIsLoading(false)
      onLogin()
      navigate('/chat')
    }, 1200)
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Dynamic Background Glow */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          position: 'absolute', width: '60vw', height: '60vw',
          background: 'radial-gradient(circle, rgba(191,0,255,0.08) 0%, rgba(0,255,247,0.05) 40%, transparent 70%)',
          borderRadius: '50%',
          top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 0, pointerEvents: 'none'
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, type: 'spring', bounce: 0.4 }}
        style={{
          background: 'rgba(10, 15, 30, 0.6)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0,255,247,0.2)',
          borderRadius: 24,
          padding: '40px 48px',
          width: '100%',
          maxWidth: 440,
          boxShadow: '0 20px 60px rgba(0,0,0,0.5), inset 0 0 20px rgba(0,255,247,0.05)',
          position: 'relative',
          zIndex: 1
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <motion.div 
            initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.2, type: 'spring' }}
            style={{ 
              width: 56, height: 56, borderRadius: '50%', background: 'linear-gradient(135deg, rgba(0,255,247,0.2), rgba(191,0,255,0.2))',
              display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
              border: '1px solid rgba(0,255,247,0.4)', boxShadow: '0 0 20px rgba(0,255,247,0.2)'
            }}
          >
            <Sparkles size={28} color="var(--cyan)" />
          </motion.div>
          
          <h2 style={{ 
            fontFamily: 'var(--font-display)', fontSize: '1.8rem', fontWeight: 800, marginBottom: 8,
            background: 'linear-gradient(90deg, #fff, var(--cyan))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
          }}>
            Welcome Back
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Access your AI Support Workspace</p>
        </div>

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          
          {/* Email Input */}
          <div style={{ position: 'relative' }}>
            <div style={{ position: 'absolute', top: '50%', transform: 'translateY(-50%)', left: 16, color: 'var(--text-muted)' }}>
              <Mail size={18} />
            </div>
            <input 
              type="email" 
              placeholder="Email Address" 
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              style={{
                width: '100%', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 12, padding: '14px 16px 14px 44px', color: '#fff', fontSize: '0.95rem',
                outline: 'none', transition: 'all 0.3s'
              }}
              onFocus={(e) => e.target.style.borderColor = 'var(--cyan)'}
              onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
            />
          </div>

          {/* Password Input */}
          <div style={{ position: 'relative' }}>
            <div style={{ position: 'absolute', top: '50%', transform: 'translateY(-50%)', left: 16, color: 'var(--text-muted)' }}>
              <Lock size={18} />
            </div>
            <input 
              type="password" 
              placeholder="Password" 
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              style={{
                width: '100%', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 12, padding: '14px 16px 14px 44px', color: '#fff', fontSize: '0.95rem',
                outline: 'none', transition: 'all 0.3s'
              }}
              onFocus={(e) => e.target.style.borderColor = 'var(--purple)'}
              onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
            />
          </div>

          {/* Options */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-dim)', cursor: 'pointer' }}>
              <input type="checkbox" style={{ accentColor: 'var(--cyan)' }} /> Remember me
            </label>
            <span style={{ color: 'var(--cyan)', cursor: 'pointer' }}>Forgot Password?</span>
          </div>

          {/* Submit */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={isLoading || !email || !password}
            style={{
              marginTop: 10,
              background: (!email || !password) ? 'rgba(255,255,255,0.05)' : 'linear-gradient(135deg, var(--cyan), var(--purple))',
              border: 'none', borderRadius: 12, padding: '14px',
              color: (!email || !password) ? 'var(--text-muted)' : '#000',
              fontSize: '1rem', fontWeight: 700, cursor: (!email || !password) ? 'default' : 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
              transition: 'all 0.3s'
            }}
          >
            {isLoading ? (
              <div className="spinner" style={{ width: 20, height: 20, borderWidth: 2, borderColor: '#000', borderTopColor: 'transparent' }} />
            ) : (
              <>
                Sign In <ArrowRight size={18} />
              </>
            )}
          </motion.button>
        </form>

      </motion.div>
    </div>
  )
}
