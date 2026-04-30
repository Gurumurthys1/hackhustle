import { useState, useEffect } from 'react'
import { Search, CheckCircle2 } from 'lucide-react'
import { fetchClaims } from '../api'

const TIERS = ['ALL', 'TRUSTED', 'CAUTION', 'ELEVATED_RISK', 'HIGH_RISK']
const TIER_COLORS = {
  TRUSTED:       { bg: 'rgba(0,255,136,0.1)',  text: '#00FF88', border: 'rgba(0,255,136,0.25)' },
  CAUTION:       { bg: 'rgba(255,184,0,0.1)',  text: '#FFB800', border: 'rgba(255,184,0,0.25)' },
  ELEVATED_RISK: { bg: 'rgba(255,102,68,0.1)', text: '#FF6644', border: 'rgba(255,102,68,0.25)' },
  HIGH_RISK:     { bg: 'rgba(255,68,68,0.1)',  text: '#FF4444', border: 'rgba(255,68,68,0.25)' },
}



function timeAgo(iso) {
  const diff = Math.floor((Date.now() - new Date(iso)) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`
  return `${Math.floor(diff / 3600)} hr ago`
}

function ScoreBar({ score, tier }) {
  const color = TIER_COLORS[tier]?.text || '#00FF88'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div style={{ width: 80, height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{
          width: `${score}%`, height: '100%', background: color, borderRadius: 4,
          boxShadow: score >= 80 ? `0 0 8px ${color}` : 'none', transition: 'width 0.6s ease',
        }} />
      </div>
      <span style={{ fontFamily: 'Space Mono, monospace', fontSize: 13, color, fontWeight: 700, minWidth: 24 }}>{score}</span>
    </div>
  )
}

export default function ClaimsQueue() {
  const [claims, setClaims]   = useState([])
  const [tierCounts, setTierCounts] = useState({ ALL: 0, TRUSTED: 0, CAUTION: 0, ELEVATED_RISK: 0, HIGH_RISK: 0 })
  const [filter, setFilter]   = useState('ALL')
  const [search, setSearch]   = useState('')
  const [loading, setLoading] = useState(true)
  const [liveData, setLiveData] = useState(false)

  useEffect(() => {
    fetchClaims('ALL', 200)
      .then(data => {
        if (data.claims && data.claims.length > 0) {
          setClaims(data.claims)
          setTierCounts(data.tier_counts || {})
          setLiveData(true)
        }
      })
      .catch(() => { /* use fallback silently */ })
      .finally(() => setLoading(false))
  }, [])

  const displayed = claims.filter(c =>
    (filter === 'ALL' || c.fraud_tier === filter) &&
    (c.id?.toLowerCase().includes(search.toLowerCase()) ||
     c.account_id?.toLowerCase().includes(search.toLowerCase()))
  )

  const reviewCount = claims.filter(c => ['UNDER_REVIEW','ESCALATED'].includes(c.status)).length

  return (
    <div style={{ padding: 32, minHeight: '100vh' }}>
      <header style={{ marginBottom: 32, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 700, letterSpacing: -0.5, marginBottom: 4 }}>Claims Queue</h1>
          <p style={{ color: '#555', fontSize: 13 }}>
            {reviewCount} claims awaiting human review
            {liveData && <span style={{ marginLeft: 10, color: '#00D4AA', fontSize: 11 }}>● LIVE from MongoDB</span>}
            {loading && <span style={{ marginLeft: 10, color: '#666', fontSize: 11 }}>Loading...</span>}
          </p>
        </div>
      </header>

      {/* Tier filter tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {TIERS.map(tier => {
          const active = filter === tier
          const color = tier === 'ALL' ? '#00D4AA' : TIER_COLORS[tier]?.text
          const count = tier === 'ALL' ? claims.length : claims.filter(c => c.fraud_tier === tier).length
          return (
            <button key={tier} onClick={() => setFilter(tier)} style={{
              padding: '8px 16px', borderRadius: 10,
              background: active ? `${color}18` : 'rgba(255,255,255,0.03)',
              border: `1px solid ${active ? color : 'rgba(255,255,255,0.07)'}`,
              color: active ? color : '#666', fontSize: 12, fontWeight: active ? 600 : 400, cursor: 'pointer',
            }}>
              {tier.replace(/_/g, ' ')}
              <span style={{ marginLeft: 6, padding: '2px 7px', borderRadius: 20,
                background: active ? `${color}25` : 'rgba(255,255,255,0.05)', fontSize: 10 }}>
                {count}
              </span>
            </button>
          )
        })}

        <div style={{ marginLeft: 'auto', position: 'relative' }}>
          <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#555' }} />
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search by ID or account..."
            style={{ paddingLeft: 36, paddingRight: 14, paddingTop: 9, paddingBottom: 9, fontSize: 12, width: 230, borderRadius: 10 }} />
        </div>
      </div>

      {/* Table */}
      <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 0.8fr 0.9fr 1.1fr 1fr 0.7fr',
          padding: '14px 20px', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: 10, color: '#555', letterSpacing: 1.5 }}>
          {['CLAIM ID','ACCOUNT','TYPE','RISK TIER','SCORE','AMOUNT','ACTIONS'].map(h => <div key={h}>{h}</div>)}
        </div>

        {displayed.map(claim => {
          const tc = TIER_COLORS[claim.fraud_tier] || TIER_COLORS.TRUSTED
          const amount = claim.order_amount || claim.amount || 0
          return (
            <div key={claim.id} style={{
              display: 'grid', gridTemplateColumns: '1.2fr 1fr 0.8fr 0.9fr 1.1fr 1fr 0.7fr',
              padding: '15px 20px', alignItems: 'center',
              borderBottom: '1px solid rgba(255,255,255,0.04)', cursor: 'default',
            }}>
              <div>
                <div style={{ fontFamily: 'Space Mono, monospace', fontSize: 12, color: '#00D4AA' }}>{claim.id}</div>
                <div style={{ fontSize: 10, color: '#555', marginTop: 2 }}>{timeAgo(claim.created_at)}</div>
              </div>
              <div style={{ fontSize: 12, color: '#aaa' }}>{claim.account_id}</div>
              <div>
                <span style={{ padding: '3px 9px', borderRadius: 6, background: 'rgba(255,255,255,0.05)', fontSize: 11, color: '#888' }}>
                  {claim.claim_type}
                </span>
              </div>
              <div>
                <span style={{ padding: '4px 10px', borderRadius: 7, background: tc.bg, color: tc.text,
                  border: `1px solid ${tc.border}`, fontSize: 10, fontWeight: 600, letterSpacing: 0.5,
                  fontFamily: 'Space Mono, monospace' }}>
                  {(claim.fraud_tier || 'TRUSTED').replace(/_/g, ' ')}
                </span>
              </div>
              <div><ScoreBar score={claim.fraud_score || 0} tier={claim.fraud_tier} /></div>
              <div style={{ fontFamily: 'Space Mono, monospace', fontSize: 13, color: '#ccc' }}>
                ₹{Number(amount).toLocaleString('en-IN')}
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                {['UNDER_REVIEW','ESCALATED'].includes(claim.status) && (
                  <>
                    <button style={{ padding: '5px 10px', borderRadius: 7, fontSize: 10, cursor: 'pointer',
                      background: 'rgba(0,255,136,0.1)', border: '1px solid rgba(0,255,136,0.3)', color: '#00FF88' }}
                      onClick={() => alert(`Approved: ${claim.id}`)}>✓</button>
                    <button style={{ padding: '5px 10px', borderRadius: 7, fontSize: 10, cursor: 'pointer',
                      background: 'rgba(255,68,68,0.1)', border: '1px solid rgba(255,68,68,0.3)', color: '#FF4444' }}
                      onClick={() => alert(`Escalated: ${claim.id}`)}>↑</button>
                  </>
                )}
                {claim.status === 'APPROVED' && <CheckCircle2 size={16} color="#00FF88" />}
              </div>
            </div>
          )
        })}

        {displayed.length === 0 && !loading && (
          <div style={{ padding: 48, textAlign: 'center', color: '#555', fontSize: 14 }}>No claims match your filters</div>
        )}
      </div>
    </div>
  )
}
