import React, { useState, useEffect } from 'react'
import { getProjects, getFunctions, analyzeMutation } from '../api'

const SAMPLE_TESTS = [
  "def test_add_positive():\n    result = add(2, 3)\n    assert result == 5",
  "def test_add_negative():\n    result = add(-1, -2)\n    assert result == -3",
  "def test_add_zero():\n    result = add(0, 5)\n    assert result == 5",
  "def test_add_exists():\n    result = add(2, 3)\n    assert result is not None",
]

function ScoreRing({ score }) {
  const pct = Math.round(score * 100)
  const color = pct >= 80 ? '#4ade80' : pct >= 50 ? '#facc15' : '#f87171'
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-28 h-28">
        <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="#334155" strokeWidth="3" />
          <circle cx="18" cy="18" r="15.9" fill="none" stroke={color} strokeWidth="3"
            strokeDasharray={`${pct} ${100 - pct}`} strokeLinecap="round" />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold" style={{ color }}>{pct}%</span>
        </div>
      </div>
      <span className="text-xs text-slate-400 mt-1">Mutation Score</span>
    </div>
  )
}

export default function MutationTester() {
  const [projects, setProjects]   = useState([])
  const [files, setFiles]         = useState([])
  const [functions, setFunctions] = useState([])
  const [sel, setSel]             = useState({ project: '', file: '', fn: '' })
  const [tests, setTests]         = useState(SAMPLE_TESTS)
  const [newTest, setNewTest]     = useState('')
  const [result, setResult]       = useState(null)
  const [loading, setLoading]     = useState(false)

  useEffect(() => {
    getProjects().then(r => setProjects(r.data)).catch(() => {})
  }, [])

  const onProject = (e) => {
    const p = projects.find(x => x.id === e.target.value)
    setSel({ project: e.target.value, file: '', fn: '' })
    setFiles(p?.files || [])
    setFunctions([])
    setResult(null)
  }

  const onFile = async (e) => {
    setSel(s => ({ ...s, file: e.target.value, fn: '' }))
    setResult(null)
    if (e.target.value && sel.project) {
      const r = await getFunctions(sel.project, e.target.value).catch(() => null)
      setFunctions(r?.data?.functions || [])
    }
  }

  const run = async () => {
    if (!sel.project || !sel.file || !sel.fn) return
    setLoading(true); setResult(null)
    try {
      const r = await analyzeMutation({ project: sel.project, filename: sel.file, function_name: sel.fn, tests })
      setResult(r.data)
    } catch (e) { setResult({ error: e.message }) }
    setLoading(false)
  }

  const addTest = () => {
    if (newTest.trim()) { setTests(t => [...t, newTest.trim()]); setNewTest('') }
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-bold text-white">☣ Mutation Tester</h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Validate test quality by injecting fake bugs into source code and measuring how many tests catch them
        </p>
      </div>

      {/* Setup */}
      <div className="card space-y-3">
        <h3 className="text-sm font-semibold text-slate-300">Select Target Function</h3>
        <div className="grid grid-cols-3 gap-3">
          <select value={sel.project} onChange={onProject} className="select">
            <option value="">Select Project...</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <select value={sel.file} onChange={onFile} className="select">
            <option value="">Select File...</option>
            {files.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
          <select value={sel.fn} onChange={e => setSel(s => ({ ...s, fn: e.target.value }))} className="select">
            <option value="">Select Function...</option>
            {functions.map(f => <option key={f.name} value={f.name}>{f.name}()</option>)}
          </select>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">

        {/* Tests */}
        <div className="card space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-300">Test Cases</h3>
            <span className="badge-blue">{tests.length} tests</span>
          </div>

          <div className="space-y-2 max-h-72 overflow-auto">
            {tests.map((t, i) => (
              <div key={i} className="bg-surface border border-border rounded-lg p-3 group relative">
                <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed">{t}</pre>
                <button onClick={() => setTests(ts => ts.filter((_, j) => j !== i))}
                  className="absolute top-2 right-2 text-slate-700 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity text-xs">
                  ✕
                </button>
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <input value={newTest} onChange={e => setNewTest(e.target.value)}
              placeholder="Paste a test to add..."
              className="input text-xs font-mono flex-1"
            />
            <button onClick={addTest} className="btn-secondary px-3">+ Add</button>
          </div>

          <button onClick={run} disabled={loading || !sel.fn} className="btn-primary w-full !bg-red-800 hover:!bg-red-700">
            {loading ? '⏳ Running Mutations...' : '☣ Run Mutation Testing'}
          </button>
        </div>

        {/* Results */}
        <div className="card space-y-4">
          <h3 className="text-sm font-semibold text-slate-300">Results</h3>

          {result && !result.error ? (
            <div className="space-y-4">
              <div className="flex items-center gap-6">
                <ScoreRing score={result.mutation_score} />
                <div className="space-y-2">
                  {[
                    { label: 'Total Mutations', value: result.total_mutations, c: 'text-slate-300' },
                    { label: 'Killed ✅',        value: result.killed,          c: 'text-green-400' },
                    { label: 'Survived ❌',      value: result.survived,        c: 'text-red-400' },
                  ].map(s => (
                    <div key={s.label} className="flex items-center gap-3">
                      <span className="text-xs text-slate-500 w-28">{s.label}</span>
                      <span className={`font-bold tabular-nums ${s.c}`}>{s.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2 max-h-64 overflow-auto">
                <div className="text-xs text-slate-500 uppercase tracking-wider">Mutations Detail</div>
                {result.mutations.map((m, i) => (
                  <div key={i} className={`bg-surface rounded-lg p-3 border text-xs space-y-1 ${
                    m.killed ? 'border-green-800/50' : 'border-red-800/50'
                  }`}>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-300">{m.mutation}</span>
                      <span className={m.killed ? 'badge-green' : 'badge-red'}>
                        {m.killed ? '✅ Killed' : '❌ Survived'}
                      </span>
                    </div>
                    <div className="font-mono text-red-400 truncate">- {m.original}</div>
                    <div className="font-mono text-green-400 truncate">+ {m.mutated}</div>
                    {m.caught_by.length > 0 && (
                      <div className="text-slate-500">Caught by: Tests {m.caught_by.map(t => t+1).join(', ')}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : result?.error ? (
            <div className="bg-red-900/20 border border-red-700 rounded-lg p-3 text-sm text-red-300">
              Error: {result.error}
            </div>
          ) : (
            <div className="text-center text-slate-600 py-16 text-sm">
              Configure the selector and click Run to see mutation results
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
