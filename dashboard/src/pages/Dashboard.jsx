import { useState, useEffect } from 'react'
import { Activity, ShieldAlert, ShieldCheck, Layers, Bell, Search, Network } from 'lucide-react'
import { RingNetworkGraph } from '../components/RingNetworkGraph.jsx'
import { EvidencePanel } from '../components/EvidencePanel.jsx'
import { fetchKPIs, fetchGraph, fetchClaims, fetchClaim } from '../api'


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
  const [selectedClaim, setSelectedClaim] = useState(null)
  const [activeTab, setActiveTab] = useState('Network View')
  const [kpis, setKpis] = useState({
    claims_per_hour: 0, auto_approved: 0, auto_approval_pct: 0,
    in_review: 0, in_review_pct: 0, rings_detected: 0
  })
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  const [liveData, setLiveData] = useState(false)
  const TABS = ['Network View', 'Entity Clusters', 'Temporal Flow']

  useEffect(() => {
    Promise.all([fetchKPIs(), fetchGraph()])
      .then(([kpiData, gData]) => {
        if (kpiData) {
          setKpis(kpiData)
        }
        if (gData && gData.nodes && gData.nodes.length > 0) {
          setGraphData({ ...gData, account_id: gData.nodes[0]?.id })
        }
        setLiveData(true)
      })
      .catch(() => {})
  }, [])

  const STATS = [
    { label: 'CLAIMS',  value: kpis.claims_per_hour, icon: Activity,    color: '#00D4AA' },
    { label: 'AUTO-APPROVED',  value: kpis.auto_approved, sub: `${kpis.auto_approval_pct}%`, icon: ShieldCheck, color: '#00FF88' },
    { label: 'IN REVIEW',      value: kpis.in_review,  sub: `${kpis.in_review_pct}%`,      icon: ShieldAlert, color: '#FFB800' },
    { label: 'RINGS DETECTED', value: kpis.rings_detected, icon: Network,     color: '#FF4444' },
  ]

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
            {liveData && <span style={{ marginLeft: 10, color: '#00D4AA', fontSize: 11 }}>● LIVE from MongoDB</span>}
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
            data={graphData}
            onNodeClick={async (node) => {
              if (node.type === 'account') {
                try {
                  const data = await fetchClaims('ALL', 100);
                  const claimMeta = data.claims?.find(c => c.account_id === node.id);
                  if (claimMeta) {
                    const fullClaim = await fetchClaim(claimMeta.id);
                    setSelectedClaim(fullClaim);
                  } else {
                    setSelectedClaim({ account_id: node.id, fraud_score: node.risk_score || node.score || 0, fraud_tier: node.tier || 'TRUSTED', evidence: [] });
                  }
                } catch (e) {
                  setSelectedClaim({ account_id: node.id, evidence: [] });
                }
              }
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
