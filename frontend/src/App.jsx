import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { getStats } from './api'

// Pages
import Dashboard     from './pages/Dashboard.jsx'
import ProjectBrowser from './pages/ProjectBrowser.jsx'
import FunctionRunner from './pages/FunctionRunner.jsx'
import ASTAnalyzer   from './pages/ASTAnalyzer.jsx'
import MutationTester from './pages/MutationTester.jsx'

const NAV = [
  { to: '/',          label: 'Dashboard',       icon: '📊' },
  { to: '/projects',  label: 'Projects',         icon: '📁' },
  { to: '/runner',    label: 'Run Functions',    icon: '▶' },
  { to: '/ast',       label: 'AST Analyzer',     icon: '🌳' },
  { to: '/mutation',  label: 'Mutation Tester',  icon: '☣' },
]

function Layout({ stats, connected }) {
  return (
    <div className="min-h-screen bg-surface flex flex-col">

      {/* Top bar */}
      <header className="bg-card border-b border-border sticky top-0 z-50">
        <div className="max-w-screen-xl mx-auto px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-base font-bold text-white leading-tight">
              🔬 AI Test Suite Auditor
            </h1>
            <p className="text-xs text-slate-500">
              {import.meta.env.VITE_AUTHOR} · {import.meta.env.VITE_UNIVERSITY}
            </p>
          </div>

          <div className="flex items-center gap-4">
            {stats && (
              <div className="hidden md:flex gap-4 text-xs text-slate-400">
                <span><b className="text-primary">{stats.total_projects}</b> Projects</span>
                <span><b className="text-primary">{stats.total_files}</b> Files</span>
                <span><b className="text-primary">{stats.total_functions}</b> Functions</span>
              </div>
            )}
            <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
              connected ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'
            }`}>
              {connected ? '● Online' : '● Offline'}
            </span>
          </div>
        </div>

        {/* Nav */}
        <nav className="max-w-screen-xl mx-auto px-4 flex gap-0 overflow-x-auto">
          {NAV.map(n => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                  isActive
                    ? 'border-primary text-primary'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`
              }
            >
              <span>{n.icon}</span>
              <span>{n.label}</span>
            </NavLink>
          ))}
        </nav>
      </header>

      {/* Offline warning */}
      {!connected && (
        <div className="bg-red-900/30 border-b border-red-800 px-4 py-2 text-sm text-red-300 text-center">
          ⚠ Backend offline — run:&nbsp;
          <code className="font-mono bg-red-900/50 px-2 py-0.5 rounded text-xs">
            cd backend && uvicorn main:app --reload
          </code>
        </div>
      )}

      {/* Page content */}
      <main className="flex-1 max-w-screen-xl mx-auto w-full px-4 py-6">
        <Routes>
          <Route path="/"          element={<Dashboard stats={stats} />} />
          <Route path="/projects"  element={<ProjectBrowser />} />
          <Route path="/runner"    element={<FunctionRunner />} />
          <Route path="/ast"       element={<ASTAnalyzer />} />
          <Route path="/mutation"  element={<MutationTester />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  const [stats, setStats]       = useState(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    getStats()
      .then(r => { setStats(r.data); setConnected(true) })
      .catch(() => setConnected(false))
  }, [])

  return (
    <BrowserRouter>
      <Layout stats={stats} connected={connected} />
    </BrowserRouter>
  )
}
