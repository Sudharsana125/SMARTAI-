import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Landing from './pages/Landing'
import UserPortal from './pages/UserPortal'
import AnalyticsDashboard from './pages/AnalyticsDashboard'
import History from './pages/History'
import ParticleBackground from './components/ParticleBackground'

export default function App() {
  const [launched, setLaunched] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [kbStatus, setKbStatus] = useState({ online: false, chunks: 0, sources: [] })

  const fetchStatus = async () => {
    try {
      const r = await fetch('/api/status')
      const d = await r.json()
      if (d.ok) setKbStatus({ online: d.online, chunks: d.knowledge_base_chunks, sources: d.indexed_sources })
    } catch (_) {}
  }

  useEffect(() => {
    if (launched) {
      fetchStatus()
      const t = setInterval(fetchStatus, 15000)
      return () => clearInterval(t)
    }
  }, [launched])

  if (!launched) {
    return (
      <>
        <ParticleBackground />
        <Landing onLaunch={() => setLaunched(true)} />
      </>
    )
  }

  return (
    <BrowserRouter>
      <ParticleBackground />
      <div className="app-layout">
        <Navbar
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen(o => !o)}
          kbStatus={kbStatus}
          onHome={() => setLaunched(false)}
        />
        <div className="app-main">
          <Sidebar
            open={sidebarOpen}
            kbStatus={kbStatus}
            onStatusRefresh={fetchStatus}
          />
          <main className={`page-content ${sidebarOpen ? 'with-sidebar' : ''}`}>
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<Navigate to="/chat" replace />} />
                <Route path="/chat" element={<UserPortal />} />
                <Route path="/analytics" element={<AnalyticsDashboard />} />
                <Route path="/history" element={<History />} />
              </Routes>
            </AnimatePresence>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
