
import { useState } from 'react'
import './App.css'

const API_BASE = 'http://127.0.0.1:8000'

function App() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('')
  const [result, setResult] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)

  async function uploadContract(event) {
    event.preventDefault()

    if (!file) {
      setMessage('Please select a PDF contract first.')
      return
    }

    setStatus('uploading')
    setMessage('Uploading your contract...')
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(await response.text())
      }

      const uploadData = await response.json()
      const jobId = uploadData.job_id

      if (!jobId) {
        throw new Error('The API did not return a job ID.')
      }

      setStatus('processing')
      setMessage(`Contract accepted. Job ID: ${jobId}`)

      // Check processing status every 2 seconds.
      for (let attempt = 0; attempt < 120; attempt++) {
        await new Promise(resolve => setTimeout(resolve, 2000))

        const statusResponse = await fetch(
          `${API_BASE}/status/${encodeURIComponent(jobId)}`
        )

        if (!statusResponse.ok) {
          throw new Error('Could not retrieve processing status.')
        }

        const statusData = await statusResponse.json()
        const currentStatus = String(statusData.status || '').toLowerCase()

        if (currentStatus === 'failed') {
          throw new Error(statusData.error || 'Contract processing failed.')
        }

        if (currentStatus === 'done') {
          const resultResponse = await fetch(
            `${API_BASE}/contracts/${encodeURIComponent(jobId)}`
          )

          if (!resultResponse.ok) {
            throw new Error('Processing finished, but results could not be loaded.')
          }

          const resultData = await resultResponse.json()
          setResult(resultData)
          setStatus('done')
          setMessage('Contract analysis completed successfully.')
          return
        }

        setMessage(`Contract is ${currentStatus || 'processing'}...`)
      }

      throw new Error('Processing is taking longer than expected. Check the job status.')
    } catch (error) {
      setStatus('failed')
      setMessage(
        error.message.includes('Failed to fetch')
          ? 'Cannot reach the backend. Check that FastAPI is running and CORS is configured.'
          : error.message
      )
    }
  }

  async function searchClauses(event) {
    event.preventDefault()

    if (!searchQuery.trim()) return

    setSearching(true)
    setSearchResults([])

    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery.trim(),
          top_k: 5,
        }),
      })

      if (!response.ok) {
        throw new Error(await response.text())
      }

      const data = await response.json()
      const items = Array.isArray(data)
        ? data
        : data.results || data.matches || data.clauses || [data]

      setSearchResults(items)
    } catch (error) {
      setSearchResults([{ error: error.message }])
    } finally {
      setSearching(false)
    }
  }

  const clauses = result?.clauses || []

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#dashboard">
          <span className="brand-icon">C</span>
          <span>
            <strong>ContractIQ</strong>
            <small>INTELLIGENCE PLATFORM</small>
          </span>
        </a>

        <p className="nav-label">WORKSPACE</p>

        <a className="nav-item active" href="#dashboard">
          <span>▦</span> Dashboard
        </a>
        <a className="nav-item" href="#upload">
          <span>↑</span> Upload contract
        </a>
        <a className="nav-item" href="#analysis">
          <span>≡</span> Analysis results
        </a>
        <a className="nav-item" href="#search">
          <span>⌕</span> Clause search
        </a>

        <div className="sidebar-bottom">
          <span className="status-dot" />
          <span>
            <strong>AI engine</strong>
            <small>Connected when API is available</small>
          </span>
        </div>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <div>
            <p className="eyebrow">CONTRACT WORKSPACE</p>
            <h1>Contract Intelligence</h1>
            <p className="subtitle">
              Extract, classify, and explore contract information.
            </p>
          </div>
          <div className="backend-badge">
            <span className="status-dot" />
            FastAPI backend
          </div>
        </header>

        <section className="welcome-banner">
          <div>
            <p className="eyebrow light">AI-POWERED CONTRACT ANALYSIS</p>
            <h2>Understand your contracts better.</h2>
            <p>
              Upload a PDF to extract clauses, identify entities, and explore
              relevant contract language.
            </p>
            <a className="primary-button banner-button" href="#upload">
              Analyse a contract <span>→</span>
            </a>
          </div>
          <div className="banner-art" aria-hidden="true">
            <div className="document-art">
              <span />
              <span />
              <span />
              <span />
              <b>AI</b>
            </div>
          </div>
        </section>

        <section className="stats-grid" aria-label="Analysis statistics">
          <article className="stat-card">
            <span className="stat-icon purple">▤</span>
            <p>Characters extracted</p>
            <h3>
              {result
                ? Number(result.characters_extracted || 0).toLocaleString()
                : '—'}
            </h3>
            <small>From the uploaded contract</small>
          </article>

          <article className="stat-card">
            <span className="stat-icon blue">≡</span>
            <p>Clauses identified</p>
            <h3>{result ? result.num_clauses ?? clauses.length : '—'}</h3>
            <small>Segmented contract text</small>
          </article>

          <article className="stat-card">
            <span className="stat-icon green">◇</span>
            <p>Vectors stored</p>
            <h3>{result ? result.vectors_stored ?? '—' : '—'}</h3>
            <small>Reported by the backend</small>
          </article>
        </section>

        <section className="content-grid">
          <article className="panel upload-panel" id="upload">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">DOCUMENT INGESTION</p>
                <h2>Upload a contract</h2>
              </div>
              <span className="step-number">01</span>
            </div>

            <form onSubmit={uploadContract}>
              <label className="drop-zone">
                <span className="upload-icon">↑</span>
                <strong>{file ? file.name : 'Choose a PDF contract'}</strong>
                <span>
                  {file
                    ? `${(file.size / 1024 / 1024).toFixed(2)} MB`
                    : 'Select a file from your computer'}
                </span>
                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={event => {
                    const selected = event.target.files?.[0]
                    setFile(selected || null)
                    setMessage('')
                    setStatus('idle')
                    setResult(null)
                  }}
                />
                <span className="browse-button">Browse files</span>
              </label>

              <button
                className="primary-button full-button"
                type="submit"
                disabled={!file || status === 'uploading' || status === 'processing'}
              >
                {status === 'uploading'
                  ? 'Uploading...'
                  : status === 'processing'
                    ? 'Analysing contract...'
                    : 'Upload and analyse'}
                <span>→</span>
              </button>
            </form>

            {message && (
              <div className={`message-box ${status}`} role="status">
                <span>
                  {status === 'done' ? '✓' : status === 'failed' ? '!' : '•'}
                </span>
                {message}
              </div>
            )}

            <p className="privacy-note">
              PDF files only. Upload contracts that you are authorised to process.
            </p>
          </article>

          <article className="panel process-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">HOW IT WORKS</p>
                <h2>Analysis pipeline</h2>
              </div>
            </div>

            {[
              ['01', 'Text extraction', 'OCR extracts text from PDF pages.'],
              ['02', 'Clause segmentation', 'Contract text is divided into clauses.'],
              ['03', 'AI classification', 'The classifier predicts clause categories.'],
              ['04', 'Entity extraction', 'spaCy identifies named entities.'],
              ['05', 'Vector storage', 'Clauses are sent to vector search storage.'],
            ].map(([number, title, description], index) => (
              <div className="pipeline-step" key={number}>
                <span className={`pipeline-number ${index === 0 && status === 'processing' ? 'working' : ''}`}>
                  {number}
                </span>
                <div>
                  <strong>{title}</strong>
                  <p>{description}</p>
                </div>
              </div>
            ))}
          </article>
        </section>

        <section className="panel results-panel" id="analysis">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">CONTRACT INSIGHTS</p>
              <h2>Extracted clauses</h2>
            </div>
            <span className="result-count">
              {clauses.length} {clauses.length === 1 ? 'clause' : 'clauses'}
            </span>
          </div>

          {!result && (
            <div className="empty-state">
              <span className="empty-icon">▤</span>
              <strong>Your analysis will appear here</strong>
              <p>Upload a PDF to review its extracted clauses and entities.</p>
            </div>
          )}

          {result && clauses.length === 0 && (
            <p className="empty-state">The backend returned no clauses.</p>
          )}

          {clauses.slice(0, 20).map((clause, index) => {
            const label =
              clause.clause_type ||
              clause.label ||
              clause.predicted_label ||
              clause.category ||
              'Unlabelled clause'

            return (
              <article className="clause-card" key={clause.clause_id ?? index}>
                <div className="clause-topline">
                  <span className="clause-label">{String(label)}</span>
                  <span className="clause-id">
                    Clause {clause.clause_id ?? index + 1}
                  </span>
                </div>
                <p className="clause-text">{clause.clause_text || 'No clause text returned.'}</p>

                {Array.isArray(clause.entities) && clause.entities.length > 0 && (
                  <div className="entity-list">
                    {clause.entities.map((entity, entityIndex) => (
                      <span className="entity-chip" key={entityIndex}>
                        {entity.text} · {entity.label}
                      </span>
                    ))}
                  </div>
                )}

                <details className="technical-details">
                  <summary>View prediction details</summary>
                  <pre>{JSON.stringify(clause, null, 2)}</pre>
                </details>
              </article>
            )
          })}

          {clauses.length > 20 && (
            <p className="privacy-note">
              Showing the first 20 clauses. The API returned {clauses.length} in total.
            </p>
          )}
        </section>

        <section className="panel search-panel" id="search">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">SEMANTIC SEARCH</p>
              <h2>Find relevant clauses</h2>
            </div>
          </div>

          <form className="search-form" onSubmit={searchClauses}>
            <input
              type="search"
              value={searchQuery}
              onChange={event => setSearchQuery(event.target.value)}
              placeholder="e.g. What are the termination obligations?"
              aria-label="Search contract clauses"
            />
            <button
              type="submit"
              className="primary-button"
              disabled={!searchQuery.trim() || searching}
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </form>

          {searchResults.map((item, index) => (
            <article className="search-result" key={index}>
              {item.error ? (
                <p className="error-text">{item.error}</p>
              ) : (
                <pre>{JSON.stringify(item, null, 2)}</pre>
              )}
            </article>
          ))}
        </section>

        <footer className="footer">
          ContractIQ · AI-Powered Contract Intelligence &amp; Risk Scoring
        </footer>
      </main>
    </div>
  )
}

export default App
