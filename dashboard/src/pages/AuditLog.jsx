import { useState } from 'react'
import { Lock, Search, Shield, User, Cpu, Filter } from 'lucide-react'

const ACTOR_ICONS = { SYSTEM: Cpu, ADMIN: User, CUSTOMER: Shield }
const ACTOR_COLORS = { SYSTEM: '#7C7CFF', ADMIN: '#FFB800', CUSTOMER: '#00D4AA' }

const MOCK_LOGS = [
  { id: 1, entity_type: 'return_claims', entity_id: 'CLM-2024-0041', action: 'CLAIM_SUBMITTED',
    actor_type: 'CUSTOMER', actor_id: 'CUST-RING-003',
    metadata: { ip: '10.0.1.42', device: 'fp_abc123' },
    created_at: '2024-06-22 14:32:11 IST' },
  { id: 2, entity_type: 'return_claims', entity_id: 'CLM-2024-0041', action: 'FRAUD_SCORE_COMPUTED',
    actor_type: 'SYSTEM', actor_id: 'fraud-engine-v3',
    metadata: { score: 92, tier: 'HIGH_RISK', latency_ms: 2840 },
    created_at: '2024-06-22 14:32:14 IST' },
  { id: 3, entity_type: 'return_claims', entity_id: 'CLM-2024-0041', action: 'ESCALATED_TO_SENIOR_REVIEW',
    actor_type: 'SYSTEM', actor_id: 'fraud-engine-v3',
    metadata: { reason: 'Score >= 80, FRAUD_RING_MEMBER evidence' },
    created_at: '2024-06-22 14:32:14 IST' },
  { id: 4, entity_type: 'fraud_rings', entity_id: 'RING-0001', action: 'RING_CONFIRMED',
    actor_type: 'ADMIN', actor_id: 'admin@trinetra.ai',
    metadata: { members: 7, total_value: 187400, confidence: 0.97 },
    created_at: '2024-06-22 14:15:02 IST' },
  { id: 5, entity_type: 'return_claims', entity_id: 'CLM-2024-0037', action: 'CLAIM_AUTO_APPROVED',
    actor_type: 'SYSTEM', actor_id: 'fraud-engine-v3',
    metadata: { score: 8, tier: 'TRUSTED', latency_ms: 1120 },
    created_at: '2024-06-22 14:10:44 IST' },
  { id: 6, entity_type: 'accounts', entity_id: 'CUST-FRAUDSTER-002', action: 'BEHAVIORAL_SCORE_UPDATED',
    actor_type: 'SYSTEM', actor_id: 'behavioral-worker',
    metadata: { new_percentile: 97.2, inr_count_90d: 5 },
    created_at: '2024-06-22 13:58:22 IST' },
  { id: 7, entity_type: 'return_claims', entity_id: 'CLM-2024-0039', action: 'REVIEWER_REQUESTED_INFO',
    actor_type: 'ADMIN', actor_id: 'reviewer2@trinetra.ai',
    metadata: { request: 'Additional photo of damaged area required' },
    created_at: '2024-06-22 13:44:08 IST' },
  { id: 8, entity_type: 'return_claims', entity_id: 'CLM-2024-0034', action: 'CLAIM_AUTO_APPROVED',
    actor_type: 'SYSTEM', actor_id: 'fraud-engine-v3',
    metadata: { score: 5, tier: 'TRUSTED', latency_ms: 980 },
    created_at: '2024-06-22 13:16:31 IST' },
]

const ACTION_COLOR = {
  CLAIM_SUBMITTED:            '#00D4AA',
  FRAUD_SCORE_COMPUTED:       '#7C7CFF',
  ESCALATED_TO_SENIOR_REVIEW: '#FF4444',
  RING_CONFIRMED:             '#FF4444',
  CLAIM_AUTO_APPROVED:        '#00FF88',
  BEHAVIORAL_SCORE_UPDATED:   '#FFB800',
  REVIEWER_REQUESTED_INFO:    '#FFB800',
}

