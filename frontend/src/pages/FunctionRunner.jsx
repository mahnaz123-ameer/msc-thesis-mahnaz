import React, { useState, useEffect } from 'react'
import { getProjects, getFunctions, runFunction } from '../api'

const EXAMPLES = [
  { label: 'calculate_cgpa',       hint: '[[[85,3],[70,4],[90,2]]]',   project: '01_university_management', file: 'grades.py',       fn: 'calculate_cgpa' },
  { label: 'assign_letter_grade',  hint: '[85]',                        project: '01_university_management', file: 'grades.py',       fn: 'assign_letter_grade' },
  { label: 'calculate_emi',        hint: '[100000, 12, 24]',            project: '02_banking_system',        file: 'loans.py',        fn: 'calculate_emi' },
  { label: 'calculate_total_fare', hint: '["bike", 5, 20]',             project: '05_ride_sharing',          file: 'fare.py',         fn: 'calculate_total_fare' },
  { label: 'calculate_bed_charge', hint: '["private", 5]',              project: '03_hospital_management',   file: 'billing.py',      fn: 'calculate_bed_charge' },
  { label: 'apply_discount',       hint: '[{}, "P1", 20]',              project: '04_ecommerce_system',      file: 'product.py',      fn: 'apply_discount' },
]

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
    setArgs(fn ? fn.args.map(() => '') : [])
    setResult(null)
  }

  const run = async () => {
    setLoading(true); setResult(null)
    try {
      const parsed = args.map(a => { try { return JSON.parse(a) } catch { return a } })
      const r = await runFunction(sel.project, sel.file, sel.fn, parsed)
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
    setArgs(fn ? fn.args.map((_, i) => JSON.stringify(hintArgs[i] ?? '')) : [])
    setResult(null)
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-lg font-bold text-white">▶ Function Runner</h2>
        <p className="text-xs text-slate-400 mt-0.5">Select any function from your 557 functions and run it with real inputs</p>
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
                  {functions.map(f => <option key={f.name} value={f.name}>{f.name}()</option>)}
                </select>
              </div>
            </div>
          </div>

          {/* Args + run */}
          {fnInfo && (
            <div className="card space-y-3">
              <div>
                <div className="text-sm font-mono text-primary font-bold">{fnInfo.name}({fnInfo.args.join(', ')})</div>
                {fnInfo.docstring && <div className="text-xs text-slate-400 mt-1 italic">{fnInfo.docstring}</div>}
              </div>
              <div className="space-y-2">
                <label className="text-xs text-slate-500 uppercase tracking-wider">Arguments — JSON format</label>
                {fnInfo.args.map((arg, i) => (
                  <div key={arg} className="flex items-center gap-3">
                    <span className="text-xs font-mono text-yellow-400 w-28 shrink-0">{arg}:</span>
                    <input
                      value={args[i] || ''}
                      onChange={e => { const a = [...args]; a[i] = e.target.value; setArgs(a) }}
                      placeholder={`value for ${arg}`}
                      className="input font-mono text-xs"
                    />
                  </div>
                ))}
              </div>
              <button onClick={run} disabled={loading} className="btn-primary w-full">
                {loading ? '⏳ Running...' : '▶ Run Function'}
              </button>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className={`card border ${result.success ? 'border-green-700/50' : 'border-red-700/50'}`}>
              <div className="flex items-center gap-2 mb-2">
                <span>{result.success ? '✅' : '❌'}</span>
                <span className="text-sm font-semibold">{result.success ? 'Result' : 'Error'}</span>
                {result.type && <span className="text-xs text-slate-500 font-mono">({result.type})</span>}
              </div>
              <pre className={`text-sm font-mono p-3 rounded-lg overflow-x-auto ${
                result.success ? 'bg-green-900/20 text-green-300' : 'bg-red-900/20 text-red-300'
              }`}>
                {result.success ? JSON.stringify(result.result, null, 2) : result.error}
              </pre>
            </div>
          )}

          {/* Quick examples */}
          <div className="card">
            <h3 className="text-xs text-slate-400 uppercase tracking-wider mb-3">Quick Examples — Click to Load</h3>
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
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Run History</span>
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
                  → {h.result.success ? JSON.stringify(h.result.result) : '❌ ' + h.result.error}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
