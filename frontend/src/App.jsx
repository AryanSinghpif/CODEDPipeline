import { useCallback, useEffect, useRef, useState } from 'react'
import gsap from 'gsap'

const API = import.meta.env.VITE_API_URL || ''

const CYCLE_WORDS = ['Extract.', 'Clean.', 'Validate.', 'Catalog.']

/* dev preview: ?stage=processing | ?stage=results renders that stage with mock data */
const PREVIEW = new URLSearchParams(window.location.search).get('stage')
const MOCK_RESULTS = {
  catalog: [
    { table_id: 1, table_name: 'Table 1.1 Area, Total Males Females Population and Density', page: 16, rows: 29, columns: 8, column_names: 's_no|district|area' },
    { table_id: 2, table_name: 'Statement 1.1 First Advance Estimates of Annual GDP', page: 17, rows: 44, columns: 8, column_names: 'item|2024_25' },
    { table_id: 3, table_name: 'Annexure 1.3 Maximum Number of Receipts', page: 23, rows: 9, columns: 9, column_names: 'name|receipts' },
  ],
  failed: [{ table: 7, page: 12, reason: 'mostly_empty' }],
}

export default function App() {
  const [stage, setStage] = useState(PREVIEW || 'upload')
  const [jobId, setJobId] = useState(null)
  const [prog, setProg] = useState({ done: 7, total: 19 })
  const [results, setResults] = useState(PREVIEW === 'results' ? MOCK_RESULTS : null)
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
      <div className="grain" aria-hidden="true" />
      <header>
        <div className="logo">
          <span className="logo-icon">⬡</span>
          <span>CODED<strong>Pipeline</strong></span>
        </div>
        <span className="header-tag">
          {stage === 'upload' && '00 / 03 — waiting'}
          {stage === 'processing' && '01 / 03 — solving'}
          {stage === 'results' && '03 / 03 — solved'}
        </span>
      </header>

      <main>
        {stage === 'upload' && (
          <div className="upload-page">
            <div className="upload-title">
              <p className="kicker">Government PDF → clean data</p>
              <h1>
                Tables, <em><CyclingWord words={CYCLE_WORDS} /></em>
              </h1>
              <p className="lede">
                Upload a statistical report. The pipeline extracts, cleans and
                catalogs every table — then lays them out for you, page by page.
              </p>
            </div>

            <div
              className={`dropzone${dragging ? ' dragging' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              onClick={() => fileRef.current?.click()}
            >
              <div className="dz-icon">PDF</div>
              <p className="dz-main">Drop your report here</p>
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
              <Feature n="01" label="Lattice + stream extraction" sub="Camelot, with borderless fallback" />
              <Feature n="02" label="Hindi-aware cleaning" sub="Strips romanized artifacts" />
              <Feature n="03" label="CSV + catalog" sub="Per-table export with metadata" />
            </div>
          </div>
        )}

        {stage === 'processing' && (
          <div className="processing-page">
            <CubeSolver />
            <h2>Solving your PDF<span className="ellipsis" /></h2>
            <div className="prog-track">
              <div className="prog-fill" style={{ width: `${pct}%` }} />
            </div>
            <p className="prog-label">
              {prog.total > 0
                ? `${prog.done} / ${prog.total} tables — ${pct}%`
                : 'Parsing pages…'}
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

function CyclingWord({ words }) {
  const [i, setI] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setI((v) => (v + 1) % words.length), 1800)
    return () => clearInterval(t)
  }, [words])
  return <span className="cycle-word" key={i}>{words[i]}</span>
}

/* on-palette sticker colours */
const STICKERS = ['#D4C500', '#FEF1D0', '#94B8F2', '#2575F6', '#0042AF', '#EEF4FF']

function StickerRow({ seed }) {
  return (
    <div className="sticker-row">
      {[0, 1, 2].map((c) => (
        <span key={c} className="sticker" style={{ background: STICKERS[(seed + c * 2) % 6] }} />
      ))}
    </div>
  )
}

function Slice({ pos }) {
  return (
    <div className={`slice slice-${pos}`}>
      {[0, 1, 2, 3].map((f) => (
        <div key={f} className={`slice-face sf-${f}`}>
          <StickerRow seed={f + pos.length} />
        </div>
      ))}
      {pos === 'top' && (
        <div className="slice-face sf-up">
          <StickerRow seed={1} />
          <StickerRow seed={3} />
          <StickerRow seed={5} />
        </div>
      )}
    </div>
  )
}

function CubeSolver() {
  const rootRef = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      // GSAP (same engine sleep-well-creatives uses) sequences the
      // "moves": twist a layer, settle, twist the next — like solving.
      const slices = ['.slice-top', '.slice-mid', '.slice-bot']
      const tl = gsap.timeline({ repeat: -1, repeatDelay: 0.2 })

      const dirs = [90, -90, 90, 90, -90, 90]
      slices.concat(slices).forEach((sel, i) => {
        tl.to(sel, {
          rotateY: `+=${dirs[i % dirs.length]}`,
          duration: 0.55,
          ease: 'back.inOut(1.4)',
        }, '+=0.25')
      })

      gsap.to('.cube-rotor', {
        rotateY: '+=360',
        duration: 9,
        ease: 'none',
        repeat: -1,
      })
    }, rootRef)
    return () => ctx.revert()
  }, [])

  return (
    <div className="solver" ref={rootRef}>
      <svg className="person" viewBox="0 0 240 200" fill="none" aria-hidden="true">
        {/* seated figure, line-art */}
        <circle cx="120" cy="48" r="22" stroke="#94B8F2" strokeWidth="4" />
        <path d="M120 70 C 120 100, 118 112, 116 128" stroke="#94B8F2" strokeWidth="4" strokeLinecap="round" />
        {/* crossed legs */}
        <path d="M116 128 C 90 150, 70 156, 48 152 C 80 168, 160 168, 192 152 C 170 156, 142 150, 116 128"
          stroke="#94B8F2" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        {/* left arm */}
        <path className="arm arm-l" d="M118 84 C 96 92, 84 100, 78 112" stroke="#FEF1D0" strokeWidth="4" strokeLinecap="round" />
        {/* right arm */}
        <path className="arm arm-r" d="M122 84 C 144 92, 156 100, 162 112" stroke="#FEF1D0" strokeWidth="4" strokeLinecap="round" />
      </svg>

      <div className="cube-stage">
        <div className="cube-rotor">
          <Slice pos="top" />
          <Slice pos="mid" />
          <Slice pos="bot" />
        </div>
      </div>
      <div className="cube-shadow" />
    </div>
  )
}

function Feature({ n, label, sub }) {
  return (
    <div className="feature">
      <span className="feature-n">{n}</span>
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
      <div className="book">
        <div className="book-spine" />

        <div className="page page-left">
          <p className="page-kicker">The Extraction</p>
          <h2 className="page-title">Solved.</h2>
          <p className="page-sub">Every table in your report, pressed into clean pages.</p>

          <div className="stats">
            <Stat label="Total found" value={catalog.length + failed.length} />
            <Stat label="Extracted" value={catalog.length} type="success" />
            <Stat label="Set aside" value={failed.length} type={failed.length > 0 ? 'warn' : 'dim'} />
          </div>

          <div className="page-actions">
            <a href={`${API}/api/download/${jobId}/all`} className="btn btn-primary" download>
              ↓ Download all CSVs
            </a>
            <button className="btn btn-ghost" onClick={onReset}>
              New PDF
            </button>
          </div>

          {failed.length > 0 && (
            <div className="failed-section">
              <h3>Set aside ({failed.length})</h3>
              {failed.map((f, i) => (
                <div key={i} className="failed-row">
                  Table {f.table} · p{f.page} · <span className="reason">{f.reason}</span>
                </div>
              ))}
            </div>
          )}

          <span className="page-no">i</span>
        </div>

        <div className="page page-right">
          <div className="page-toolbar">
            <p className="page-kicker">Index of tables</p>
            <input
              className="search-input"
              placeholder="Search…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="toc">
            {filtered.map((row) => (
              <a
                key={row.table_id}
                className="toc-row"
                href={`${API}/api/download/${jobId}/${row.table_id}`}
                download
                title={row.column_names?.replace(/\|/g, ', ')}
              >
                <span className="toc-id">{String(row.table_id).padStart(2, '0')}</span>
                <span className="toc-name">{row.table_name}</span>
                <span className="toc-dots" />
                <span className="toc-page">p{row.page}</span>
                <span className="toc-dl">CSV ↓</span>
              </a>
            ))}
            {filtered.length === 0 && (
              <div className="empty-state">No tables match “{search}”</div>
            )}
          </div>

          <span className="page-no">ii</span>
        </div>
      </div>
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
