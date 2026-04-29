import { useState } from 'react'
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts'

const DAILY_SCORES = [
  { day: 'Jun 16', auto: 94, manual: 5, escalated: 1 },
  { day: 'Jun 17', auto: 92, manual: 6, escalated: 2 },
  { day: 'Jun 18', auto: 95, manual: 4, escalated: 1 },
  { day: 'Jun 19', auto: 91, manual: 7, escalated: 2 },
  { day: 'Jun 20', auto: 93, manual: 5, escalated: 2 },
  { day: 'Jun 21', auto: 96, manual: 3, escalated: 1 },
  { day: 'Jun 22', auto: 94, manual: 5, escalated: 1 },
]

const SCORE_DIST = [
  { range: '0-9',   count: 412, tier: 'TRUSTED' },
  { range: '10-29', count: 318, tier: 'TRUSTED' },
  { range: '30-49', count: 87,  tier: 'CAUTION' },
  { range: '50-59', count: 43,  tier: 'CAUTION' },
  { range: '60-69', count: 29,  tier: 'ELEVATED_RISK' },
  { range: '70-79', count: 18,  tier: 'ELEVATED_RISK' },
  { range: '80-89', count: 12,  tier: 'HIGH_RISK' },
  { range: '90-100',count: 7,   tier: 'HIGH_RISK' },
]

const TIER_COLORS_MAP = {
  TRUSTED: '#00FF88', CAUTION: '#FFB800', ELEVATED_RISK: '#FF6644', HIGH_RISK: '#FF4444',
}

const DETECTOR_PERF = [
  { name: 'ELA (Image)',      precision: 91, recall: 78, f1: 84 },
  { name: 'EXIF Analysis',   precision: 96, recall: 62, f1: 75 },
  { name: 'CLIP Similarity', precision: 88, recall: 84, f1: 86 },
  { name: 'pHash Match',     precision: 99, recall: 71, f1: 83 },
  { name: 'Receipt OCR',     precision: 87, recall: 79, f1: 83 },
  { name: 'Behavioral ML',   precision: 82, recall: 88, f1: 85 },
  { name: 'Graph / Rings',   precision: 94, recall: 69, f1: 80 },
]

const CUSTOM_TOOLTIP_STYLE = {
  background: '#0E1420', border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: 8, padding: '10px 14px', fontFamily: 'Sora, sans-serif', fontSize: 12,
}

function MetricCard({ label, value, sub, color, hint }) {
  return (
    <div style={{
      padding: '20px 24px', borderRadius: 14,
      background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)',
    }}>
      <div style={{ fontSize: 9, color: '#555', letterSpacing: 2, marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 30, fontWeight: 700, fontFamily: 'Space Mono, monospace', color }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: '#555', marginTop: 4 }}>{sub}</div>}
      {hint && <div style={{ fontSize: 10, color: '#444', marginTop: 4, fontStyle: 'italic' }}>{hint}</div>}
    </div>
  )
}

export default function ModelPerformance() {
  return (
    <div style={{ padding: 32, minHeight: '100vh' }}>
      <header style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, letterSpacing: -0.5, marginBottom: 4 }}>Model Performance</h1>
        <p style={{ color: '#555', fontSize: 13 }}>Live metrics for all 6 fraud detection components — last 7 days</p>
      </header>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 32 }}>
        <MetricCard label="AUTO-APPROVAL RATE" value="94.1%" color="#00FF88" hint="Target: ≥ 90%" />
        <MetricCard label="FALSE POSITIVE RATE" value="1.4%" color="#00D4AA" hint="Target: ≤ 2% (CRITICAL)" />
        <MetricCard label="FRAUD DETECTION RATE" value="89.3%" color="#FFB800" hint="Based on confirmed fraud" />
        <MetricCard label="AVG SCORE LATENCY" value="3.2s" color="#7C7CFF" hint="Full pipeline (<10s SLA)" />
      </div>

      {/* Two-column charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        {/* Daily Approval Breakdown */}
        <div style={{
          padding: 24, borderRadius: 16,
          background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)',
        }}>
          <div style={{ fontSize: 12, color: '#888', letterSpacing: 1.5, marginBottom: 20 }}>
            DAILY DECISION BREAKDOWN (%)
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={DAILY_SCORES}>
              <defs>
                <linearGradient id="autoGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00FF88" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#00FF88" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="day" tick={{ fontSize: 10, fill: '#555' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#555' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={CUSTOM_TOOLTIP_STYLE} />
              <Area type="monotone" dataKey="auto" stroke="#00FF88" fill="url(#autoGrad)" strokeWidth={2} name="Auto-Approved %" />
              <Area type="monotone" dataKey="manual" stroke="#FFB800" fill="transparent" strokeWidth={1.5} strokeDasharray="4 4" name="Manual Review %" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Score Distribution */}
        <div style={{
          padding: 24, borderRadius: 16,
          background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)',
        }}>
          <div style={{ fontSize: 12, color: '#888', letterSpacing: 1.5, marginBottom: 20 }}>
            FRAUD SCORE DISTRIBUTION — TODAY
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={SCORE_DIST}>
              <XAxis dataKey="range" tick={{ fontSize: 10, fill: '#555' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#555' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={CUSTOM_TOOLTIP_STYLE} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]} name="Claims">
                {SCORE_DIST.map((entry, i) => (
                  <Cell key={i} fill={TIER_COLORS_MAP[entry.tier]} opacity={0.8} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detector Performance Table */}
      <div style={{
        padding: 24, borderRadius: 16,
        background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)',
      }}>
        <div style={{ fontSize: 12, color: '#888', letterSpacing: 1.5, marginBottom: 20 }}>
          DETECTOR PERFORMANCE — PRECISION / RECALL / F1
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {DETECTOR_PERF.map(d => (
            <div key={d.name} style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr', alignItems: 'center', gap: 16 }}>
              <span style={{ fontSize: 13, color: '#ccc' }}>{d.name}</span>
              {[
                { label: 'Precision', val: d.precision, color: '#00D4AA' },
                { label: 'Recall',    val: d.recall,    color: '#7C7CFF' },
                { label: 'F1 Score',  val: d.f1,        color: '#FFB800' },
              ].map(metric => (
                <div key={metric.label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 9, color: '#555', letterSpacing: 1 }}>{metric.label}</span>
                    <span style={{ fontFamily: 'Space Mono, monospace', fontSize: 11, color: metric.color }}>{metric.val}%</span>
                  </div>
                  <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 4 }}>
                    <div style={{
                      width: `${metric.val}%`, height: '100%',
                      background: metric.color, borderRadius: 4,
                    }} />
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
