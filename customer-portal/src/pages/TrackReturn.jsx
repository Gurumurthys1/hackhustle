import { useState } from 'react'
import { Search, Package, Truck, CheckCircle2, Clock, AlertTriangle, ArrowRight } from 'lucide-react'

const STATUS_STEPS = ['SUBMITTED', 'PROCESSING', 'SCORED', 'APPROVED']

// Demo claims for the track page
const DEMO_CLAIMS = {
  'CLM-DEMO-001': {
    id: 'CLM-DEMO-001', status: 'APPROVED', tier: 'TRUSTED',
    claimType: 'DAMAGE', amount: 3499, productName: 'Wireless Headphones Pro',
    submittedAt: '2024-06-21 09:14 IST', resolvedAt: '2024-06-21 09:16 IST',
    message: 'Your return has been approved. Refund of ₹3,499 will be credited in 3–5 business days.',
    timeline: [
      { status: 'SUBMITTED',  time: '09:14 IST', done: true },
      { status: 'PROCESSING', time: '09:14 IST', done: true },
      { status: 'SCORED',     time: '09:15 IST', done: true },
      { status: 'APPROVED',   time: '09:16 IST', done: true },
    ]
  },
  'CLM-DEMO-002': {
    id: 'CLM-DEMO-002', status: 'UNDER_REVIEW', tier: 'CAUTION',
    claimType: 'INR', amount: 1299, productName: 'Smart Watch Band',
    submittedAt: '2024-06-22 14:22 IST', resolvedAt: null,
    message: 'We need a bit more information. Our team will contact you within 24 hours.',
    timeline: [
      { status: 'SUBMITTED',  time: '14:22 IST', done: true },
      { status: 'PROCESSING', time: '14:23 IST', done: true },
      { status: 'UNDER_REVIEW', time: '14:24 IST', done: true, current: true },
      { status: 'RESOLVED',   time: 'Pending', done: false },
    ]
  },
}

const STATUS_INFO = {
  SUBMITTED:    { color: '#00D4AA', icon: Package,      label: 'Submitted' },
  PROCESSING:   { color: '#7C7CFF', icon: Clock,        label: 'Processing' },
  SCORED:       { color: '#00D4AA', icon: CheckCircle2, label: 'Verified' },
  UNDER_REVIEW: { color: '#FFB800', icon: AlertTriangle,label: 'Under Review' },
  APPROVED:     { color: '#00FF88', icon: CheckCircle2, label: 'Approved' },
  DENIED:       { color: '#FF4444', icon: AlertTriangle,label: 'Denied' },
  ESCALATED:    { color: '#FF6644', icon: AlertTriangle,label: 'Escalated' },
}

