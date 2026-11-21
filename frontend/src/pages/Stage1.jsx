import React, { useState, useEffect, useMemo } from 'react'
import { stage1Overview, stage1Item, stage1Save, stage1Run, stage1Generate, stage1Delete, stage1ExportUrl } from '../api'

const TOOL_ORDER = ['chatgpt', 'claude', 'gemini']
const LEVEL_STYLE = { simple: 'badge-green', moderate: 'badge-yellow', complex: 'badge-red' }

// Colour of a tool's status for one function
function statusOf(s) {
  if (!s) return { dot: 'bg-slate-700', text: 'not collected yet' }
  if (!s.ran) return { dot: 'bg-slate-400', text: 'saved, not run' }
  if (!s.could_run) return { dot: 'bg-red-500', text: 'could not run (import or syntax error)' }
  if (s.passed === s.total) return { dot: 'bg-green-500', text: `${s.total} tests, all passed` }
  return { dot: 'bg-yellow-400', text: `${s.total} tests: ${s.passed} passed, ${s.total - s.passed} failed` }
}

function RunResult({ run }) {
  if (!run) return null
  const bad = !run.could_run
  const cls = bad ? 'border-red-800/60 bg-red-900/20' : run.passed === run.total ? 'border-green-800/60 bg-green-900/20' : 'border-yellow-800/60 bg-yellow-900/10'
  return (
    <div className={`rounded-lg border p-3 ${cls}`}>
      <div className="text-sm font-semibold text-white">
        {bad ? '❌ The test file could not run'
          : run.passed === run.total ? `✅ ${run.total} tests — all passed`
          : `⚠ ${run.total} tests — ${run.passed} passed, ${run.failed} failed${run.errors ? `, ${run.errors} errors` : ''}`}
      </div>
      <div className="text-xs text-slate-400 mt-0.5">
        {bad ? 'Usually a wrong import or a syntax error in the AI answer. The output below shows why.'
          : run.passed === run.total ? 'Every test the AI wrote agrees with the real code.'
          : 'Failed tests expect a different answer than the real code gives — the AI guessed wrong (or found a bug).'}
        {' '}Ran {run.ran_at}.
      </div>
      <details className="mt-2">
        <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-300">Show pytest output</summary>
        <pre className="mt-2 text-xs font-mono text-slate-300 whitespace-pre-wrap max-h-72 overflow-auto">{run.output}</pre>
      </details>
    </div>
  )
}

