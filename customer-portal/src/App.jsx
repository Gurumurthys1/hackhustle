import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import { ShieldCheck } from 'lucide-react'
import Orders from './pages/Orders.jsx'
import SubmitReturn from './pages/SubmitReturn.jsx'
import TrackReturn from './pages/TrackReturn.jsx'

function Header() {
  const { pathname } = useLocation()
  return (
    <header style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 32px', height: 64,
      borderBottom: '1px solid rgba(255,255,255,0.06)',
      background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(20px)',
      position: 'sticky', top: 0, zIndex: 100,
    }}>
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
        <div style={{
          width: 30, height: 30,
          background: 'linear-gradient(135deg, #00FF88 0%, #00D4AA 100%)',
          borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 16px rgba(0,255,136,0.3)',
        }}>
          <ShieldCheck size={17} color="#07090F" />
        </div>
        <span style={{ fontWeight: 700, fontSize: 15, color: '#fff' }}>
          TRI<span style={{ color: '#00FF88' }}>ÑETRA</span>
        </span>
      </Link>
      <nav style={{ display: 'flex', gap: 8 }}>
        <Link to="/" style={{
          padding: '8px 18px', borderRadius: 10, fontSize: 13, fontWeight: 500,
          background: pathname === '/' ? 'rgba(0,255,136,0.1)' : 'transparent',
          border: `1px solid ${pathname === '/' ? 'rgba(0,255,136,0.3)' : 'transparent'}`,
          color: pathname === '/' ? '#00FF88' : '#888',
        }}>
          My Orders
        </Link>
        <Link to="/return" style={{
          padding: '8px 18px', borderRadius: 10, fontSize: 13, fontWeight: 500,
          background: pathname === '/return' ? 'rgba(0,212,170,0.1)' : 'transparent',
          border: `1px solid ${pathname === '/return' ? 'rgba(0,212,170,0.3)' : 'transparent'}`,
          color: pathname === '/return' ? '#00D4AA' : '#888',
        }}>
          Start Return
        </Link>
        <Link to="/track" style={{
          padding: '8px 18px', borderRadius: 10, fontSize: 13, fontWeight: 500,
          background: pathname === '/track' ? 'rgba(0,212,170,0.1)' : 'transparent',
          border: `1px solid ${pathname === '/track' ? 'rgba(0,212,170,0.3)' : 'transparent'}`,
          color: pathname === '/track' ? '#00D4AA' : '#888',
        }}>
          Track Return
        </Link>
      </nav>
    </header>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', background: '#07090F', display: 'flex', flexDirection: 'column' }}>
        <Header />
        <main style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'flex-start', paddingTop: 48 }}>
          <Routes>
            <Route path="/"      element={<Orders />} />
            <Route path="/return" element={<SubmitReturn />} />
            <Route path="/track" element={<TrackReturn />} />
          </Routes>
        </main>
        <footer style={{ textAlign: 'center', padding: '24px', borderTop: '1px solid rgba(255,255,255,0.05)', fontSize: 11, color: '#333' }}>
          Secured by TriNetra AI · DPDPA 2023 Compliant ·{' '}
          <a href="/privacy" style={{ color: '#444' }}>Privacy Policy</a>
        </footer>
      </div>
    </BrowserRouter>
  )
}
