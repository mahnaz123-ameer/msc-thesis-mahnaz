import React from 'react'

const STAGES = [
  { n: '1', title: 'AI Test Generation',       desc: 'ChatGPT, Claude and Gemini generate unit tests for your Python functions with the same standard prompt.' },
  { n: '2', title: 'AST Redundancy Detection', desc: 'Parse tests into AST trees, compare execution paths, remove semantic duplicates.' },
  { n: '3', title: 'Mutation Validation',      desc: 'Inject fake bugs, check which surviving tests catch them, remove weak tests.' },
  { n: '4', title: 'Final Suite Selection',    desc: 'Output a smaller, stronger test suite with preserved fault-detection capability.' },
]

const PAPERS = [
  { name: 'LTM 2024',      desc: 'IEEE — Test Suite Minimization using Language Models',      url: 'https://arxiv.org/pdf/2304.01397' },
  { name: 'TripRL 2024',   desc: 'arXiv — RL-based Similarity-Aware Test Suite Minimization', url: 'https://arxiv.org/pdf/2408.13517' },
  { name: 'Meta ACH 2025', desc: 'arXiv — Mutation-Guided LLM Test Generation at Meta',       url: 'https://arxiv.org/pdf/2501.12862' },
  { name: 'MutGen 2025',   desc: 'arXiv — Fault Detection in LLM-Based Test Generation',      url: 'https://arxiv.org/pdf/2506.02954' },
]

const SectionTitle = ({ children }) => (
  <h3 className="text-sm font-semibold text-white mb-3">{children}</h3>
)

export default function Dashboard({ stats }) {
  return (
    <div className="space-y-10">

      {/* Intro */}
      <div className="max-w-3xl">
        <div className="text-xs font-medium text-primary mb-2">MSc Thesis · 2026/2027</div>
        <h2 className="text-2xl font-semibold text-white leading-snug">
          Semantic Redundancy Pruning & Targeted Mutation Validation
        </h2>
        <p className="text-slate-400 text-sm mt-3 leading-relaxed">
          An automated framework that evaluates and optimises AI-generated unit test suites
          by combining AST-based semantic execution-path analysis with selective mutation testing —
          deployed as an inline CI/CD auditing tool.
        </p>
        <p className="mt-3 text-xs text-slate-500">
          Mahnaz Ameer · University of Dhaka — CSE
        </p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-3 max-w-2xl">
          {[
            { label: 'Projects',     value: stats.total_projects },
            { label: 'Python files', value: stats.total_files },
            { label: 'Functions',    value: stats.total_functions.toLocaleString() },
          ].map(s => (
            <div key={s.label} className="card">
              <div className="text-2xl font-semibold text-white tabular-nums">{s.value}</div>
              <div className="text-xs text-slate-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Framework stages */}
      <div>
        <SectionTitle>Research framework</SectionTitle>
        <div className="grid sm:grid-cols-2 gap-3">
          {STAGES.map(s => (
            <div key={s.n} className="card flex gap-4">
              <div className="w-7 h-7 shrink-0 rounded-full border border-border grid place-items-center text-xs font-semibold text-slate-300">
                {s.n}
              </div>
              <div>
                <div className="text-sm font-medium text-white mb-1">{s.title}</div>
                <p className="text-xs text-slate-400 leading-relaxed">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Projects table */}
      {stats && (
        <div>
          <SectionTitle>Evaluation projects</SectionTitle>
          <div className="card p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="px-4 py-3 text-left text-xs text-slate-500 font-medium">Project</th>
                  <th className="px-4 py-3 text-left text-xs text-slate-500 font-medium">Type</th>
                  <th className="px-4 py-3 text-right text-xs text-slate-500 font-medium">Files</th>
                  <th className="px-4 py-3 text-right text-xs text-slate-500 font-medium">Functions</th>
                </tr>
              </thead>
              <tbody>
                {stats.projects.map(p => (
                  <tr key={p.id} className="border-b border-border last:border-0 hover:bg-slate-800 transition-colors">
                    <td className="px-4 py-2.5 text-slate-200">{p.name}</td>
                    <td className="px-4 py-2.5 text-xs text-slate-500">{p.kind === 'library' ? 'Open-source library' : 'Domain project'}</td>
                    <td className="px-4 py-2.5 text-right text-slate-400 tabular-nums">{p.files}</td>
                    <td className="px-4 py-2.5 text-right text-slate-200 tabular-nums">{p.functions.toLocaleString()}</td>
                  </tr>
                ))}
                <tr className="border-t border-border">
                  <td colSpan={2} className="px-4 py-3 font-medium text-white">Total</td>
                  <td className="px-4 py-3 text-right font-medium text-white tabular-nums">{stats.total_files}</td>
                  <td className="px-4 py-3 text-right font-medium text-white tabular-nums">{stats.total_functions.toLocaleString()}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Related papers */}
      <div>
        <SectionTitle>Related papers</SectionTitle>
        <div className="grid sm:grid-cols-2 gap-3">
          {PAPERS.map(p => (
            <a key={p.name} href={p.url} target="_blank" rel="noreferrer"
               className="card hover:border-primary transition-colors block">
              <div className="text-sm font-medium text-white">{p.name}</div>
              <div className="text-xs text-slate-400 mt-0.5">{p.desc}</div>
              <div className="text-xs text-slate-500 mt-2 font-mono truncate">{p.url}</div>
            </a>
          ))}
        </div>
      </div>

    </div>
  )
}
