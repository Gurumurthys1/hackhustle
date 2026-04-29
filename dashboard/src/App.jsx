import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'
import {
  LayoutDashboard, Layers, Users, TrendingUp, Database,
  ShieldCheck, Bell, User, LogOut, ChevronRight
} from 'lucide-react'
import Dashboard from './pages/Dashboard.jsx'
import ClaimsQueue from './pages/ClaimsQueue.jsx'
import FraudRings from './pages/FraudRings.jsx'
import ModelPerformance from './pages/ModelPerformance.jsx'
import AuditLog from './pages/AuditLog.jsx'

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Intelligence Center', path: '/' },
  { icon: Layers,          label: 'Claims Queue',        path: '/claims' },
  { icon: Users,           label: 'Fraud Rings',         path: '/rings' },
  { icon: TrendingUp,      label: 'Model Performance',   path: '/performance' },
  { icon: Database,        label: 'Audit Log',           path: '/audit' },
]

function Sidebar() {
  const { pathname } = useLocation()

  return (
    <aside style={{
      width: 260, minHeight: '100vh',
      borderRight: '1px solid rgba(255,255,255,0.06)',
      padding: '24px 14px',
      display: 'flex', flexDirection: 'column', gap: 32,
      background: 'rgba(0,0,0,0.3)',
      backdropFilter: 'blur(20px)',
      position: 'sticky', top: 0, height: '100vh',
      flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '0 10px' }}>
        <div style={{
          width: 34, height: 34,
          background: 'linear-gradient(135deg, #00FF88 0%, #00D4AA 100%)',
          borderRadius: 9, display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 20px rgba(0,255,136,0.3)',
        }}>
          <ShieldCheck size={20} color="#07090F" />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 15, letterSpacing: -0.3 }}>
            TRI<span style={{ color: '#00FF88' }}>ÑETRA</span>
          </div>
          <div style={{ fontSize: 10, color: '#555', letterSpacing: 2 }}>FRAUD AI v3.0</div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV_ITEMS.map(({ icon: Icon, label, path }) => {
          const active = path === '/' ? pathname === '/' : pathname.startsWith(path)
          return (
            <NavLink key={path} to={path} style={{ textDecoration: 'none' }}>
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '11px 14px', borderRadius: 10, cursor: 'pointer',
                background: active ? 'rgba(0,255,136,0.08)' : 'transparent',
                color: active ? '#00FF88' : '#666',
                transition: 'all 0.15s',
                border: `1px solid ${active ? 'rgba(0,255,136,0.15)' : 'transparent'}`,
              }}
              onMouseEnter={e => { if (!active) e.currentTarget.style.color = '#aaa' }}
              onMouseLeave={e => { if (!active) e.currentTarget.style.color = '#666' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <Icon size={17} />
                  <span style={{ fontSize: 13, fontWeight: active ? 600 : 400 }}>{label}</span>
                </div>
                {active && <ChevronRight size={14} />}
              </div>
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {/* System status */}
        <div style={{
          padding: '12px 14px',
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(255,255,255,0.05)',
          borderRadius: 10,
        }}>
          <div style={{ fontSize: 10, color: '#444', letterSpacing: 1.5, marginBottom: 8 }}>
            SYSTEM STATUS
          </div>
          {[
            { label: 'Fraud Engine', ok: true },
            { label: 'Graph Service', ok: true },
            { label: 'Kafka Queue', ok: true },
          ].map(({ label, ok }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
              <div style={{
                width: 6, height: 6, borderRadius: '50%',
                background: ok ? '#00FF88' : '#FF4444',
                boxShadow: ok ? '0 0 6px #00FF88' : '0 0 6px #FF4444',
              }} />
              <span style={{ fontSize: 11, color: '#777' }}>{label}</span>
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '0 14px' }}>
          <div style={{
            width: 32, height: 32, borderRadius: '50%',
            background: 'linear-gradient(135deg, #1e3a5f, #0d2040)',
            border: '1px solid rgba(255,255,255,0.1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <User size={15} color="#888" />
          </div>
          <div>
            <div style={{ fontSize: 12, color: '#ccc' }}>Admin</div>
            <div style={{ fontSize: 10, color: '#444' }}>Senior Reviewer</div>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', minHeight: '100vh', background: '#07090F' }}>
        <Sidebar />
        <main style={{ flex: 1, overflowY: 'auto', minWidth: 0 }}>
          <Routes>
            <Route path="/"             element={<Dashboard />} />
            <Route path="/claims"       element={<ClaimsQueue />} />
            <Route path="/rings"        element={<FraudRings />} />
            <Route path="/performance"  element={<ModelPerformance />} />
            <Route path="/audit"        element={<AuditLog />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