function ToolPanel({ item, tool, info, saved, onChange }) {
  const [text, setText]   = useState('')
  const [busy, setBusy]   = useState('')
  const [error, setError] = useState('')
  const [edit, setEdit]   = useState(false)

  useEffect(() => { setText(''); setError(''); setEdit(false) }, [item.id, tool])

  const act = async (label, fn) => {
    setBusy(label); setError('')
    try { onChange(tool, (await fn()).data) }
    catch (e) { setError(e.response?.data?.detail || e.message) }
    setBusy('')
  }

  const showEditor = !saved || edit
  return (
    <div className="space-y-3">
      {showEditor ? (
        <>
          <div className="text-xs text-slate-400 leading-relaxed">
            Paste the prompt into <b className="text-slate-200">{info.where}</b>, then paste the <b>whole answer</b> here —
            the test code is taken out of it automatically.
          </div>
          <textarea value={text} onChange={e => setText(e.target.value)} rows={12} spellCheck={false}
            placeholder={`Paste ${info.name}'s answer here…`}
            className="input font-mono text-xs resize-y" />
          <div className="flex flex-wrap gap-2">
            <button disabled={!text.trim() || !!busy} className="btn-primary"
              onClick={() => act('save', () => stage1Save(item.id, tool, text))}>
              {busy === 'save' ? '⏳ Saving and running tests…' : '💾 Save & run tests'}
            </button>
            {info.auto && (
              <button disabled={!!busy} className="btn-secondary"
                onClick={() => act('gen', () => stage1Generate(item.id, tool))}>
                {busy === 'gen' ? `⏳ Asking ${info.name}…` : `⚡ Generate with ${info.name} API (${info.model})`}
              </button>
            )}
            {saved && <button className="btn-secondary" onClick={() => setEdit(false)}>Cancel</button>}
          </div>
          {!info.auto && info.key_env && (
            <div className="text-[11px] text-slate-600">
              Optional: set <code className="text-slate-400">{info.key_env}</code> before starting the backend to generate automatically.
            </div>
          )}
        </>
      ) : (
        <>
          <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
            <span>Saved {saved.saved_at}</span>
            <span>·</span>
            <span>{saved.source === 'api' ? `generated via API (${saved.model})` : 'pasted by hand'}</span>
            <span>·</span>
            <span>{saved.test_functions ?? '?'} test functions</span>
            <div className="ml-auto flex gap-2">
              <button className="btn-secondary !py-1 !px-3 text-xs" disabled={!!busy}
                onClick={() => act('run', () => stage1Run(item.id, tool))}>
                {busy === 'run' ? '⏳ Running…' : '▶ Run again'}
              </button>
              <button className="btn-secondary !py-1 !px-3 text-xs" onClick={() => { setText(saved.code); setEdit(true) }}>
                ✏ Replace
              </button>
              <button className="btn-secondary !py-1 !px-3 text-xs text-red-300" disabled={!!busy}
                onClick={() => window.confirm(`Delete the saved ${info.name} tests for ${item.function}?`) &&
                  act('del', async () => { await stage1Delete(item.id, tool); return { data: null } })}>
                🗑 Delete
              </button>
            </div>
          </div>
          <RunResult run={saved.run} />
          <details>
            <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-300">Show saved test code</summary>
            <pre className="mt-2 text-xs font-mono text-green-300 whitespace-pre-wrap bg-slate-900/60 rounded-lg p-3 max-h-96 overflow-auto">{saved.code}</pre>
          </details>
        </>
      )}
      {error && <div className="text-xs text-red-300">⚠ {error}</div>}
    </div>
  )
}

