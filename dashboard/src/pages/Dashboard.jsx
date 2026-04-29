import { useState, useEffect } from 'react'
import { Activity, ShieldAlert, ShieldCheck, Layers, Bell, Search, Network } from 'lucide-react'
import { RingNetworkGraph } from '../components/RingNetworkGraph.jsx'
import { EvidencePanel } from '../components/EvidencePanel.jsx'

/* ── Mock data (replaced by real API calls in production) ── */
const MOCK_GRAPH_DATA = {
  nodes: [
    { id: 'acc_001', type: 'account', risk_score: 12 },
    { id: 'acc_002', type: 'account', risk_score: 87 },
    { id: 'acc_003', type: 'account', risk_score: 91 },
    { id: 'acc_004', type: 'account', risk_score: 78 },
    { id: 'dev_abc', type: 'device' },
    { id: 'dev_xyz', type: 'device' },
    { id: 'ip_10_0', type: 'ip' },
    { id: 'addr_mumbai', type: 'address' },
  ],
  links: [
    { source: 'acc_002', target: 'dev_abc',    relationship: 'USES_DEVICE' },
    { source: 'acc_003', target: 'dev_abc',    relationship: 'USES_DEVICE' },
    { source: 'acc_004', target: 'dev_xyz',    relationship: 'USES_DEVICE' },
    { source: 'acc_002', target: 'ip_10_0',    relationship: 'SHARES_IP' },
    { source: 'acc_003', target: 'ip_10_0',    relationship: 'SHARES_IP' },
    { source: 'acc_003', target: 'addr_mumbai',relationship: 'SHARES_ADDRESS' },
    { source: 'acc_004', target: 'addr_mumbai',relationship: 'SHARES_ADDRESS' },
    { source: 'acc_001', target: 'dev_xyz',    relationship: 'USES_DEVICE' },
  ],
  account_id: 'acc_002',
}

const MOCK_CLAIM = {
  account_id: 'acc_002',
  fraud_score: 82,
  fraud_tier: 'HIGH_RISK',
  sub_scores: { image: 35, receipt: 20, behavioral: 15, carrier: 7, graph: 5 },
  evidence: [
    { type: 'IMAGE_ELA',              severity: 'HIGH',     detail: 'Localized editing detected in bottom-right quadrant',   score_added: 20 },
    { type: 'EXIF_DATE_MISMATCH',     severity: 'HIGH',     detail: 'Photo taken 3 days before purchase date',               score_added: 15 },
    { type: 'RECEIPT_AMOUNT_MISMATCH',severity: 'HIGH',     detail: 'Receipt: ₹2,999 vs Order: ₹4,599 (35% variance)',       score_added: 20 },
    { type: 'SHARED_DEVICE_FINGERPRINT', severity: 'MEDIUM', detail: 'Device fingerprint shared with 2 other accounts',      score_added: 15 },
    { type: 'HIGH_INR_RATE',          severity: 'MEDIUM',   detail: '4 INR claims in last 90 days (threshold: 2)',           score_added: 12 },
  ],
}

const STATS = [
  { label: 'CLAIMS / HOUR',  value: '247', change: '+12%', icon: Activity,    color: '#00D4AA' },
  { label: 'AUTO-APPROVED',  value: '231', sub: '94%',     icon: ShieldCheck, color: '#00FF88' },
  { label: 'IN REVIEW',      value: '12',  sub: '5%',      icon: ShieldAlert, color: '#FFB800' },
  { label: 'RINGS DETECTED', value: '4',   change: '+1',   icon: Network,     color: '#FF4444' },
]

function StatCard({ stat }) {
  const Icon = stat.icon
  return (
    <div style={{
      background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)',
      borderRadius: 16, padding: 24,
      transition: 'border-color 0.2s',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ padding: 10, background: `${stat.color}18`, borderRadius: 10 }}>
          <Icon size={20} color={stat.color} />
        </div>
        {stat.change && (
          <span style={{ color: stat.color, fontSize: 12, fontWeight: 600, alignSelf: 'flex-start' }}>
            {stat.change}
          </span>
        )}
      </div>
      <div style={{ fontSize: 10, color: '#555', letterSpacing: 1.8, marginBottom: 6 }}>{stat.label}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
        <span style={{ fontSize: 30, fontWeight: 700, fontFamily: 'Space Mono, monospace', color: '#fff' }}>
          {stat.value}
        </span>
        {stat.sub && <span style={{ fontSize: 13, color: '#555' }}>({stat.sub})</span>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [selectedClaim, setSelectedClaim] = useState(MOCK_CLAIM)
  const [activeTab, setActiveTab] = useState('Network View')
  const TABS = ['Network View', 'Entity Clusters', 'Temporal Flow']

  return (
    <div style={{ padding: 32, minHeight: '100vh' }}>
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 36 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 4, letterSpacing: -0.5 }}>
            Intelligence Center
          </h1>
          <p style={{ color: '#555', fontSize: 13 }}>
            Real-time fraud surveillance across the ecosystem
          </p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ position: 'relative' }}>
            <Search size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#555' }} />
            <input
              placeholder="Search Claim ID, Email, IP..."
              style={{ padding: '11px 14px 11px 38px', width: 280, fontSize: 13, borderRadius: 12 }}
            />
          </div>
          <button style={{
            width: 44, height: 44, borderRadius: 12,
            background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Bell size={19} color="#777" />
          </button>
        </div>
      </header>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 20, marginBottom: 36 }}>
        {STATS.map((s, i) => <StatCard key={i} stat={s} />)}
      </div>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 390px', gap: 28, minHeight: 580 }}>
        {/* Graph */}
        <div style={{
          background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.07)',
          borderRadius: 20, overflow: 'hidden', position: 'relative',
        }}>
          {/* Graph header */}
          <div style={{ position: 'absolute', top: 20, left: 20, zIndex: 10 }}>
            <div style={{ fontSize: 10, color: '#555', letterSpacing: 2, marginBottom: 10 }}>
              FRAUD RING INTELLIGENCE
            </div>
            <div style={{ display: 'flex', gap: 6 }}>
              {TABS.map(tab => (
                <button key={tab} onClick={() => setActiveTab(tab)} style={{
                  padding: '7px 14px',
                  background: activeTab === tab ? 'rgba(0,255,136,0.1)' : 'transparent',
                  border: `1px solid ${activeTab === tab ? '#00FF88' : 'rgba(255,255,255,0.08)'}`,
                  borderRadius: 8, color: activeTab === tab ? '#00FF88' : '#555',
                  fontSize: 11, fontWeight: activeTab === tab ? 600 : 400,
                }}>
                  {tab}
                </button>
              ))}
            </div>
          </div>
          <RingNetworkGraph
            data={MOCK_GRAPH_DATA}
            onNodeClick={(node) => {
              if (node.type === 'account') setSelectedClaim({ ...MOCK_CLAIM, account_id: node.id, fraud_score: node.risk_score || 50 })
            }}
            height={580}
          />
        </div>

        {/* Evidence Panel */}
        <EvidencePanel
          claim={selectedClaim}
          onDecision={(d) => {
            alert(`Decision recorded: ${d}\nClaim: ${selectedClaim.account_id}`)
          }}
        />
      </div>
    </div>
  )
}
