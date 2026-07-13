import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, RefreshCw, Trash2, AlertTriangle, Database, FileText, ChevronDown, ChevronUp, Layers, Book, UploadCloud, CheckCircle, XCircle } from 'lucide-react'

export default function Sidebar({ open, kbStatus, onStatusRefresh }) {
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
      setUploadResults([{ filename: 'Error', success: false, message: e.message }])
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

  return (
    <AnimatePresence>
      {open && (
        <motion.aside
          key="sidebar"
          initial={{ x: -280, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -280, opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          style={{
            position: 'fixed',
            top: 'var(--navbar-h)',
            left: 0,
            width: 'var(--sidebar-w)',
            height: 'calc(100vh - var(--navbar-h))',
            background: 'rgba(5, 6, 18, 0.98)',
            borderRight: '1px solid rgba(255,255,255,0.06)',
            backdropFilter: 'blur(20px)',
            overflowY: 'auto',
            overflowX: 'hidden',
            padding: '20px 16px',
            zIndex: 900,
            display: 'flex',
            flexDirection: 'column',
            gap: 20,
          }}
        >
          {/* KB Stats */}
          <div>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: 2, marginBottom: 12 }}>
              Knowledge Base
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {/* Chunks */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: 10, padding: '10px 14px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
                  <div style={{ width: 28, height: 28, borderRadius: 7, background: 'rgba(0,255,247,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Layers size={14} color="var(--cyan)" />
                  </div>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Chunks</span>
                </div>
                <span style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--cyan)', fontFamily: 'var(--font-display)' }}>
                  {kbStatus.chunks}
                </span>
              </div>

              {/* Docs */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: 10, padding: '10px 14px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
                  <div style={{ width: 28, height: 28, borderRadius: 7, background: 'rgba(191,0,255,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Book size={14} color="var(--purple)" />
                  </div>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Documents</span>
                </div>
                <span style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--purple)', fontFamily: 'var(--font-display)' }}>
                  {kbStatus.sources?.length || 0}
                </span>
              </div>
            </div>
          </div>

          <div style={{ height: 1, background: 'rgba(255,255,255,0.05)', flexShrink: 0 }} />

          {/* Upload */}
          <div>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: 2, marginBottom: 12 }}>
              Upload Documents
            </div>

            <motion.div
              whileHover={{ borderColor: 'rgba(0,255,247,0.4)', background: 'rgba(0,255,247,0.03)' }}
              animate={{ borderColor: dragOver ? 'var(--cyan)' : 'rgba(255,255,255,0.08)' }}
              onClick={() => fileRef.current?.click()}
              onDragOver={e => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={e => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files) }}
              style={{
                background: 'rgba(255,255,255,0.02)',
                border: '1px dashed rgba(255,255,255,0.1)',
                borderRadius: 12,
                padding: '20px 12px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                marginBottom: 10,
              }}
            >
              {uploading ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
                  <div className="spinner" style={{ width: 22, height: 22, borderWidth: 2 }} />
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Indexing...</div>
                </div>
              ) : (
                <>
                  <UploadCloud size={22} color="var(--text-dim)" style={{ marginBottom: 8 }} />
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: 3 }}>
                    Drop files here
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>PDF · TXT · DOCX</div>
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
              <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
                {uploadResults.map((r, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    fontSize: '0.73rem', padding: '6px 10px', borderRadius: 7,
                    background: r.success ? 'rgba(0,255,136,0.06)' : 'rgba(255,68,102,0.06)',
                    color: r.success ? 'var(--green)' : 'var(--red)',
                  }}>
                    {r.success ? <CheckCircle size={12} /> : <XCircle size={12} />}
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {r.filename}
                    </span>
                  </div>
                ))}
              </motion.div>
            )}

            {/* Load sample */}
            <motion.button
              whileHover={{ scale: 1.02, background: 'rgba(255,255,255,0.06)' }}
              whileTap={{ scale: 0.98 }}
              onClick={handleLoadSample}
              disabled={loadingSample}
              style={{
                width: '100%', background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.07)',
                borderRadius: 10, padding: '10px 0',
                color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
                cursor: loadingSample ? 'not-allowed' : 'pointer', transition: 'all 0.2s',
              }}
            >
              {loadingSample ? <div className="spinner" style={{ width: 13, height: 13, borderWidth: 2 }} /> : <Database size={13} />}
              Load Sample KB
            </motion.button>
          </div>

          {/* Indexed sources */}
          {kbStatus.sources?.length > 0 && (
            <>
              <div style={{ height: 1, background: 'rgba(255,255,255,0.05)', flexShrink: 0 }} />
              <div>
                <button
                  onClick={() => setFilesExpanded(f => !f)}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                    color: 'var(--text-secondary)', fontSize: '0.78rem', fontWeight: 600,
                    padding: '4px 0',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <FileText size={13} />
                    Indexed Files ({kbStatus.sources.length})
                  </div>
                  {filesExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
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
                      <div style={{ paddingTop: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
                        {kbStatus.sources.map((s, i) => (
                          <div key={i} style={{
                            fontSize: '0.72rem', color: 'var(--text-dim)',
                            background: 'rgba(255,255,255,0.02)',
                            padding: '5px 10px', borderRadius: 6,
                            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                          }}>
                            {s}
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </>
          )}

          {/* Bottom actions */}
          <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
            <motion.button
              whileHover={{ background: 'rgba(255,68,102,0.08)', borderColor: 'rgba(255,68,102,0.35)', color: 'var(--red)' }}
              whileTap={{ scale: 0.98 }}
              onClick={handleResetKB}
              disabled={resetting}
              style={{
                width: '100%', background: 'transparent',
                border: '1px solid rgba(255,68,102,0.18)',
                borderRadius: 10, padding: '10px 0',
                color: 'rgba(255,68,102,0.6)', fontSize: '0.78rem', fontWeight: 600,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
                cursor: resetting ? 'not-allowed' : 'pointer', transition: 'all 0.2s',
              }}
            >
              {resetting ? <div className="spinner" style={{ width: 13, height: 13, borderWidth: 2, borderColor: 'var(--red)' }} /> : <AlertTriangle size={13} />}
              Reset Knowledge Base
            </motion.button>

            <motion.button
              whileHover={{ color: '#fff' }}
              whileTap={{ scale: 0.95 }}
              onClick={onStatusRefresh}
              style={{
                background: 'transparent', border: 'none',
                padding: '8px 0', color: 'var(--text-dim)',
                fontSize: '0.73rem', fontWeight: 600,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                cursor: 'pointer', transition: 'all 0.2s',
              }}
            >
              <RefreshCw size={12} />
              Refresh Status
            </motion.button>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
