import React, { useState, useEffect } from 'react'
import { getProjects, getFunctions, getSource, getFnSource } from '../api'

export default function ProjectBrowser() {
  const [projects, setProjects]   = useState([])
  const [selProject, setSelProject] = useState(null)
  const [selFile, setSelFile]     = useState(null)
  const [selFn, setSelFn]         = useState(null)
  const [functions, setFunctions] = useState([])
  const [source, setSource]       = useState('')
  const [fnSource, setFnSource]   = useState('')
  const [loading, setLoading]     = useState(false)

  useEffect(() => {
    getProjects().then(r => setProjects(r.data)).catch(() => {})
  }, [])

  const pickProject = (p) => {
    setSelProject(p)
    setSelFile(null)
    setSelFn(null)
    setFunctions([])
    setSource('')
    setFnSource('')
  }

  const pickFile = async (file) => {
    setSelFile(file)
    setSelFn(null)
    setFnSource('')
    setLoading(true)
    try {
      const [fnRes, srcRes] = await Promise.all([
        getFunctions(selProject.id, file),
        getSource(selProject.id, file),
      ])
      setFunctions(fnRes.data.functions)
      setSource(srcRes.data.source)
    } catch { setSource('Error loading file') }
    setLoading(false)
  }

  const pickFn = async (fn) => {
    setSelFn(fn)
    try {
      const r = await getFnSource(selProject.id, selFile, fn.name)
      setFnSource(r.data.source)
    } catch { setFnSource('Error') }
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-lg font-bold text-white">📁 Project Browser</h2>
        <p className="text-xs text-slate-400 mt-0.5">Browse all 5 research projects, files and functions</p>
      </div>

      <div className="grid grid-cols-4 gap-3 h-[calc(100vh-220px)]">

        {/* Projects */}
        <div className="card p-0 overflow-auto flex flex-col">
          <div className="px-4 py-3 border-b border-border shrink-0">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Projects</span>
          </div>
          <div className="p-2 space-y-1 overflow-auto flex-1">
            {projects.map(p => (
              <button key={p.id} onClick={() => pickProject(p)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  selProject?.id === p.id
                    ? 'bg-primary/20 text-primary border border-primary/30'
                    : 'hover:bg-slate-800 text-slate-300 border border-transparent'
                }`}>
                <div className="font-medium leading-tight">{p.name}</div>
                <div className="text-xs text-slate-500 mt-0.5">{p.file_count} files</div>
              </button>
            ))}
          </div>
        </div>

        {/* Files */}
        <div className="card p-0 overflow-auto flex flex-col">
          <div className="px-4 py-3 border-b border-border shrink-0">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Files</span>
          </div>
          <div className="p-2 space-y-1 overflow-auto flex-1">
            {selProject?.files?.map(file => (
              <button key={file} onClick={() => pickFile(file)}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs font-mono transition-colors ${
                  selFile === file
                    ? 'bg-primary/20 text-primary border border-primary/30'
                    : 'hover:bg-slate-800 text-slate-300 border border-transparent'
                }`}>
                {file}
              </button>
            ))}
            {!selProject && (
              <div className="text-xs text-slate-600 text-center py-6">Select a project</div>
            )}
          </div>
        </div>

        {/* Functions */}
        <div className="card p-0 overflow-auto flex flex-col">
          <div className="px-4 py-3 border-b border-border shrink-0 flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Functions</span>
            {functions.length > 0 && (
              <span className="badge-blue">{functions.length}</span>
            )}
          </div>
          <div className="p-2 space-y-1 overflow-auto flex-1">
            {loading && <div className="text-xs text-slate-500 text-center py-6">Loading...</div>}
            {functions.map(fn => (
              <button key={fn.name} onClick={() => pickFn(fn)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  selFn?.name === fn.name
                    ? 'bg-primary/20 text-primary border border-primary/30'
                    : 'hover:bg-slate-800 text-slate-300 border border-transparent'
                }`}>
                <div className="text-xs font-mono font-medium">{fn.name}()</div>
                <div className="text-xs text-slate-600 truncate">{fn.args.join(', ')}</div>
              </button>
            ))}
            {!selFile && !loading && (
              <div className="text-xs text-slate-600 text-center py-6">Select a file</div>
            )}
          </div>
        </div>

        {/* Source viewer */}
        <div className="card p-0 overflow-auto flex flex-col">
          <div className="px-4 py-3 border-b border-border shrink-0 flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              {selFn ? selFn.name + '()' : 'Source'}
            </span>
            {selFn && (
              <span className="text-xs text-slate-600 font-mono">line {selFn.lineno}</span>
            )}
          </div>
          <div className="p-4 overflow-auto flex-1">
            {selFn && fnSource ? (
              <>
                {selFn.docstring && (
                  <p className="text-xs text-slate-500 italic mb-3 leading-relaxed">{selFn.docstring}</p>
                )}
                <pre className="text-xs font-mono text-green-300 leading-relaxed">{fnSource}</pre>
              </>
            ) : source ? (
              <pre className="text-xs font-mono text-slate-300 leading-relaxed">{source}</pre>
            ) : (
              <div className="text-xs text-slate-600 text-center py-12">
                Select project → file → function
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  )
}