function ClaimCard({ claim }) {
  const si = STATUS_INFO[claim.status] || STATUS_INFO.SUBMITTED
  const Icon = si.icon

  return (
    <div style={{
      width: '100%', maxWidth: 520,
      background: 'rgba(255,255,255,0.025)',
      border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: 16, overflow: 'hidden',
      animation: 'fadeUp 0.3s ease forwards',
    }}>
      {/* Header */}
      <div style={{
        padding: '20px 24px',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
      }}>
        <div>
          <div style={{ fontSize: 11, color: '#555', letterSpacing: 1.5, marginBottom: 4 }}>RETURN REQUEST</div>
          <div style={{ fontFamily: 'Space Mono, monospace', fontSize: 14, color: '#00D4AA', marginBottom: 6 }}>
            {claim.id}
          </div>
          <div style={{ fontSize: 14, color: '#ccc', fontWeight: 500 }}>{claim.productName}</div>
          <div style={{ fontSize: 12, color: '#555', marginTop: 2 }}>
            {claim.claimType.replace('_', ' ')} · ₹{claim.amount.toLocaleString('en-IN')}
          </div>
        </div>
        <div style={{
          padding: '8px 14px', borderRadius: 10,
          background: `${si.color}15`, border: `1px solid ${si.color}35`,
          display: 'flex', alignItems: 'center', gap: 7,
        }}>
          <Icon size={14} color={si.color} />
          <span style={{ fontSize: 12, color: si.color, fontWeight: 600 }}>{si.label}</span>
        </div>
      </div>

      {/* Timeline */}
      <div style={{ padding: '20px 24px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ fontSize: 10, color: '#555', letterSpacing: 1.5, marginBottom: 14 }}>TIMELINE</div>
        <div style={{ position: 'relative' }}>
          {claim.timeline.map((t, i) => {
            const tsi = STATUS_INFO[t.status] || STATUS_INFO.SUBMITTED
            const TIcon = tsi.icon
            return (
              <div key={i} style={{ display: 'flex', gap: 14, marginBottom: i < claim.timeline.length - 1 ? 16 : 0 }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                    background: t.done ? `${tsi.color}20` : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${t.done ? tsi.color : 'rgba(255,255,255,0.1)'}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    ...(t.current ? { boxShadow: `0 0 10px ${tsi.color}` } : {}),
                  }}>
                    <TIcon size={13} color={t.done ? tsi.color : '#444'} />
                  </div>
                  {i < claim.timeline.length - 1 && (
                    <div style={{ width: 1, flex: 1, minHeight: 12, marginTop: 3, background: t.done ? 'rgba(0,212,170,0.2)' : 'rgba(255,255,255,0.06)' }} />
                  )}
                </div>
                <div style={{ paddingBottom: i < claim.timeline.length - 1 ? 12 : 0 }}>
                  <div style={{ fontSize: 13, color: t.done ? '#ccc' : '#555', fontWeight: t.current ? 600 : 400 }}>
                    {t.status.replace('_', ' ')}
                  </div>
                  <div style={{ fontSize: 11, color: '#444', marginTop: 1 }}>{t.time}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Message */}
      <div style={{ padding: '16px 24px' }}>
        <p style={{ fontSize: 13, color: '#888', lineHeight: 1.6 }}>{claim.message}</p>
        <div style={{ fontSize: 11, color: '#444', marginTop: 8 }}>
          Submitted: {claim.submittedAt}
          {claim.resolvedAt && ` · Resolved: ${claim.resolvedAt}`}
        </div>
      </div>
    </div>
  )
}

export default function TrackReturn() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      // Try real API first
      let found = null
      try {
        const res = await fetch(`/api/v1/returns/${query.trim()}?accountId=DEMO-ACC-001`)
        if (res.ok) found = await res.json()
      } catch {
        // Fall through to demo
      }

      // Demo fallback
      if (!found) {
        await new Promise(r => setTimeout(r, 800))
        found = DEMO_CLAIMS[query.trim().toUpperCase()] || null
      }

      if (found) {
        setResult(found)
      } else {
        setError('No return request found with this ID. Try: CLM-DEMO-001 or CLM-DEMO-002')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ width: '100%', maxWidth: 540, padding: '0 24px 48px' }}>
      <div style={{ marginBottom: 36 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 8, letterSpacing: -0.5 }}>Track Your Return</h1>
        <p style={{ color: '#666', fontSize: 14 }}>Enter your Return ID from the confirmation email</p>
      </div>

      <form onSubmit={handleSearch} style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', gap: 10 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={15} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: '#555' }} />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="e.g. CLM-DEMO-001"
              style={{ paddingLeft: 42, paddingRight: 16, paddingTop: 14, paddingBottom: 14, fontSize: 14 }}
            />
          </div>
          <button type="submit" disabled={loading} style={{
            padding: '0 24px',
            background: 'rgba(0,212,170,0.15)', border: '1px solid rgba(0,212,170,0.4)',
            borderRadius: 12, color: '#00D4AA', fontSize: 13, fontWeight: 600,
            display: 'flex', alignItems: 'center', gap: 8,
          }}>
            {loading ? <span className="spinner" /> : <><ArrowRight size={15} /> Track</>}
          </button>
        </div>
      </form>

      {error && (
        <div style={{
          padding: '14px 18px', borderRadius: 10, marginBottom: 20,
          background: 'rgba(255,184,0,0.08)', border: '1px solid rgba(255,184,0,0.2)',
          color: '#FFB800', fontSize: 13,
          display: 'flex', alignItems: 'center', gap: 10,
        }}>
          <AlertTriangle size={15} />
          {error}
        </div>
      )}

      {result && <ClaimCard claim={result} />}

      {!result && !error && !loading && (
        <div style={{ textAlign: 'center', padding: '40px 0', color: '#333' }}>
          <Package size={32} color="#333" style={{ marginBottom: 12 }} />
          <div style={{ fontSize: 14 }}>Enter a Return ID to see status</div>
          <div style={{ fontSize: 12, marginTop: 6, color: '#2a2a2a' }}>
            Demo: try <code style={{ color: '#00D4AA' }}>CLM-DEMO-001</code> or <code style={{ color: '#00D4AA' }}>CLM-DEMO-002</code>
          </div>
        </div>
      )}
    </div>
  )
}
