import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { Zap, Brain, Globe, BarChart2, Database, Sparkles, Send, Bot, User, FileText, Search, MessageSquare, CheckCircle } from 'lucide-react'

const FEATURES = [
  { icon: Brain, title: 'Context-Aware RAG', desc: 'Retrieves highly relevant chunks from your documents to generate precise answers.' },
  { icon: Globe, title: 'Multilingual AI', desc: 'Seamlessly understands and responds in over 50 languages including Tamil and Hindi.' },
  { icon: Database, title: 'Vector Knowledge Base', desc: 'Powered by ChromaDB for lightning-fast semantic search across all your data.' },
  { icon: BarChart2, title: 'Real-time Analytics', desc: 'Track conversation metrics, sentiment, and trending topics instantly.' },
]

const TECH_STACK = ['GEMINI AI', 'CHROMADB', 'TRANSFORMERS', 'PYTHON REST API', 'REACT & VITE', 'FRAMER MOTION']

const TYPEWRITER_WORDS = ['Intelligent', 'Context-Aware', 'Lightning-Fast', 'Multilingual']

function TypewriterText() {
  const [wordIdx, setWordIdx] = useState(0)
  const [chars, setChars] = useState('')
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const word = TYPEWRITER_WORDS[wordIdx]
    let timeout

    if (!deleting && chars.length < word.length) {
      timeout = setTimeout(() => setChars(word.slice(0, chars.length + 1)), 60)
    } else if (!deleting && chars.length === word.length) {
      timeout = setTimeout(() => setDeleting(true), 2500)
    } else if (deleting && chars.length > 0) {
      timeout = setTimeout(() => setChars(chars.slice(0, -1)), 30)
    } else if (deleting && chars.length === 0) {
      setDeleting(false)
      setWordIdx(i => (i + 1) % TYPEWRITER_WORDS.length)
    }
    return () => clearTimeout(timeout)
  }, [chars, deleting, wordIdx])

  return (
    <span className="gradient-text-cyan">
      {chars}
      <motion.span
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.5, repeat: Infinity }}
        style={{ display: 'inline-block', width: 4, background: 'var(--cyan)', marginLeft: 4, height: '0.8em', verticalAlign: 'middle' }}
      />
    </span>
  )
}

function MockChatInterface() {
  const [hoveredCard, setHoveredCard] = useState(null)

  const cardStyle = {
    background: 'rgba(10, 15, 30, 0.75)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: 20,
    padding: '20px 24px',
    width: '320px',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4), inset 0 0 20px rgba(255, 255, 255, 0.02)',
    position: 'absolute',
    cursor: 'pointer',
    userSelect: 'none',
  }

  const cards = [
    {
      id: 'retrieval',
      title: 'Semantic Retrieval',
      icon: Search,
      iconBg: 'rgba(0, 255, 247, 0.1)',
      iconColor: 'var(--cyan)',
      rotate: -6,
      y: -90,
      x: -20,
      zIndex: 1,
      content: (
        <div style={{ marginTop: 16 }}>
          <div style={{ width: '85%', height: 4, background: 'rgba(0, 255, 247, 0.2)', borderRadius: 2 }} />
          <div style={{ width: '60%', height: 4, background: 'rgba(0, 255, 247, 0.1)', borderRadius: 2, marginTop: 8 }} />
        </div>
      )
    },
    {
      id: 'genai',
      title: 'Generative AI',
      icon: MessageSquare,
      iconBg: 'rgba(191, 0, 255, 0.1)',
      iconColor: '#bf00ff',
      rotate: 4,
      y: 10,
      x: 15,
      zIndex: 2,
      content: (
        <div style={{ marginTop: 14 }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0, lineHeight: 1.4 }}>
            Synthesizing response using context...
          </p>
          <div style={{ color: 'var(--cyan)', fontSize: '0.85rem', fontWeight: 600, marginTop: 8 }}>
            Accuracy: 99.8%
          </div>
        </div>
      )
    },
    {
      id: 'source',
      title: 'Source Cited',
      icon: CheckCircle,
      iconBg: 'rgba(0, 255, 136, 0.1)',
      iconColor: '#00ff88',
      rotate: -3,
      y: 110,
      x: -15,
      zIndex: 3,
      content: (
        <div style={{ 
          marginTop: 14, 
          padding: '10px 14px', 
          background: 'rgba(0, 0, 0, 0.25)', 
          borderRadius: 8, 
          borderLeft: '2px solid #00ff88',
          border: '1px solid rgba(255,255,255,0.03)',
          borderLeftColor: '#00ff88'
        }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontStyle: 'italic' }}>
            "Refer to page 12 of Return Policy PDF"
          </span>
        </div>
      )
    }
  ]

  return (
    <div style={{
      position: 'relative',
      height: '380px',
      width: '100%',
      maxWidth: '380px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      {cards.map((card) => {
        const isHovered = hoveredCard === card.id
        return (
          <motion.div
            key={card.id}
            initial={{ opacity: 0, scale: 0.8, rotate: card.rotate }}
            animate={{
              opacity: 1,
              scale: isHovered ? 1.05 : 1,
              rotate: isHovered ? 0 : card.rotate,
              y: card.y,
              x: card.x,
              zIndex: isHovered ? 10 : card.zIndex,
              boxShadow: isHovered 
                ? '0 30px 60px rgba(0,0,0,0.6), 0 0 20px rgba(0,255,247,0.1)' 
                : '0 20px 40px rgba(0,0,0,0.4)'
            }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            onMouseEnter={() => setHoveredCard(card.id)}
            onMouseLeave={() => setHoveredCard(null)}
            style={{
              ...cardStyle,
              border: isHovered ? `1px solid ${card.iconColor}44` : cardStyle.border,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 8,
                background: card.iconBg,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: card.iconColor
              }}>
                <card.icon size={16} />
              </div>
              <span style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 700, letterSpacing: 0.5 }}>
                {card.title}
              </span>
            </div>
            {card.content}
          </motion.div>
        )
      })}
    </div>
  )
}

