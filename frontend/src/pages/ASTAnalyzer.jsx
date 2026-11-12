import React, { useState, useEffect } from 'react'
import { getProjects, getFunctions, getFnAST, analyzeAST } from '../api'

const NODE_COLORS = {
  FunctionDef: 'bg-blue-900/60 text-blue-300 border-blue-700',
  If:          'bg-yellow-900/60 text-yellow-300 border-yellow-700',
  Return:      'bg-green-900/60 text-green-300 border-green-700',
  Call:        'bg-purple-900/60 text-purple-300 border-purple-700',
  Assign:      'bg-orange-900/60 text-orange-300 border-orange-700',
  Compare:     'bg-pink-900/60 text-pink-300 border-pink-700',
  Raise:       'bg-red-900/60 text-red-300 border-red-700',
  For:         'bg-cyan-900/60 text-cyan-300 border-cyan-700',
  Assert:      'bg-teal-900/60 text-teal-300 border-teal-700',
  default:     'bg-slate-800 text-slate-300 border-slate-600',
}

function ASTNode({ node, depth = 0 }) {
  const [open, setOpen] = useState(depth < 2)
  if (!node) return null
  const cls = NODE_COLORS[node.type] || NODE_COLORS.default
  const hasKids = node.children?.length > 0

  return (
    <li className="my-0.5">
      <div className="flex items-center gap-1">
        <button onClick={() => setOpen(o => !o)}
          className={`w-4 text-xs text-slate-600 hover:text-slate-300 shrink-0 ${!hasKids && 'invisible'}`}>
          {open ? '▼' : '▶'}
        </button>
        <span className={`ast-node border ${cls}`}>{node.name}</span>
      </div>
      {hasKids && open && (
        <ul className="pl-5 border-l border-slate-700/40 ml-2 mt-0.5">
          {node.children.map((c, i) => <ASTNode key={i} node={c} depth={depth + 1} />)}
        </ul>
      )}
    </li>
  )
}

const SAMPLE = `def test_add_positive():
    result = add(2, 3)
    assert result == 5

def test_addition_works():
    x = add(2, 3)
    assert x == 5

def test_add_numbers():
    output = add(2, 3)
    assert output == 5

def test_add_negative():
    result = add(-1, -2)
    assert result == -3

def test_add_zero():
    result = add(0, 5)
    assert result == 5`

