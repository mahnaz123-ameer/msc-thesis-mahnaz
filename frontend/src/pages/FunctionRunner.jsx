import React, { useState, useEffect, useRef } from 'react'
import { getProjects, getFunctions, runFunction } from '../api'

const EXAMPLES = [
  { label: 'calculate_cgpa',       hint: '[[[85,3],[70,4],[90,2]]]',   project: '01_university_management', file: 'grades.py',       fn: 'calculate_cgpa' },
  { label: 'assign_letter_grade',  hint: '[85]',                        project: '01_university_management', file: 'grades.py',       fn: 'assign_letter_grade' },
  { label: 'calculate_emi',        hint: '[100000, 12, 24]',            project: '02_banking_system',        file: 'loans.py',        fn: 'calculate_emi' },
  { label: 'calculate_total_fare', hint: '["bike", 5, 20]',             project: '05_ride_sharing',          file: 'fare.py',         fn: 'calculate_total_fare' },
  { label: 'calculate_bed_charge', hint: '["private", 5]',              project: '03_hospital_management',   file: 'billing.py',      fn: 'calculate_bed_charge' },
  { label: 'apply_discount',       hint: '[{}, "P1", 20]',              project: '04_ecommerce_system',      file: 'product.py',      fn: 'apply_discount' },
]

// ─── Input help ──────────────────────────────────────────────
const TYPE_WORD = { string: 'text', number: 'number', bool: 'true or false', list: 'list',
                    dict: 'dictionary', record: 'dictionary', any: 'any value' }

// Example value as it should appear in the box (text without quotes)
const exampleText = (p) => {
  if (!p.example_json) return ''
  try { const v = JSON.parse(p.example_json); if (p.type === 'string' && typeof v === 'string') return v } catch {}
  return p.example_json
}

// Short help line shown under each input
const hintFor = (p) => {
  if (p.typeable === false) {
    return `needs a real Python object (${p.annotation || 'object'})` +
      (p.required ? '' : ' — leave empty, the default is used')
  }
  const parts = [TYPE_WORD[p.type] || p.type]
  if (p.label && !['text', 'number', 'bool', 'any value'].includes(p.label) && p.label !== p.annotation) parts.push(p.label)
  if (p.choices?.length) parts.push('one of: ' + p.choices.join(', '))
  if (!p.required) parts.push(p.default != null ? `optional, leave empty for default ${p.default}` : 'optional')
  if (p.source === 'library tests') parts.push("example from the library's own tests")
  return parts.join(' — ')
}

// Turn the boxes into positional args + keyword args
const buildCall = (params, values) => {
  const args = [], kwargs = {}
  let skipped = false
  params.forEach((p, i) => {
    const raw = p.type === 'string' ? (values[i] ?? '') : (values[i] ?? '').trim()
    const parse = (v) => { try { return JSON.parse(v) } catch { return v } }
    if (p.kind === 'var_positional') { if (raw) { const v = parse(raw); if (Array.isArray(v)) args.push(...v) } return }
    if (p.kind === 'var_keyword') { if (raw) { const v = parse(raw); if (v && typeof v === 'object') Object.assign(kwargs, v) } return }
    if (p.typeable === false || (raw === '' && !p.required)) { skipped = true; return }
    const v = p.type === 'string' ? (raw.startsWith('"') ? parse(raw) : raw) : parse(raw)
    if (p.kind === 'keyword_only' || skipped) kwargs[p.name] = v
    else args.push(v)
  })
  return { args, kwargs }
}