export default function AuditLog() {
  const [search, setSearch] = useState('')
  const [actorFilter, setActorFilter] = useState('ALL')

  const filtered = MOCK_LOGS.filter(l =>
    (actorFilter === 'ALL' || l.actor_type === actorFilter) &&
    (l.action.toLowerCase().includes(search.toLowerCase()) ||
     l.entity_id.toLowerCase().includes(search.toLowerCase()) ||
     l.actor_id.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <div style={{ padding: 32, minHeight: '100vh' }}>
      <header style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <Lock size={20} color="#00D4AA" />
          <h1 style={{ fontSize: 26, fontWeight: 700, letterSpacing: -0.5 }}>Audit Vault</h1>
        </div>
        <p style={{ color: '#555', fontSize: 13 }}>
          Immutable, append-only event log — DPDPA compliant. DELETE and UPDATE are revoked at DB level.
        </p>
        {/* Compliance badge */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8, marginTop: 10,
          padding: '6px 14px', borderRadius: 8,
          background: 'rgba(0,255,136,0.08)', border: '1px solid rgba(0,255,136,0.2)',
        }}>
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#00FF88', boxShadow: '0 0 6px #00FF88' }} />
          <span style={{ fontSize: 11, color: '#00FF88', fontFamily: 'Space Mono, monospace' }}>
            DPDPA § 9.4 — Full audit trail enforced
          </span>
        </div>
      </header>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, alignItems: 'center' }}>
        {['ALL', 'SYSTEM', 'ADMIN', 'CUSTOMER'].map(a => (
          <button key={a} onClick={() => setActorFilter(a)} style={{
            padding: '8px 16px', borderRadius: 10, fontSize: 12,
            background: actorFilter === a ? 'rgba(0,212,170,0.12)' : 'rgba(255,255,255,0.03)',
            border: `1px solid ${actorFilter === a ? '#00D4AA' : 'rgba(255,255,255,0.07)'}`,
            color: actorFilter === a ? '#00D4AA' : '#666',
          }}>
            {a}
          </button>
        ))}
        <div style={{ marginLeft: 'auto', position: 'relative' }}>
          <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#555' }} />
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search action, entity, actor..."
            style={{ paddingLeft: 36, paddingRight: 14, paddingTop: 9, paddingBottom: 9, fontSize: 12, width: 260, borderRadius: 10 }}
          />
        </div>
      </div>

      {/* Log Entries */}
      <div style={{
        background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 16, overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          display: 'grid', gridTemplateColumns: '0.8fr 1.2fr 1.5fr 0.8fr 1.5fr 1.2fr',
          padding: '12px 20px', borderBottom: '1px solid rgba(255,255,255,0.05)',
          fontSize: 9, color: '#555', letterSpacing: 1.5,
        }}>
          {['TIME', 'ENTITY', 'ACTION', 'ACTOR', 'ACTOR ID', 'METADATA'].map(h => <div key={h}>{h}</div>)}
        </div>

        {filtered.map((log, i) => {
          const ActorIcon = ACTOR_ICONS[log.actor_type] || Shield
          const actorColor = ACTOR_COLORS[log.actor_type] || '#888'
          const actionColor = ACTION_COLOR[log.action] || '#888'
          return (
            <div key={log.id} style={{
              display: 'grid', gridTemplateColumns: '0.8fr 1.2fr 1.5fr 0.8fr 1.5fr 1.2fr',
              padding: '13px 20px', alignItems: 'center',
              borderBottom: i < filtered.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none',
              transition: 'background 0.15s',
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <div style={{ fontSize: 10, color: '#555', fontFamily: 'Space Mono, monospace' }}>
                {log.created_at.split(' ').slice(1).join(' ')}
              </div>
              <div>
                <div style={{ fontSize: 10, color: '#777', marginBottom: 2 }}>{log.entity_type}</div>
                <div style={{ fontSize: 11, fontFamily: 'Space Mono, monospace', color: '#00D4AA' }}>
                  {log.entity_id.slice(0, 20)}
                </div>
              </div>
              <div style={{
                fontSize: 10, fontWeight: 600, letterSpacing: 0.5,
                color: actionColor, fontFamily: 'Space Mono, monospace',
              }}>
                {log.action}
              </div>
              <div>
                <div style={{
                  display: 'inline-flex', alignItems: 'center', gap: 5,
                  padding: '3px 8px', borderRadius: 6,
                  background: `${actorColor}12`, border: `1px solid ${actorColor}30`,
                  color: actorColor, fontSize: 10, fontWeight: 600,
                }}>
                  <ActorIcon size={10} />
                  {log.actor_type}
                </div>
              </div>
              <div style={{ fontSize: 11, color: '#888' }}>{log.actor_id}</div>
              <div style={{ fontSize: 10, color: '#555', fontFamily: 'Space Mono, monospace' }}>
                {JSON.stringify(log.metadata).slice(0, 50)}…
              </div>
            </div>
          )
        })}
      </div>

      <div style={{ marginTop: 16, fontSize: 11, color: '#444', textAlign: 'center' }}>
        Showing {filtered.length} of {MOCK_LOGS.length} entries ·
        <span style={{ color: '#00FF88', marginLeft: 6 }}>
          Records are cryptographically append-only — no modifications permitted
        </span>
      </div>
    </div>
  )
}
