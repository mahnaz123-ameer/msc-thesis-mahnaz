import React from 'react'

const STAGES = [
  { n: '01', title: 'AI Test Generation',      desc: 'GPT-4 / Copilot generates unit tests for your Python functions automatically.', icon: '🤖', color: 'text-blue-400',   border: 'border-blue-800/50' },
  { n: '02', title: 'AST Redundancy Detection', desc: 'Parse tests into AST trees, compare execution paths, remove semantic duplicates.', icon: '🌳', color: 'text-green-400',  border: 'border-green-800/50' },
  { n: '03', title: 'Mutation Validation',      desc: 'Inject fake bugs, check which surviving tests catch them, remove weak tests.', icon: '☣',  color: 'text-yellow-400', border: 'border-yellow-800/50' },
  { n: '04', title: 'Final Suite Selection',    desc: 'Output a smaller, stronger test suite with preserved fault-detection capability.', icon: '✅', color: 'text-purple-400', border: 'border-purple-800/50' },
]

const PAPERS = [
  { name: 'LTM 2024',      desc: 'IEEE — Test Suite Minimization using Language Models',      url: 'https://arxiv.org/pdf/2304.01397' },
  { name: 'TripRL 2024',   desc: 'arXiv — RL-based Similarity-Aware Test Suite Minimization', url: 'https://arxiv.org/pdf/2408.13517' },
  { name: 'Meta ACH 2025', desc: 'arXiv — Mutation-Guided LLM Test Generation at Meta',       url: 'https://arxiv.org/pdf/2501.12862' },
  { name: 'MutGen 2025',   desc: 'arXiv — Fault Detection in LLM-Based Test Generation',      url: 'https://arxiv.org/pdf/2506.02954' },
]

export default function Dashboard({ stats }) {
  return (
    <div className="space-y-6">

      {/* Hero */}
      <div className="bg-gradient-to-br from-indigo-950 to-slate-900 border border-indigo-800/40 rounded-2xl p-6">
        <div className="badge-blue inline-block mb-3">MSc Thesis — 2026/2027</div>
        <h2 className="text-2xl font-bold text-white mb-2 leading-snug">
          Semantic Redundancy Pruning &<br />Targeted Mutation Validation
        </h2>
        <p className="text-slate-300 text-sm max-w-2xl leading-relaxed">
          An automated framework that evaluates and optimises AI-generated unit test suites
          by combining AST-based semantic execution-path analysis with selective mutation testing —
          deployed as an inline CI/CD auditing tool.
        </p>
        <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
          <span>👩‍🎓 Mahnaz Ameer</span>
          <span>·</span>
          <span>🏛 University of Dhaka — CSE</span>
          <span>·</span>
          <span>🎯 Novel Research Contribution</span>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Projects',    value: stats.total_projects,  icon: '📁', c: 'text-blue-400' },
            { label: 'Python Files', value: stats.total_files,    icon: '📄', c: 'text-green-400' },
            { label: 'Functions',   value: stats.total_functions, icon: '⚡', c: 'text-yellow-400' },
            { label: 'Research Gap', value: 'Novel',              icon: '🎯', c: 'text-purple-400' },
          ].map((s, i) => (
            <div key={i} className="card text-center">
              <div className="text-2xl mb-1">{s.icon}</div>
              <div className={`text-3xl font-bold ${s.c}`}>{s.value}</div>
              <div className="text-xs text-slate-400 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Framework stages */}
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
          Research Framework
        </h3>
        <div className="grid sm:grid-cols-2 gap-3">
          {STAGES.map(s => (
            <div key={s.n} className={`card border ${s.border} flex gap-4`}>
              <div>
                <div className="text-2xl">{s.icon}</div>
              </div>
              <div>
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="text-xs font-mono text-slate-500">Stage {s.n}</span>
                  <span className={`text-sm font-semibold ${s.color}`}>{s.title}</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Projects table */}
      {stats && (
        <div>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
            Evaluation Projects
          </h3>
          <div className="card p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-slate-800/40">
                  <th className="px-4 py-3 text-left text-xs text-slate-500 font-medium">#</th>
                  <th className="px-4 py-3 text-left text-xs text-slate-500 font-medium">Project</th>
                  <th className="px-4 py-3 text-right text-xs text-slate-500 font-medium">Files</th>
                  <th className="px-4 py-3 text-right text-xs text-slate-500 font-medium">Functions</th>
                </tr>
              </thead>
              <tbody>
                {stats.projects.map((p, i) => (
                  <tr key={p.id} className="border-b border-border/40 hover:bg-slate-800/20 transition-colors">
                    <td className="px-4 py-3 text-xs font-mono text-slate-600">{String(i+1).padStart(2,'0')}</td>
                    <td className="px-4 py-3 font-medium text-slate-200">{p.name}</td>
                    <td className="px-4 py-3 text-right text-slate-400 tabular-nums">{p.files}</td>
                    <td className="px-4 py-3 text-right font-bold text-primary tabular-nums">{p.functions}</td>
                  </tr>
                ))}
                <tr className="bg-slate-800/30">
                  <td colSpan={2} className="px-4 py-3 font-bold text-white text-sm">Total</td>
                  <td className="px-4 py-3 text-right font-bold text-white tabular-nums">{stats.total_files}</td>
                  <td className="px-4 py-3 text-right font-bold text-primary tabular-nums">{stats.total_functions}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Related papers */}
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
          Related Papers
        </h3>
        <div className="grid sm:grid-cols-2 gap-3">
          {PAPERS.map(p => (
            <a key={p.name} href={p.url} target="_blank" rel="noreferrer"
               className="card hover:border-primary/50 transition-colors block">
              <div className="font-semibold text-sm text-primary mb-0.5">{p.name}</div>
              <div className="text-xs text-slate-400">{p.desc}</div>
              <div className="text-xs text-slate-600 mt-1 font-mono truncate">↗ {p.url}</div>
            </a>
          ))}
        </div>
      </div>

    </div>
  )
}
