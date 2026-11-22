import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { getStats } from './api'

// Pages
import Dashboard     from './pages/Dashboard.jsx'
import ProjectBrowser from './pages/ProjectBrowser.jsx'
import FunctionRunner from './pages/FunctionRunner.jsx'
import Stage1        from './pages/Stage1.jsx'

const NAV = [
  { to: '/',          label: 'Dashboard' },
  { to: '/projects',  label: 'Projects' },
  { to: '/runner',    label: 'Run Functions' },
  { to: '/stage1',    label: 'Stage 1 · Test Generation' },
]

// Dark / light switch (remembered in this browser)
function ThemeToggle() {
  const [light, setLight] = useState(() => document.documentElement.classList.contains('light'))
  const toggle = () => {
    const next = !light
    document.documentElement.classList.toggle('light', next)
    try { localStorage.setItem('theme', next ? 'light' : 'dark') } catch {}
    setLight(next)
  }
  return (
    <button onClick={toggle} title={light ? 'Switch to dark mode' : 'Switch to light mode'}
      className="w-8 h-8 grid place-items-center rounded-lg border border-border text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors">
      {light ? (
        <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4"><path fillRule="evenodd" clipRule="evenodd" d="M7.455 2.004a.75.75 0 0 1 .26.77 7 7 0 0 0 9.958 7.967.75.75 0 0 1 1.067.853A8.5 8.5 0 1 1 6.647 1.921a.75.75 0 0 1 .808.083Z" /></svg>
      ) : (
        <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4"><path d="M10 14a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm0-12a.75.75 0 0 1 .75.75v1a.75.75 0 0 1-1.5 0v-1A.75.75 0 0 1 10 2Zm0 13.5a.75.75 0 0 1 .75.75v1a.75.75 0 0 1-1.5 0v-1a.75.75 0 0 1 .75-.75ZM2 10a.75.75 0 0 1 .75-.75h1a.75.75 0 0 1 0 1.5h-1A.75.75 0 0 1 2 10Zm13.5 0a.75.75 0 0 1 .75-.75h1a.75.75 0 0 1 0 1.5h-1a.75.75 0 0 1-.75-.75ZM4.34 4.34a.75.75 0 0 1 1.06 0l.7.7a.75.75 0 0 1-1.06 1.06l-.7-.7a.75.75 0 0 1 0-1.06Zm9.56 9.56a.75.75 0 0 1 1.06 0l.7.7a.75.75 0 1 1-1.06 1.06l-.7-.7a.75.75 0 0 1 0-1.06ZM4.34 15.66a.75.75 0 0 1 0-1.06l.7-.7a.75.75 0 1 1 1.06 1.06l-.7.7a.75.75 0 0 1-1.06 0Zm9.56-9.56a.75.75 0 0 1 0-1.06l.7-.7a.75.75 0 1 1 1.06 1.06l-.7.7a.75.75 0 0 1-1.06 0Z" /></svg>
      )}
    </button>
  )
}

function Layout({ stats, connected }) {
  return (
    <div className="min-h-screen bg-surface flex flex-col">

      {/* Top bar */}
      <header className="bg-card border-b border-border sticky top-0 z-50">
        <div className="max-w-screen-xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-7 h-7 rounded-md bg-primary grid place-items-center text-[13px] font-bold" style={{ color: '#fff' }}>T</div>
            <div className="min-w-0">
              <h1 className="text-sm font-semibold text-white leading-tight">AI Test Suite Auditor</h1>
              <p className="text-xs text-slate-500 truncate">
                {import.meta.env.VITE_AUTHOR} · {import.meta.env.VITE_UNIVERSITY}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {stats && (
              <div className="hidden md:flex gap-4 text-xs text-slate-500">
                <span><span className="text-slate-300 font-medium">{stats.total_projects}</span> projects</span>
                <span><span className="text-slate-300 font-medium">{stats.total_files}</span> files</span>
                <span><span className="text-slate-300 font-medium">{stats.total_functions.toLocaleString()}</span> functions</span>
              </div>
            )}
            <span className="flex items-center gap-1.5 text-xs text-slate-400" title="Backend connection">
              <span className={`w-2 h-2 rounded-full ${
                connected === null ? 'bg-slate-600' : connected ? 'bg-green-500' : 'bg-red-500'}`} />
              {connected === null ? 'Connecting' : connected ? 'Online' : 'Offline'}
            </span>
            <ThemeToggle />
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
                `px-3 py-2.5 text-sm border-b-2 whitespace-nowrap transition-colors ${
                  isActive
                    ? 'border-primary text-white font-medium'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
      </header>

      {/* Offline warning */}
      {connected === false && (
        <div className="bg-red-900 border-b border-red-800 px-4 py-2 text-sm text-red-300 text-center">
          The backend is not running. Start it with&nbsp;
          <code className="font-mono bg-card px-2 py-0.5 rounded text-xs">
            cd backend && uvicorn main:app --reload
          </code>
        </div>
      )}

      {/* Page content */}
      <main className="flex-1 max-w-screen-xl mx-auto w-full px-4 py-8">
        <Routes>
          <Route path="/"          element={<Dashboard stats={stats} />} />
          <Route path="/projects"  element={<ProjectBrowser />} />
          <Route path="/runner"    element={<FunctionRunner />} />
          <Route path="/stage1"    element={<Stage1 />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  const [stats, setStats]       = useState(null)
  const [connected, setConnected] = useState(null)   // null = still checking

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
