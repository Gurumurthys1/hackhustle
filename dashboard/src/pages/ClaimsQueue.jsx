import { useState, useCallback } from 'react'
import { Filter, Search, Eye, ChevronDown, Clock, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'

const TIERS = ['ALL', 'TRUSTED', 'CAUTION', 'ELEVATED_RISK', 'HIGH_RISK']
const TIER_COLORS = {
  TRUSTED:       { bg: 'rgba(0,255,136,0.1)',  text: '#00FF88', border: 'rgba(0,255,136,0.25)' },
  CAUTION:       { bg: 'rgba(255,184,0,0.1)',  text: '#FFB800', border: 'rgba(255,184,0,0.25)' },
  ELEVATED_RISK: { bg: 'rgba(255,102,68,0.1)', text: '#FF6644', border: 'rgba(255,102,68,0.25)' },
  HIGH_RISK:     { bg: 'rgba(255,68,68,0.1)',  text: '#FF4444', border: 'rgba(255,68,68,0.25)' },
}

const MOCK_CLAIMS = [
  { id: 'CLM-2024-0041', account: 'CUST-RING-003', type: 'INR',          tier: 'HIGH_RISK',     score: 92, amount: 4599, time: '2 min ago',  status: 'UNDER_REVIEW' },
  { id: 'CLM-2024-0040', account: 'CUST-RING-004', type: 'DAMAGE',       tier: 'HIGH_RISK',     score: 88, amount: 2399, time: '5 min ago',  status: 'UNDER_REVIEW' },
  { id: 'CLM-2024-0039', account: 'CUST-007',      type: 'WRONG_ITEM',   tier: 'ELEVATED_RISK', score: 71, amount: 1299, time: '12 min ago', status: 'UNDER_REVIEW' },
  { id: 'CLM-2024-0038', account: 'CUST-012',      type: 'QUALITY_ISSUE',tier: 'CAUTION',       score: 42, amount: 899,  time: '18 min ago', status: 'SCORED' },
  { id: 'CLM-2024-0037', account: 'CUST-INNOCENT-001', type: 'DAMAGE',   tier: 'TRUSTED',       score: 8,  amount: 3499, time: '22 min ago', status: 'APPROVED' },
  { id: 'CLM-2024-0036', account: 'CUST-089',      type: 'INR',          tier: 'TRUSTED',       score: 14, amount: 799,  time: '28 min ago', status: 'APPROVED' },
  { id: 'CLM-2024-0035', account: 'CUST-FRAUDSTER-002', type: 'DAMAGE',  tier: 'ELEVATED_RISK', score: 68, amount: 5999, time: '35 min ago', status: 'UNDER_REVIEW' },
  { id: 'CLM-2024-0034', account: 'CUST-102',      type: 'CHANGE_OF_MIND', tier: 'TRUSTED',    score: 5,  amount: 1099, time: '44 min ago', status: 'APPROVED' },
]

function ScoreBar({ score, tier }) {
  const color = TIER_COLORS[tier]?.text || '#00FF88'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div style={{
        width: 80, height: 5, background: 'rgba(255,255,255,0.06)',
        borderRadius: 4, overflow: 'hidden',
      }}>
        <div style={{
          width: `${score}%`, height: '100%', background: color,
          borderRadius: 4,
          boxShadow: score >= 80 ? `0 0 8px ${color}` : 'none',
          transition: 'width 0.6s ease',
        }} />
      </div>
      <span style={{ fontFamily: 'Space Mono, monospace', fontSize: 13, color, fontWeight: 700, minWidth: 24 }}>
        {score}
      </span>
    </div>
  )
}