export default function Landing({ onLaunch }) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e) => setMousePos({ x: e.clientX, y: e.clientY })
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Dynamic ambient glow tracking mouse */}
      <motion.div
        animate={{
          x: mousePos.x - 300,
          y: mousePos.y - 300,
        }}
        transition={{ type: 'tween', ease: 'backOut', duration: 1 }}
        style={{
          position: 'absolute',
          width: 600,
          height: 600,
          background: 'radial-gradient(circle, rgba(0,255,247,0.06) 0%, rgba(191,0,255,0.04) 40%, rgba(0,0,0,0) 70%)',
          borderRadius: '50%',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />

      <div style={{
        maxWidth: 1200,
        margin: '0 auto',
        width: '100%',
        padding: '80px 40px',
        display: 'grid',
        gridTemplateColumns: '1.2fr 0.8fr',
        gap: 60,
        alignItems: 'center',
        flex: 1,
        zIndex: 1,
      }}>
        {/* Left column: Hero Text */}
        <div style={{ paddingRight: 40 }}>
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: 'rgba(0,255,247,0.08)',
              border: '1px solid rgba(0,255,247,0.3)',
              borderRadius: 'var(--radius-full)',
              padding: '6px 20px',
              fontSize: '0.75rem',
              letterSpacing: 2,
              color: 'var(--cyan)',
              textTransform: 'uppercase',
              marginBottom: 30,
            }}
          >
            <Sparkles size={14} /> AI Customer Support Platform
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(2.5rem, 4.5vw, 4.5rem)',
              fontWeight: 900,
              lineHeight: 1.1,
              marginBottom: 24,
            }}
          >
            Build a truly <br />
            <TypewriterText /> <br />
            <span style={{ color: 'var(--text-primary)' }}>Support Experience.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            style={{
              color: 'var(--text-secondary)',
              fontSize: '1.1rem',
              lineHeight: 1.6,
              maxWidth: 480,
              marginBottom: 40,
            }}
          >
            Upload your company documents and instantly deploy a hallucination-free, retrieval-augmented AI assistant that cites its sources.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <motion.button
              onClick={onLaunch}
              className="btn btn-primary"
              whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(0,255,247,0.4)' }}
              whileTap={{ scale: 0.95 }}
              style={{ fontSize: '1.05rem', padding: '18px 48px', gap: 10, borderRadius: 30 }}
            >
              Enter Workspace
              <Zap size={18} fill="currentColor" />
            </motion.button>
          </motion.div>
        </div>

        {/* Right column: Clean Mock Interface */}
        <div style={{ position: 'relative', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <MockChatInterface />
        </div>
      </div>

      {/* Interactive Feature Strip at bottom */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.8 }}
        style={{
          borderTop: '1px solid rgba(255,255,255,0.05)',
          background: 'rgba(0,0,0,0.2)',
          padding: '40px 24px',
          zIndex: 1,
        }}
      >
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24 }}>
          {FEATURES.map((feat, i) => (
            <motion.div
              key={feat.title}
              whileHover={{ y: -5, background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(0,255,247,0.2)' }}
              style={{ padding: 20, borderRadius: 12, border: '1px solid transparent', transition: 'border-color 0.3s' }}
            >
              <feat.icon size={24} color="var(--cyan)" style={{ marginBottom: 16 }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 8 }}>{feat.title}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Tech Stack Marquee */}
      <div style={{ padding: '20px 0', borderTop: '1px solid rgba(255,255,255,0.03)', overflow: 'hidden', whiteSpace: 'nowrap' }}>
        <motion.div
          animate={{ x: [0, -1000] }}
          transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
          style={{ display: 'inline-block' }}
        >
          {[...TECH_STACK, ...TECH_STACK].map((tech, i) => (
            <span key={i} style={{ 
              display: 'inline-block', padding: '0 40px', fontSize: '0.8rem', 
              color: 'var(--text-dim)', letterSpacing: 2, fontWeight: 600 
            }}>
              {tech} •
            </span>
          ))}
        </motion.div>
      </div>

    </div>
  )
}
