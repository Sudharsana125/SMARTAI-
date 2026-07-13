import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Upload, RefreshCw, AlertTriangle, Database, FileText,
  ChevronDown, ChevronUp, Layers, Book, UploadCloud,
  CheckCircle, XCircle, X
} from 'lucide-react'

export default function KnowledgeBaseModal({ open, onClose, kbStatus, onStatusRefresh }) {
  const [uploading, setUploading] = useState(false)
  const [uploadResults, setUploadResults] = useState([])
  const [loadingSample, setLoadingSample] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [filesExpanded, setFilesExpanded] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef(null)

  const handleUpload = async (files) => {
    if (!files || !files.length) return
    setUploading(true)
    setUploadResults([])
    const fd = new FormData()
    Array.from(files).forEach(f => fd.append('files', f))
    try {
      const r = await fetch('/api/upload', { method: 'POST', body: fd })
      const d = await r.json()
      if (d.ok) setUploadResults(d.results)
    } catch (e) {
      setUploadResults([{ filename: 'Error', success: false }])
    } finally {
      setUploading(false)
      onStatusRefresh()
    }
  }

  const handleLoadSample = async () => {
    setLoadingSample(true)
    try {
      const r = await fetch('/api/load-sample', { method: 'POST' })
      const d = await r.json()
      if (d.ok) onStatusRefresh()
    } catch (_) {}
    setLoadingSample(false)
  }

  const handleResetKB = async () => {
    if (!window.confirm('Reset entire knowledge base? This cannot be undone.')) return
    setResetting(true)
    try {
      await fetch('/api/reset-kb', { method: 'POST' })
      onStatusRefresh()
    } catch (_) {}
    setResetting(false)
  }

  const isOnline = kbStatus.online

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed', inset: 0, zIndex: 1100,
              background: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(6px)',
            }}
          />

          {/* Modal Panel */}
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.97 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            style={{
              position: 'fixed',
              top: 80,
              left: '50%',
              transform: 'translateX(-50%)',
              width: '100%',
              maxWidth: 560,
              zIndex: 1101,
              background: 'rgba(10, 12, 26, 0.98)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 20,
              boxShadow: '0 40px 80px rgba(0,0,0,0.6)',
              overflow: 'hidden',
            }}
          >
            {/* Header */}
            <div style={{
              padding: '20px 24px',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}>
              <div>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: 2 }}>
                  Knowledge Base
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  Manage your indexed documents and data sources
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.1, background: 'rgba(255,255,255,0.08)' }}
                whileTap={{ scale: 0.95 }}
                onClick={onClose}
                style={{
                  width: 32, height: 32, borderRadius: 8,
                  background: 'rgba(255,255,255,0.04)', border: 'none',
                  color: 'var(--text-muted)', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'all 0.2s',
                }}
              >
                <X size={16} />
              </motion.button>
            </div>

            {/* Stats Row */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: 12,
              padding: '20px 24px 0',
            }}>
              <StatRow icon={<Layers size={16} color="var(--cyan)" />} label="Total Chunks" value={kbStatus.chunks} online={isOnline} color="var(--cyan)" />
              <StatRow icon={<Book size={16} color="var(--purple)" />} label="Documents" value={kbStatus.sources?.length || 0} online={isOnline} color="var(--purple)" />
            </div>

            {/* Body */}
            <div style={{ padding: '16px 24px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>

              {/* Drop zone */}
              <motion.div
                whileHover={{ borderColor: 'rgba(0,255,247,0.5)', background: 'rgba(0,255,247,0.03)' }}
                animate={{ borderColor: dragOver ? 'var(--cyan)' : 'rgba(255,255,255,0.08)' }}
                onClick={() => fileRef.current?.click()}
                onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={e => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files) }}
                style={{
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px dashed rgba(255,255,255,0.1)',
                  borderRadius: 14,
                  padding: '28px 20px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                {uploading ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
                    <div className="spinner" style={{ width: 28, height: 28, borderWidth: 2 }} />
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                      Indexing your documents...
                    </div>
                  </div>
                ) : (
                  <>
                    <div style={{
                      width: 48, height: 48, borderRadius: '50%',
                      background: 'rgba(255,255,255,0.04)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      margin: '0 auto 12px',
                    }}>
                      <UploadCloud size={22} color="var(--text-muted)" />
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#fff', fontWeight: 600, marginBottom: 4 }}>
                      Drop files or click to upload
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      Supports PDF, TXT, and DOCX
                    </div>
                  </>
                )}
              </motion.div>

              <input
                ref={fileRef}
                type="file"
                accept=".pdf,.txt,.docx"
                multiple
                style={{ display: 'none' }}
                onChange={e => handleUpload(e.target.files)}
              />

              {/* Upload results */}
              {uploadResults.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{ display: 'flex', flexDirection: 'column', gap: 4 }}
                >
                  {uploadResults.map((r, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'center', gap: 8,
                      fontSize: '0.78rem', padding: '8px 12px', borderRadius: 8,
                      background: r.success ? 'rgba(0,255,136,0.06)' : 'rgba(255,68,102,0.06)',
                      color: r.success ? 'var(--green)' : 'var(--red)',
                    }}>
                      {r.success ? <CheckCircle size={13} /> : <XCircle size={13} />}
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {r.filename}
                      </span>
                    </div>
                  ))}
                </motion.div>
              )}

              {/* Action buttons row */}
              <div style={{ display: 'flex', gap: 8 }}>
                <motion.button
                  whileHover={{ scale: 1.02, background: 'rgba(255,255,255,0.07)' }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleLoadSample}
                  disabled={loadingSample}
                  style={{
                    flex: 1, background: 'rgba(255,255,255,0.04)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: 10, padding: '10px 0',
                    color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600,
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
                    cursor: loadingSample ? 'not-allowed' : 'pointer', transition: 'all 0.2s',
                  }}
                >
                  {loadingSample ? <div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> : <Database size={14} />}
                  Load Sample Data
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02, background: 'rgba(255,255,255,0.07)' }}
                  whileTap={{ scale: 0.98 }}
                  onClick={onStatusRefresh}
                  style={{
                    flex: 1, background: 'rgba(255,255,255,0.04)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: 10, padding: '10px 0',
                    color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600,
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
                    cursor: 'pointer', transition: 'all 0.2s',
                  }}
                >
                  <RefreshCw size={14} />
                  Refresh
                </motion.button>
              </div>

              {/* Indexed files */}
              {kbStatus.sources?.length > 0 && (
                <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 12, overflow: 'hidden' }}>
                  <button
                    onClick={() => setFilesExpanded(f => !f)}
                    style={{
                      width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600,
                      padding: '12px 16px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                      <FileText size={14} /> Indexed Files ({kbStatus.sources.length})
                    </div>
                    {filesExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                  <AnimatePresence>
                    {filesExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        style={{ overflow: 'hidden' }}
                      >
                        <div style={{ padding: '0 12px 12px', display: 'flex', flexDirection: 'column', gap: 4 }}>
                          {kbStatus.sources.map((s, i) => (
                            <div key={i} style={{
                              fontSize: '0.75rem', color: 'var(--text-muted)',
                              background: 'rgba(255,255,255,0.03)', padding: '6px 10px',
                              borderRadius: 6, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                            }}>
                              {s}
                            </div>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}

              {/* Reset */}
              <motion.button
                whileHover={{ background: 'rgba(255,68,102,0.1)', borderColor: 'rgba(255,68,102,0.4)', color: 'var(--red)' }}
                whileTap={{ scale: 0.98 }}
                onClick={handleResetKB}
                disabled={resetting}
                style={{
                  width: '100%', background: 'transparent',
                  border: '1px solid rgba(255,68,102,0.2)',
                  borderRadius: 10, padding: '10px 0',
                  color: 'rgba(255,68,102,0.6)', fontSize: '0.8rem', fontWeight: 600,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
                  cursor: resetting ? 'not-allowed' : 'pointer', transition: 'all 0.2s',
                }}
              >
                {resetting ? <div className="spinner" style={{ width: 14, height: 14, borderWidth: 2, borderColor: 'var(--red)' }} /> : <AlertTriangle size={14} />}
                Reset Knowledge Base
              </motion.button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

function StatRow({ icon, label, value, color }) {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 12, padding: '14px 16px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {icon}
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>{label}</span>
      </div>
      <span style={{ fontSize: '1.1rem', fontWeight: 800, color, fontFamily: 'var(--font-display)' }}>
        {value}
      </span>
    </div>
  )
}