export default function ClaimsQueue() {
  const [filter, setFilter] = useState('ALL')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState(null)

  const filtered = MOCK_CLAIMS.filter(c =>
    (filter === 'ALL' || c.tier === filter) &&
    (c.id.toLowerCase().includes(search.toLowerCase()) || c.account.toLowerCase().includes(search.toLowerCase()))
  )

  const counts = TIERS.reduce((acc, t) => {
    acc[t] = t === 'ALL' ? MOCK_CLAIMS.length : MOCK_CLAIMS.filter(c => c.tier === t).length
    return acc
  }, {})

  return (
    <div style={{ padding: 32, minHeight: '100vh' }}>
      <header style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, letterSpacing: -0.5, marginBottom: 4 }}>Claims Queue</h1>
        <p style={{ color: '#555', fontSize: 13 }}>
          {MOCK_CLAIMS.filter(c => c.status === 'UNDER_REVIEW').length} claims awaiting human review
        </p>
      </header>

      {/* Tier filter tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {TIERS.map(tier => {
          const active = filter === tier
          const color = tier === 'ALL' ? '#00D4AA' : TIER_COLORS[tier]?.text
          return (
            <button key={tier} onClick={() => setFilter(tier)} style={{
              padding: '8px 16px', borderRadius: 10,
              background: active ? `${color}18` : 'rgba(255,255,255,0.03)',
              border: `1px solid ${active ? color : 'rgba(255,255,255,0.07)'}`,
              color: active ? color : '#666', fontSize: 12, fontWeight: active ? 600 : 400,
            }}>
              {tier.replace('_', ' ')}
              <span style={{
                marginLeft: 6, padding: '2px 7px', borderRadius: 20,
                background: active ? `${color}25` : 'rgba(255,255,255,0.05)',
                fontSize: 10,
              }}>
                {counts[tier]}
              </span>
            </button>
          )
        })}

        {/* Search */}
        <div style={{ marginLeft: 'auto', position: 'relative' }}>
          <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#555' }} />
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search by ID or account..."
            style={{ paddingLeft: 36, paddingRight: 14, paddingTop: 9, paddingBottom: 9, fontSize: 12, width: 230, borderRadius: 10 }}
          />
        </div>
      </div>

      {/* Claims Table */}
      <div style={{
        background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 16, overflow: 'hidden',
      }}>
        {/* Table Header */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1.2fr 1fr 0.8fr 0.9fr 1.1fr 1fr 0.7fr',
          padding: '14px 20px', borderBottom: '1px solid rgba(255,255,255,0.05)',
          fontSize: 10, color: '#555', letterSpacing: 1.5,
        }}>
          {['CLAIM ID', 'ACCOUNT', 'TYPE', 'RISK TIER', 'SCORE', 'AMOUNT', 'ACTIONS'].map(h => (
            <div key={h}>{h}</div>
          ))}
        </div>

        {/* Rows */}
        {filtered.map(claim => {
          const tc = TIER_COLORS[claim.tier] || TIER_COLORS.TRUSTED
          const isSelected = selected === claim.id
          return (
            <div
              key={claim.id}
              style={{
                display: 'grid', gridTemplateColumns: '1.2fr 1fr 0.8fr 0.9fr 1.1fr 1fr 0.7fr',
                padding: '15px 20px', alignItems: 'center',
                borderBottom: '1px solid rgba(255,255,255,0.04)',
                background: isSelected ? 'rgba(0,212,170,0.04)' : 'transparent',
                cursor: 'pointer', transition: 'background 0.15s',
              }}
              onClick={() => setSelected(isSelected ? null : claim.id)}
              onMouseEnter={e => { if (!isSelected) e.currentTarget.style.background = 'rgba(255,255,255,0.02)' }}
              onMouseLeave={e => { if (!isSelected) e.currentTarget.style.background = 'transparent' }}
            >
              <div>
                <div style={{ fontFamily: 'Space Mono, monospace', fontSize: 12, color: '#00D4AA' }}>{claim.id}</div>
                <div style={{ fontSize: 10, color: '#555', marginTop: 2 }}>{claim.time}</div>
              </div>
              <div style={{ fontSize: 12, color: '#aaa' }}>{claim.account}</div>
              <div>
                <span style={{
                  padding: '3px 9px', borderRadius: 6,
                  background: 'rgba(255,255,255,0.05)', fontSize: 11, color: '#888',
                }}>
                  {claim.type}
                </span>
              </div>
              <div>
                <span style={{
                  padding: '4px 10px', borderRadius: 7,
                  background: tc.bg, color: tc.text, border: `1px solid ${tc.border}`,
                  fontSize: 10, fontWeight: 600, letterSpacing: 0.5,
                  fontFamily: 'Space Mono, monospace',
                }}>
                  {claim.tier.replace('_', ' ')}
                </span>
              </div>
              <div><ScoreBar score={claim.score} tier={claim.tier} /></div>
              <div style={{ fontFamily: 'Space Mono, monospace', fontSize: 13, color: '#ccc' }}>
                ₹{claim.amount.toLocaleString('en-IN')}
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                {claim.status === 'UNDER_REVIEW' && (
                  <>
                    <button style={{
                      padding: '5px 10px', borderRadius: 7, fontSize: 10,
                      background: 'rgba(0,255,136,0.1)', border: '1px solid rgba(0,255,136,0.3)', color: '#00FF88',
                    }} onClick={e => { e.stopPropagation(); alert(`Approved: ${claim.id}`) }}>
                      ✓
                    </button>
                    <button style={{
                      padding: '5px 10px', borderRadius: 7, fontSize: 10,
                      background: 'rgba(255,68,68,0.1)', border: '1px solid rgba(255,68,68,0.3)', color: '#FF4444',
                    }} onClick={e => { e.stopPropagation(); alert(`Escalated: ${claim.id}`) }}>
                      ↑
                    </button>
                  </>
                )}
                {claim.status === 'APPROVED' && <CheckCircle2 size={16} color="#00FF88" />}
              </div>
            </div>
          )
        })}

        {filtered.length === 0 && (
          <div style={{ padding: 48, textAlign: 'center', color: '#555', fontSize: 14 }}>
            No claims match your filters
          </div>
        )}
      </div>
    </div>
  )
}
