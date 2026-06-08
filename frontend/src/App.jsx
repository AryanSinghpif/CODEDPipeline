import { useCallback, useEffect, useRef, useState } from 'react'

const API = import.meta.env.VITE_API_URL || ''

export default function App() {
  const [stage, setStage] = useState('upload')
  const [jobId, setJobId] = useState(null)
  const [prog, setProg] = useState({ done: 0, total: 0 })
  const [results, setResults] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState(null)
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef()

  useEffect(() => {
    if (stage !== 'processing' || !jobId) return
    const iv = setInterval(async () => {
      try {
        const r = await fetch(`${API}/api/status/${jobId}`)
        const d = await r.json()
        setProg({ done: d.progress, total: d.total })
        if (d.status === 'done') {
          clearInterval(iv)
          const rr = await fetch(`${API}/api/results/${jobId}`)
          const rd = await rr.json()
          setResults(rd)
          setStage('results')
        } else if (d.status === 'failed') {
          clearInterval(iv)
          setError('Pipeline failed. Check backend logs.')
          setStage('upload')
        }
      } catch {
        clearInterval(iv)
        setError('Lost connection — is the backend running?')
        setStage('upload')
      }
    }, 1200)
    return () => clearInterval(iv)
  }, [stage, jobId])

  const submit = async (file) => {
    if (!file) return
    if (file.type !== 'application/pdf') {
      setError('PDF files only.')
      return
    }
    setError(null)
    setUploading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const r = await fetch(`${API}/api/process`, { method: 'POST', body: fd })
      const d = await r.json()
      setJobId(d.job_id)
      setProg({ done: 0, total: 0 })
      setStage('processing')
    } catch {
      setError('Upload failed — is the backend running?')
    } finally {
      setUploading(false)
    }
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    submit(e.dataTransfer.files[0])
  }, [])

  const pct = prog.total > 0 ? Math.round((prog.done / prog.total) * 100) : 0

  return (
    <div className="app">
      <header>
        <div className="logo">
          <span className="logo-icon">⬡</span>
          <span>CODED<strong>Pipeline</strong></span>
        </div>
      </header>

      <main>
        {stage === 'upload' && (
          <div className="upload-page">
            <div className="upload-title">
              <h1>Extract Tables from Government PDFs</h1>
              <p>Upload a DES statistical report. The pipeline extracts, cleans, and exports all tables as CSV.</p>
            </div>

            <div
              className={`dropzone${dragging ? ' dragging' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              onClick={() => fileRef.current?.click()}
            >
              <div className="dz-icon">PDF</div>
              <p className="dz-main">Drop your PDF here</p>
              <p className="dz-sub">or click to browse</p>
              <input
                ref={fileRef}
                type="file"
                accept=".pdf"
                style={{ display: 'none' }}
                onChange={(e) => submit(e.target.files[0])}
              />
            </div>

            {error && <p className="msg-error">{error}</p>}
            {uploading && <p className="msg-muted">Uploading…</p>}

            <div className="feature-row">
              <Feature icon="⬡" label="Lattice extraction" sub="Camelot lattice parser" />
              <Feature icon="⬡" label="Hindi-aware cleaning" sub="Strips romanized artifacts" />
              <Feature icon="⬡" label="CSV + catalog" sub="Per-table + metadata export" />
            </div>
          </div>
        )}

        {stage === 'processing' && (
          <div className="processing-page">
            <div className="spinner" />
            <h2>Extracting tables…</h2>
            <div className="prog-track">
              <div className="prog-fill" style={{ width: `${pct}%` }} />
            </div>
            <p className="prog-label">
              {prog.total > 0
                ? `${prog.done} / ${prog.total} tables — ${pct}%`
                : 'Parsing PDF…'}
            </p>
          </div>
        )}

        {stage === 'results' && results && (
          <Results
            results={results}
            jobId={jobId}
            onReset={() => { setStage('upload'); setResults(null); setJobId(null) }}
          />
        )}
      </main>
    </div>
  )
}

function Feature({ icon, label, sub }) {
  return (
    <div className="feature">
      <span className="feature-icon">{icon}</span>
      <span className="feature-label">{label}</span>
      <span className="feature-sub">{sub}</span>
    </div>
  )
}

function Results({ results, jobId, onReset }) {
  const { catalog = [], failed = [] } = results
  const [search, setSearch] = useState('')

  const filtered = catalog.filter((r) =>
    r.table_name?.toLowerCase().includes(search.toLowerCase()) ||
    String(r.table_id).includes(search)
  )

  return (
    <div className="results-page">
      <div className="results-header">
        <div className="stats">
          <Stat label="Total" value={catalog.length + failed.length} />
          <Stat label="Extracted" value={catalog.length} type="success" />
          <Stat label="Failed" value={failed.length} type={failed.length > 0 ? 'warn' : 'dim'} />
        </div>
        <div className="results-actions">
          <input
            className="search-input"
            placeholder="Search tables…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <a
            href={`${API}/api/download/${jobId}/all`}
            className="btn btn-primary"
            download
          >
            ↓ Download All
          </a>
          <button className="btn btn-ghost" onClick={onReset}>
            New PDF
          </button>
        </div>
      </div>

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Table Name</th>
              <th>Page</th>
              <th>Rows</th>
              <th>Cols</th>
              <th>Columns</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row) => (
              <tr key={row.table_id}>
                <td className="mono">{row.table_id}</td>
                <td className="name-cell">{row.table_name}</td>
                <td className="mono">{row.page}</td>
                <td className="mono">{row.rows}</td>
                <td className="mono">{row.columns}</td>
                <td className="cols-cell">{row.column_names?.replace(/\|/g, ', ')}</td>
                <td>
                  <a
                    href={`${API}/api/download/${jobId}/${row.table_id}`}
                    className="btn btn-xs"
                    download
                  >
                    CSV
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="empty-state">No tables match "{search}"</div>
        )}
      </div>

      {failed.length > 0 && (
        <div className="failed-section">
          <h3>Failed ({failed.length})</h3>
          {failed.map((f, i) => (
            <div key={i} className="failed-row">
              Table {f.table} · Page {f.page} · <span className="reason">{f.reason}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function Stat({ label, value, type }) {
  return (
    <div className={`stat stat-${type || 'default'}`}>
      <span className="stat-val">{value}</span>
      <span className="stat-lbl">{label}</span>
    </div>
  )
}