export default function Stage1() {
  const [data, setData]       = useState(null)
  const [loadErr, setLoadErr] = useState('')
  const [filter, setFilter]   = useState({ project: '', level: '', missing: '' })
  const [selId, setSelId]     = useState(null)
  const [item, setItem]       = useState(null)
  const [tool, setTool]       = useState('chatgpt')
  const [copied, setCopied]   = useState(false)

  const load = () => stage1Overview().then(r => setData(r.data)).catch(e => setLoadErr(e.message))
  useEffect(() => { load() }, [])

  const select = async (id) => {
    setSelId(id); setItem(null); setCopied(false)
    const r = await stage1Item(id).catch(() => null)
    setItem(r?.data || null)
  }

  // a tool's saved test changed -> update the detail and the overview row
  const onChange = (t, saved) => {
    setItem(it => ({ ...it, tests: { ...it.tests, [t]: saved } }))
    load()
  }

  const rows = useMemo(() => (data?.functions || []).filter(f =>
    (!filter.project || f.project === filter.project) &&
    (!filter.level || f.level === filter.level) &&
    (!filter.missing || !f.status[filter.missing])
  ), [data, filter])

  if (loadErr) return <div className="card text-red-300 text-sm">Could not load Stage 1: {loadErr}</div>
  if (!data) return <div className="text-slate-400 text-sm">Loading Stage 1…</div>

  const fns = data.functions
  const projects = [...new Map(fns.map(f => [f.project, f.project_name])).entries()]
  const countLevel = (l) => fns.filter(f => f.level === l).length

  const copyPrompt = async () => {
    try { await navigator.clipboard.writeText(item.prompt); setCopied(true); setTimeout(() => setCopied(false), 2000) }
    catch { setCopied(false) }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-white">🤖 Stage 1 — AI Test Generation</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            The same prompt goes to ChatGPT, Claude and Gemini for every function. Their test files are saved and run here.
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} className="btn-secondary text-xs">🔄 Refresh</button>
          <a href={stage1ExportUrl()} className="btn-secondary text-xs">⬇ Download results (CSV)</a>
        </div>
      </div>

      {/* How to */}
      <div className="card">
        <h3 className="text-sm font-semibold text-slate-300 mb-2">How to finish Stage 1</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <div className="text-xs font-semibold text-green-400 mb-1">A. Automatic — all functions (recommended)</div>
            <ol className="text-xs text-slate-400 space-y-1 list-decimal ml-4">
              <li>Copy <code className="text-slate-300">backend/.env.example</code> to <code className="text-slate-300">backend/.env</code> and put your API keys in it.</li>
              <li>In a terminal: <code className="text-slate-300">cd backend && python3 stage1_generate_all.py --tool all</code></li>
              <li>Leave it running. You can stop it any time and start it again — it continues where it stopped.</li>
              <li>Press <b className="text-slate-200">Refresh</b> here to watch the dots fill up.</li>
            </ol>
            <div className="text-[11px] mt-1 text-slate-500">
              API keys:{' '}
              {TOOL_ORDER.map((t, i) => (
                <span key={t}>
                  {i > 0 && ' · '}{data.tools[t].name}{' '}
                  {data.tools[t].auto ? <span className="text-green-400">✓ found</span> : <span className="text-red-300">missing</span>}
                </span>
              ))}
              {' '}(restart the backend after editing .env)
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-300 mb-1">B. By hand — one function at a time</div>
            <ol className="text-xs text-slate-400 space-y-1 list-decimal ml-4">
              <li>Pick a function and click <b className="text-slate-200">Copy prompt</b>.</li>
              <li>Paste it into ChatGPT, Claude and Gemini (a <b>new chat</b> each time).</li>
              <li>Paste each answer into that tool's tab and click <b className="text-slate-200">Save & run tests</b>.</li>
            </ol>
          </div>
        </div>
        <div className="text-[11px] text-slate-500 mt-2">Stage 1 is finished when every function has a green or yellow dot for all three tools.</div>
      </div>

      {/* Progress */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="card">
          <div className="text-xs text-slate-500">Functions in dataset</div>
          <div className="text-2xl font-bold text-white">{fns.length}</div>
          <div className="text-xs text-slate-400 mt-1">
            {countLevel('simple')} simple · {countLevel('moderate')} moderate · {countLevel('complex')} complex
          </div>
        </div>
        {TOOL_ORDER.map(t => {
          const got = fns.filter(f => f.status[t])
          const tests = got.reduce((n, f) => n + (f.status[t].total || 0), 0)
          const passed = got.reduce((n, f) => n + (f.status[t].passed || 0), 0)
          const pct = Math.round(100 * got.length / fns.length)
          return (
            <div key={t} className="card">
              <div className="text-xs text-slate-500">{data.tools[t].name}</div>
              <div className="text-2xl font-bold text-white">{got.length}<span className="text-sm text-slate-500"> / {fns.length}</span></div>
              <div className="h-1.5 bg-slate-800 rounded-full mt-1.5 overflow-hidden">
                <div className="h-full bg-primary" style={{ width: `${pct}%` }} />
              </div>
              <div className="text-xs text-slate-400 mt-1">{tests} tests · {tests ? Math.round(100 * passed / tests) : 0}% passing</div>
            </div>
          )
        })}
      </div>

      {/* Standard prompt */}
      <details className="card">
        <summary className="text-sm font-semibold text-slate-300 cursor-pointer">
          Standard prompt (same for all tools) <span className="text-xs font-normal text-slate-500">— edit stage1/prompt_template.txt to change it</span>
        </summary>
        <pre className="mt-3 text-xs font-mono text-slate-300 whitespace-pre-wrap">{data.prompt_template}</pre>
      </details>

      <div className="grid md:grid-cols-5 gap-4">
        {/* List */}
        <div className="md:col-span-2 card p-0 flex flex-col max-h-[calc(100vh-160px)]">
          <div className="p-3 border-b border-border space-y-2">
            <select className="select" value={filter.project} onChange={e => setFilter(f => ({ ...f, project: e.target.value }))}>
              <option value="">All projects</option>
              {projects.map(([id, name]) => <option key={id} value={id}>{name}</option>)}
            </select>
            <div className="grid grid-cols-2 gap-2">
              <select className="select" value={filter.level} onChange={e => setFilter(f => ({ ...f, level: e.target.value }))}>
                <option value="">All levels</option>
                <option value="simple">Simple</option>
                <option value="moderate">Moderate</option>
                <option value="complex">Complex</option>
              </select>
              <select className="select" value={filter.missing} onChange={e => setFilter(f => ({ ...f, missing: e.target.value }))}>
                <option value="">Any status</option>
                {TOOL_ORDER.map(t => <option key={t} value={t}>Missing {data.tools[t].name}</option>)}
              </select>
            </div>
            <div className="text-xs text-slate-500">
              {rows.length} functions · dots: {TOOL_ORDER.map(t => data.tools[t].name).join(' / ')}
            </div>
          </div>
          <div className="overflow-auto p-2 space-y-1">
            {rows.map(f => (
              <button key={f.id} onClick={() => select(f.id)}
                className={`w-full text-left px-3 py-2 rounded-lg border transition-colors ${
                  selId === f.id ? 'bg-primary/20 border-primary/30' : 'border-transparent hover:bg-slate-800'}`}>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-slate-200 truncate flex-1">{f.function}()</span>
                  <span className={LEVEL_STYLE[f.level]}>{f.level}</span>
                  <span className="flex gap-1">
                    {TOOL_ORDER.map(t => (
                      <span key={t} title={`${data.tools[t].name}: ${statusOf(f.status[t]).text}`}
                        className={`w-2.5 h-2.5 rounded-full ${statusOf(f.status[t]).dot}`} />
                    ))}
                  </span>
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5 truncate">{f.project_name} · {f.file}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Detail */}
        <div className="md:col-span-3 space-y-4">
          {!selId && (
            <div className="card text-center py-16 text-sm text-slate-500">
              Pick a function on the left to get its prompt and collect the AI tests.
            </div>
          )}
          {selId && !item && <div className="card text-sm text-slate-500">Loading…</div>}
          {item && (
            <>
              <div className="card space-y-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-base font-mono font-bold text-primary">{item.function}()</span>
                  <span className={LEVEL_STYLE[item.level]}>{item.level}</span>
                  <span className="text-xs text-slate-500">complexity {item.complexity} · {item.lines} lines</span>
                </div>
                <div className="text-xs text-slate-500 font-mono">{item.project_name} / {item.file}</div>
                {item.summary && <p className="text-sm text-slate-300">{item.summary}</p>}
                <div className="flex flex-wrap gap-2 items-center">
                  <button onClick={copyPrompt} className="btn-primary">{copied ? '✅ Copied!' : '📋 Copy prompt'}</button>
                  <span className="text-xs text-slate-500">Paste it into each AI tool, in a new chat.</span>
                </div>
                <details>
                  <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-300">Show the prompt</summary>
                  <pre className="mt-2 text-xs font-mono text-slate-300 whitespace-pre-wrap bg-slate-900/60 rounded-lg p-3 max-h-96 overflow-auto">{item.prompt}</pre>
                </details>
              </div>

              <div className="card">
                <div className="flex gap-1 border-b border-border mb-4 -mt-1">
                  {TOOL_ORDER.map(t => (
                    <button key={t} onClick={() => setTool(t)}
                      className={`px-3 py-2 text-sm font-medium border-b-2 -mb-px flex items-center gap-2 ${
                        tool === t ? 'border-primary text-primary' : 'border-transparent text-slate-400 hover:text-slate-200'}`}>
                      <span className={`w-2 h-2 rounded-full ${statusOf(data.functions.find(f => f.id === item.id)?.status[t]).dot}`} />
                      {data.tools[t].name}
                    </button>
                  ))}
                </div>
                <ToolPanel item={item} tool={tool} info={data.tools[tool]} saved={item.tests[tool]} onChange={onChange} />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