// "What it does" box: summary, what you get back, possible results, errors
function About({ fn }) {
  const a = fn.about || {}
  const okCount = (a.outcomes || []).filter(o => o.ok === true).length
  return (
    <div className="mt-3 rounded-lg border border-border bg-slate-900/40 p-3 space-y-2">
      <div className="text-xs font-semibold text-slate-400">What it does</div>
      <p className="text-sm text-slate-200 leading-relaxed">
        {a.summary || 'No description available for this function.'}
      </p>
      {a.returns && (
        <p className="text-xs text-slate-400"><span className="text-slate-500">You get back:</span> {a.returns}</p>
      )}
      {a.outcomes?.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-1">
            Possible results ({okCount} success, {a.outcomes.length - okCount} {a.outcomes.some(o => o.ok === null) ? 'other' : 'refusal'}):
          </div>
          <ul className="space-y-0.5">
            {a.outcomes.map((o, i) => (
              <li key={i} className="text-xs font-mono flex gap-2">
                <span className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${o.ok === true ? 'bg-green-500' : o.ok === false ? 'bg-red-500' : 'bg-slate-500'}`} />
                <span className={o.ok === true ? 'text-green-300' : o.ok === false ? 'text-red-300' : 'text-slate-300'}>{o.message}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {a.raises?.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-1">Raises an error when the input is wrong:</div>
          <ul className="space-y-0.5">
            {a.raises.map((e, i) => (
              <li key={i} className="text-xs font-mono text-orange-300">{e.type}{e.message ? `: ${e.message}` : ''}</li>
            ))}
          </ul>
        </div>
      )}
      {fn.docstring && fn.docstring.trim() !== a.summary && fn.docstring.length > (a.summary || '').length + 20 && (
        <details className="text-xs text-slate-500">
          <summary className="cursor-pointer hover:text-slate-300">Show full documentation</summary>
          <pre className="mt-2 whitespace-pre-wrap font-sans text-slate-400 leading-relaxed">{fn.docstring}</pre>
        </details>
      )}
    </div>
  )
}

// Only list functions that were checked and run fine with the pre-filled values
const works = (f) => f.runnable !== false && f.works !== false

// How a suggested value appears in the box (text without quotes)
const showValue = (p, json) => {
  try { const v = JSON.parse(json); if (p.type === 'string' && typeof v === 'string') return v } catch {}
  return json
}

// Make blank-looking values visible in the list
const VISIBLE = { '': '(empty text)', ' ': '(space)', '\n': '(new line)', '\t': '(tab)' }
const visible = (text) => VISIBLE[text] ?? text

// Input box with a ▾ list of values to choose from — you can also type your own
function ValueBox({ p, value, onChange }) {
  const [open, setOpen] = useState(false)
  const boxRef = useRef(null)
  // close the list when clicking anywhere outside it
  useEffect(() => {
    if (!open) return
    const close = (e) => { if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [open])
  if (p.typeable === false) {
    return (
      <input disabled value=""
        placeholder="Python object — can't be typed here, leave empty"
        className="input font-mono text-xs opacity-50 cursor-not-allowed" />
    )
  }
  const options = p.suggestions || []
  return (
    <div ref={boxRef} className="relative flex-1"
      onKeyDown={e => e.key === 'Escape' && setOpen(false)}>
      <input
        value={value || ''}
        onChange={e => onChange(e.target.value)}
        onFocus={() => !value && options.length && setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        placeholder={exampleText(p) !== '' ? `e.g. ${visible(exampleText(p))}` : `value for ${p.name}`}
        className={`input font-mono text-xs ${options.length ? 'pr-24' : ''}`}
      />
      {options.length > 0 && (
        <button type="button" title="Show options"
          onMouseDown={e => { e.preventDefault(); setOpen(o => !o) }}
          className="absolute right-1 top-1/2 -translate-y-1/2 px-2 py-1 rounded-md text-xs text-slate-300 bg-slate-800 hover:bg-primary/30 hover:text-white border border-border">
          options ▾
        </button>
      )}
      {open && options.length > 0 && (
        <div className="absolute z-20 left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-xl max-h-60 overflow-auto">
          <div className="px-3 py-1.5 text-[11px] text-slate-500 border-b border-border">Choose a value, or type your own</div>
          {options.map(o => (
            <button key={o.value} type="button"
              onMouseDown={e => { e.preventDefault(); onChange(showValue(p, o.value)); setOpen(false) }}
              className="w-full text-left px-3 py-1.5 hover:bg-slate-800 flex items-center justify-between gap-3">
              <span className="font-mono text-xs text-slate-200 truncate">
                {visible(showValue(p, o.value))}
              </span>
              {o.note && <span className="text-[11px] text-slate-500 shrink-0">{o.note}</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default function FunctionRunner() {
  const [projects, setProjects]   = useState([])
  const [files, setFiles]         = useState([])
  const [functions, setFunctions] = useState([])
  const [sel, setSel]             = useState({ project: '', file: '', fn: '' })
  const [fnInfo, setFnInfo]       = useState(null)
  const [args, setArgs]           = useState([])
  const [result, setResult]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [history, setHistory]     = useState([])

  useEffect(() => {
    getProjects().then(r => setProjects(r.data)).catch(() => {})
  }, [])

  const onProject = (e) => {
    const p = projects.find(x => x.id === e.target.value)
    setSel({ project: e.target.value, file: '', fn: '' })
    setFiles(p?.files || [])
    setFunctions([])
    setFnInfo(null)
    setArgs([])
    setResult(null)
  }

  const onFile = async (e) => {
    setSel(s => ({ ...s, file: e.target.value, fn: '' }))
    setFnInfo(null); setArgs([]); setResult(null)
    if (e.target.value && sel.project) {
      const r = await getFunctions(sel.project, e.target.value).catch(() => null)
      setFunctions(r?.data?.functions || [])
    }
  }

  const onFn = (e) => {
    const fn = functions.find(f => f.name === e.target.value)
    setSel(s => ({ ...s, fn: e.target.value }))
    setFnInfo(fn)
    setArgs(fn ? fn.params.map(p => (p.typeable !== false && (p.required || p.source === 'library tests' || p.source === 'sample file') ? exampleText(p) : '')) : [])
    setResult(null)
  }

  const run = async () => {
    setLoading(true); setResult(null)
    try {
      const { args: parsed, kwargs } = buildCall(fnInfo?.params || [], args)
      const r = await runFunction(sel.project, sel.file, sel.fn, parsed, kwargs)
      setResult(r.data)
      setHistory(h => [{ fn: sel.fn, args: parsed, result: r.data, time: new Date().toLocaleTimeString() }, ...h.slice(0, 9)])
    } catch (e) {
      setResult({ success: false, error: e.message })
    }
    setLoading(false)
  }

  const loadExample = async (ex) => {
    setSel({ project: ex.project, file: ex.file, fn: ex.fn })
    const p = projects.find(x => x.id === ex.project)
    setFiles(p?.files || [])
    const r = await getFunctions(ex.project, ex.file).catch(() => null)
    const fns = r?.data?.functions || []
    setFunctions(fns)
    const fn = fns.find(f => f.name === ex.fn)
    setFnInfo(fn)
    const hintArgs = JSON.parse(`[${ex.hint}]`)
    setArgs(fn ? fn.params.map((p, i) => i < hintArgs.length
      ? (p.type === 'string' && typeof hintArgs[i] === 'string' ? hintArgs[i] : JSON.stringify(hintArgs[i]))
      : (p.required ? exampleText(p) : '')) : [])
    setResult(null)
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-white">Run Functions</h2>
        <p className="text-xs text-slate-400 mt-0.5">Select a function — the boxes are filled with example inputs, just press Run</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2 space-y-4">

          {/* Selectors */}
          <div className="card space-y-3">
            <h3 className="text-sm font-semibold text-slate-300">Select Function</h3>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-xs text-slate-500 mb-1 block">Project</label>
                <select value={sel.project} onChange={onProject} className="select">
                  <option value="">Choose...</option>
                  {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-500 mb-1 block">File</label>
                <select value={sel.file} onChange={onFile} className="select">
                  <option value="">Choose...</option>
                  {files.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-500 mb-1 block">Function</label>
                <select value={sel.fn} onChange={onFn} className="select">
                  <option value="">Choose...</option>
                  {functions.filter(works).map(f => <option key={f.name} value={f.name}>{f.name}()</option>)}
                </select>
                {sel.file && functions.length > 0 && (
                  <div className="text-xs text-slate-500 mt-1">
                    {functions.filter(works).length === 0
                      ? 'No function in this file can run on its own — pick another file'
                      : `${functions.filter(works).length} working function${functions.filter(works).length === 1 ? '' : 's'}`
                        + (functions.length > functions.filter(works).length
                          ? ` (${functions.length - functions.filter(works).length} hidden: need a real app, object or setup)` : '')}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Args + run */}
          {fnInfo && (
            <div className="card space-y-3">
              <div>
                <div className="text-sm font-mono text-primary font-bold">{fnInfo.name}({fnInfo.args.join(', ')})</div>
                <About fn={fnInfo} />
              </div>
              <div className="space-y-2">
                <label className="text-xs text-slate-500">Arguments</label>
                {fnInfo.params.length === 0 && (
                  <div className="text-xs text-slate-500">This function needs no input — just press Run.</div>
                )}
                {fnInfo.params.map((p, i) => (
                  <div key={p.name}>
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono text-yellow-400 w-28 shrink-0 truncate" title={p.name}>{p.name}:</span>
                      <ValueBox p={p} value={args[i]}
                        onChange={v => setArgs(a => { const n = [...a]; n[i] = v; return n })} />
                    </div>
                    <div className="text-xs text-slate-500 mt-1 ml-[124px]">{hintFor(p)}</div>
                  </div>
                ))}
              </div>
              <button onClick={run} disabled={loading} className="btn-primary w-full">
                {loading ? 'Running…' : 'Run function'}
              </button>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className={`card border ${result.success ? 'border-green-700/50' : 'border-red-700/50'}`}>
              <div className="flex items-center gap-2 mb-2">
                <span className={`w-2 h-2 rounded-full ${result.success ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm font-semibold">{result.success ? 'Result' : 'Error'}</span>
                {result.type && <span className="text-xs text-slate-500 font-mono">({result.type})</span>}
              </div>
              <pre className={`text-sm font-mono p-3 rounded-lg overflow-x-auto ${
                result.success ? 'bg-green-900/20 text-green-300' : 'bg-red-900/20 text-red-300'
              }`}>
                {result.success ? JSON.stringify(result.result, null, 2) : result.error}
              </pre>
              {result.output && (
                <div className="mt-3">
                  <div className="text-xs text-slate-500 mb-1">Printed output</div>
                  <pre className="text-sm font-mono p-3 rounded-lg bg-slate-900/60 text-slate-200 whitespace-pre-wrap">{result.output}</pre>
                </div>
              )}
            </div>
          )}

          {/* Quick examples */}
          <div className="card">
            <h3 className="text-xs text-slate-400 mb-3">Quick Examples — Click to Load</h3>
            <div className="grid grid-cols-2 gap-2">
              {EXAMPLES.map(ex => (
                <button key={ex.label} onClick={() => loadExample(ex)}
                  className="text-left bg-surface border border-border hover:border-primary/50 rounded-lg p-3 transition-colors">
                  <div className="text-xs font-mono text-primary">{ex.label}()</div>
                  <div className="text-xs text-slate-500 mt-0.5">{ex.hint}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* History */}
        <div className="card p-0 overflow-auto flex flex-col">
          <div className="px-4 py-3 border-b border-border shrink-0">
            <span className="text-xs font-semibold text-slate-400">Run History</span>
          </div>
          <div className="p-2 space-y-2 overflow-auto flex-1">
            {history.length === 0 && (
              <div className="text-xs text-slate-600 text-center py-8">No runs yet</div>
            )}
            {history.map((h, i) => (
              <div key={i} className="bg-surface border border-border rounded-lg p-3 cursor-pointer hover:border-primary/40"
                onClick={() => setResult(h.result)}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-mono text-primary">{h.fn}()</span>
                  <span className="text-xs text-slate-600">{h.time}</span>
                </div>
                <div className="text-xs text-slate-400 truncate">
                  → {h.result.success ? JSON.stringify(h.result.result) : 'Error: ' + h.result.error}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