export default function ASTAnalyzer() {
  const [projects, setProjects] = useState([])
  const [files, setFiles]       = useState([])
  const [functions, setFunctions] = useState([])
  const [sel, setSel]           = useState({ project: '', file: '', fn: '' })
  const [astData, setAstData]   = useState(null)
  const [astLoading, setAstLoading] = useState(false)

  const [testCode, setTestCode]     = useState(SAMPLE)
  const [analysis, setAnalysis]     = useState(null)
  const [analyzing, setAnalyzing]   = useState(false)

  useEffect(() => {
    getProjects().then(r => setProjects(r.data)).catch(() => {})
  }, [])

  const onProject = (e) => {
    const p = projects.find(x => x.id === e.target.value)
    setSel({ project: e.target.value, file: '', fn: '' })
    setFiles(p?.files || [])
    setFunctions([])
    setAstData(null)
  }

  const onFile = async (e) => {
    setSel(s => ({ ...s, file: e.target.value, fn: '' }))
    setAstData(null)
    if (e.target.value && sel.project) {
      const r = await getFunctions(sel.project, e.target.value).catch(() => null)
      setFunctions(r?.data?.functions || [])
    }
  }

  const loadAST = async (fnName) => {
    setSel(s => ({ ...s, fn: fnName }))
    setAstLoading(true)
    try {
      const r = await getFnAST(sel.project, sel.file, fnName)
      setAstData(r.data)
    } catch { setAstData(null) }
    setAstLoading(false)
  }

  const runAnalysis = async () => {
    setAnalyzing(true)
    const tests = testCode.split(/\n(?=def )/).map(t => t.trim()).filter(Boolean)
    try {
      const r = await analyzeAST(tests)
      setAnalysis(r.data)
    } catch (e) { setAnalysis({ error: e.message }) }
    setAnalyzing(false)
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-bold text-white">🌳 AST Analyzer</h2>
        <p className="text-xs text-slate-400 mt-0.5">View Abstract Syntax Trees and detect semantically redundant tests</p>
      </div>

      {/* Function AST viewer */}
      <div className="card space-y-4">
        <h3 className="text-sm font-semibold text-slate-300">Function AST Tree</h3>
        <div className="grid grid-cols-3 gap-3">
          <select value={sel.project} onChange={onProject} className="select">
            <option value="">Select Project...</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <select value={sel.file} onChange={onFile} className="select">
            <option value="">Select File...</option>
            {files.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
          <select value={sel.fn} onChange={e => loadAST(e.target.value)} className="select">
            <option value="">Select Function...</option>
            {functions.map(f => <option key={f.name} value={f.name}>{f.name}()</option>)}
          </select>
        </div>

        {astLoading && <div className="text-center text-slate-500 py-6 text-sm">Loading AST...</div>}

        {astData && (
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-surface rounded-xl p-4 overflow-auto max-h-96 border border-border">
              <div className="text-xs text-slate-400 mb-3 font-mono">{astData.function}() — AST Tree</div>
              <div className="ast-tree">
                <ul><ASTNode node={astData.simplified} depth={0} /></ul>
              </div>
            </div>
            <div className="bg-surface rounded-xl p-4 border border-border">
              <div className="text-xs text-slate-400 mb-3">Node Types</div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(NODE_COLORS).filter(([k]) => k !== 'default').map(([type, cls]) => (
                  <span key={type} className={`ast-node border ${cls}`}>{type}</span>
                ))}
              </div>
              <div className="mt-4 text-xs text-slate-500 leading-relaxed">
                The AST tree shows the logical structure of the function. Each node represents a code construct.
                Two tests with identical trees are semantically equivalent — they test the same logic even with different variable names.
              </div>
            </div>
          </div>
        )}

        {!astData && !astLoading && (
          <div className="text-center text-slate-600 py-6 text-sm">Select a project → file → function to view its AST</div>
        )}
      </div>

      {/* Redundancy analysis */}
      <div className="card space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-300">🔍 AI-Generated Test Redundancy Analysis</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Paste AI-generated tests below. The analyzer compares AST execution paths to detect semantic duplicates.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-400">AI-Generated Tests (paste here)</label>
            <textarea
              value={testCode}
              onChange={e => setTestCode(e.target.value)}
              rows={14}
              className="input font-mono text-xs resize-none"
            />
            <button onClick={runAnalysis} disabled={analyzing} className="btn-primary w-full">
              {analyzing ? '⏳ Analyzing...' : '🔍 Detect Redundant Tests'}
            </button>
          </div>

          <div>
            {analysis && !analysis.error ? (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { label: 'Total Tests',  value: analysis.total,      c: 'text-slate-200' },
                    { label: 'Unique Tests', value: analysis.unique,     c: 'text-green-400' },
                    { label: 'Duplicates',   value: analysis.duplicates, c: 'text-red-400' },
                    { label: 'Reduction',    value: `${analysis.reduction_percent}%`, c: 'text-primary' },
                  ].map(s => (
                    <div key={s.label} className="bg-surface border border-border rounded-xl p-3 text-center">
                      <div className={`text-2xl font-bold ${s.c}`}>{s.value}</div>
                      <div className="text-xs text-slate-500 mt-0.5">{s.label}</div>
                    </div>
                  ))}
                </div>
                <div className="space-y-1.5 max-h-56 overflow-auto">
                  {analysis.results.map((r, i) => (
                    <div key={i} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs border ${
                      r.status === 'unique'
                        ? 'bg-green-900/20 border-green-800/50 text-green-300'
                        : 'bg-red-900/20 border-red-800/50 text-red-300'
                    }`}>
                      <span>{r.status === 'unique' ? '✅' : '❌'}</span>
                      <span className="font-mono flex-1">Test {i + 1}</span>
                      <span className="font-semibold capitalize">{r.status}</span>
                      {r.status === 'duplicate' && r.duplicate_of !== null && (
                        <span className="text-slate-500">≡ Test {r.duplicate_of + 1}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center text-slate-600 py-16 text-sm">
                Results appear here after analysis
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
