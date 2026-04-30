import { useState, useEffect } from 'react'
import { AlertTriangle, Users, ChevronRight } from 'lucide-react'
import { fetchRings } from '../api'



const STATUS_STYLE = {
  CONFIRMED:             { bg: 'rgba(255,68,68,0.12)',  text: '#FF4444', border: 'rgba(255,68,68,0.3)' },
  ACTIVE:                { bg: 'rgba(255,184,0,0.12)',  text: '#FFB800', border: 'rgba(255,184,0,0.3)' },
  UNDER_INVESTIGATION:   { bg: 'rgba(0,212,170,0.1)',   text: '#00D4AA', border: 'rgba(0,212,170,0.3)' },
  CLOSED:                { bg: 'rgba(255,255,255,0.05)', text: '#555',   border: 'rgba(255,255,255,0.1)' },
}

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100)
  const color = pct >= 90 ? '#FF4444' : pct >= 75 ? '#FFB800' : '#00D4AA'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 4 }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 4, boxShadow: `0 0 8px ${color}` }} />
      </div>
      <span style={{ fontSize: 12, color, fontFamily: 'Space Mono, monospace', minWidth: 36 }}>{pct}%</span>
    </div>
  )
}

export default function FraudRings() {
  const [rings, setRings]       = useState([])
  const [summary, setSummary]   = useState(null)
  const [expanded, setExpanded] = useState(null)
  const [liveData, setLiveData] = useState(false)

  useEffect(() => {
    fetchRings()
      .then(data => {
        if (data.rings && data.rings.length > 0) {
          setRings(data.rings.map(r => ({
            id: r.id, name: r.ring_name, status: r.status,
            members: r.member_count, value: r.total_claimed, prevented: r.total_prevented,
            confidence: r.confidence, algorithm: r.algorithm,
            detected: r.detected_at ? r.detected_at.slice(0,10) : '',
            accounts: r.members.map(m => m.account_id),
            leader: r.members.find(m => m.role === 'RING_LEADER')?.account_id || r.members[0]?.account_id,
            shared_signal: r.metadata ? Object.entries(r.metadata).map(([k,v])=>`${k}: ${v}`).join(', ') : '',
          })))
          setSummary(data)
          setLiveData(true)
        }
      })
      .catch(() => {})
  }, [])

  const total          = rings.reduce((a, r) => a + r.value, 0)
  const totalPrevented = rings.reduce((a, r) => a + r.prevented, 0)

  return (
    <div style={{ padding: 32, minHeight: '100vh' }}>
      <header style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, letterSpacing: -0.5, marginBottom: 4 }}>Fraud Ring Intelligence</h1>
        <p style={{ color: '#555', fontSize: 13 }}>Coordinated return fraud networks identified via graph community detection
          {liveData && <span style={{ marginLeft: 10, color: '#00D4AA', fontSize: 11 }}>● LIVE from MongoDB</span>}
        </p>
      </header>

      {/* Summary KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 32 }}>
        {[
          { label: 'ACTIVE RINGS',    value: rings.filter(r => r.status !== 'CLOSED').length, color: '#FF4444' },
          { label: 'TOTAL MEMBERS',   value: rings.reduce((a, r) => a + r.members, 0),         color: '#FFB800' },
          { label: 'CLAIMED VALUE',      value: `₹${(total/1000).toFixed(0)}K`,                         color: '#FF6644' },
          { label: 'VALUE PREVENTED',    value: `₹${(totalPrevented/1000).toFixed(0)}K`,                color: '#00FF88' },
        ].map(kpi => (
          <div key={kpi.label} style={{
            padding: '20px 24px', borderRadius: 14,
            background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)',
          }}>
            <div style={{ fontSize: 9, color: '#555', letterSpacing: 2, marginBottom: 8 }}>{kpi.label}</div>
            <div style={{ fontSize: 28, fontWeight: 700, fontFamily: 'Space Mono, monospace', color: kpi.color }}>
              {kpi.value}
            </div>
          </div>
        ))}
      </div>

      {/* Ring Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {rings.map(ring => {
          const isExpanded = expanded === ring.id
          const sc = STATUS_STYLE[ring.status] || STATUS_STYLE.CLOSED
          return (
            <div key={ring.id} style={{
              background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)',
              borderRadius: 16, overflow: 'hidden',
              transition: 'border-color 0.2s',
              ...(isExpanded ? { borderColor: 'rgba(0,212,170,0.2)' } : {}),
            }}>
              {/* Ring Header */}
              <div
                style={{
                  display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1.2fr 1.5fr 40px',
                  padding: '20px 24px', alignItems: 'center', cursor: 'pointer',
                  gap: 16,
                }}
                onClick={() => setExpanded(isExpanded ? null : ring.id)}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                    <AlertTriangle size={15} color={sc.text} />
                    <span style={{ fontWeight: 600, fontSize: 15, color: '#fff' }}>{ring.name}</span>
                  </div>
                  <div style={{ fontSize: 10, color: '#555', fontFamily: 'Space Mono, monospace' }}>
                    {ring.id} · {ring.algorithm}
                  </div>
                </div>
                <div>
                  <span style={{
                    padding: '4px 10px', borderRadius: 7, fontSize: 10, fontWeight: 600,
                    background: sc.bg, color: sc.text, border: `1px solid ${sc.border}`,
                    fontFamily: 'Space Mono, monospace',
                  }}>
                    {ring.status.replace('_', ' ')}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                  <Users size={14} color="#666" />
                  <span style={{ fontFamily: 'Space Mono, monospace', fontSize: 14, fontWeight: 700 }}>{ring.members}</span>
                </div>
                <div>
                  <div style={{ fontSize: 13, fontFamily: 'Space Mono, monospace', color: '#FF6644', fontWeight: 700 }}>
                    ₹{ring.value.toLocaleString('en-IN')}
                  </div>
                  <div style={{ fontSize: 10, color: '#555', marginTop: 2 }}>detected {ring.detected}</div>
                </div>
                <div><ConfidenceBar value={ring.confidence} /></div>
                <div style={{
                  transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s',
                }}>
                  <ChevronRight size={16} color="#555" />
                </div>
              </div>

              {/* Expanded Detail */}
              {isExpanded && (
                <div style={{
                  padding: '0 24px 24px',
                  borderTop: '1px solid rgba(255,255,255,0.05)',
                }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, paddingTop: 20 }}>
                    <div>
                      <div style={{ fontSize: 10, color: '#555', letterSpacing: 1.5, marginBottom: 10 }}>MEMBER ACCOUNTS</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {ring.accounts.map(acc => (
                          <span key={acc} style={{
                            padding: '4px 10px', borderRadius: 6, fontSize: 11, fontFamily: 'Space Mono, monospace',
                            background: acc === ring.leader ? 'rgba(255,68,68,0.15)' : 'rgba(255,255,255,0.05)',
                            color: acc === ring.leader ? '#FF4444' : '#aaa',
                            border: `1px solid ${acc === ring.leader ? 'rgba(255,68,68,0.3)' : 'rgba(255,255,255,0.08)'}`,
                          }}>
                            {acc === ring.leader ? '👑 ' : ''}{acc}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: 10, color: '#555', letterSpacing: 1.5, marginBottom: 10 }}>SHARED SIGNALS</div>
                      <p style={{ fontSize: 12, color: '#aaa', lineHeight: 1.6 }}>{ring.shared_signal}</p>
                      <div style={{ marginTop: 16 }}>
                        <div style={{ fontSize: 10, color: '#555', letterSpacing: 1.5, marginBottom: 8 }}>VALUE PREVENTED</div>
                        <span style={{ fontSize: 18, fontFamily: 'Space Mono, monospace', color: '#00FF88', fontWeight: 700 }}>
                          ₹{ring.prevented.toLocaleString('en-IN')}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
                    <button style={{
                      padding: '10px 20px', borderRadius: 10, fontSize: 12,
                      background: 'rgba(255,68,68,0.1)', border: '1px solid rgba(255,68,68,0.3)', color: '#FF4444',
                    }}>
                      🚫 Block All Members
                    </button>
                    <button style={{
                      padding: '10px 20px', borderRadius: 10, fontSize: 12,
                      background: 'rgba(0,212,170,0.1)', border: '1px solid rgba(0,212,170,0.3)', color: '#00D4AA',
                    }}>
                      📋 Export Report
                    </button>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
