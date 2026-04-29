import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle, 
         Eye, FileText, Network, Package } from 'lucide-react';

const SEVERITY_STYLES = {
  CRITICAL: { bg: 'rgba(255,68,68,0.15)', border: '#FF4444', icon: XCircle, color: '#FF4444' },
  HIGH:     { bg: 'rgba(255,68,68,0.08)', border: '#FF6644', icon: AlertTriangle, color: '#FF6644' },
  MEDIUM:   { bg: 'rgba(255,184,0,0.08)', border: '#FFB800', icon: AlertTriangle, color: '#FFB800' },
  LOW:      { bg: 'rgba(0,212,170,0.08)', border: '#00D4AA', icon: Shield, color: '#00D4AA' },
};

const CATEGORY_ICONS = {
  image:     { icon: Eye, label: 'Image Forensics' },
  receipt:   { icon: FileText, label: 'Receipt Validation' },
  behavioral:{ icon: Shield, label: 'Behavioral Analysis' },
  carrier:   { icon: Package, label: 'Carrier Validation' },
  graph:     { icon: Network, label: 'Network Analysis' },
};

export function EvidencePanel({ claim, onDecision }) {
  const [activeTab, setActiveTab] = useState('overview');

  const tierColors = {
    TRUSTED:      '#00FF88',
    CAUTION:      '#FFB800',
    ELEVATED_RISK:'#FF6644',
    HIGH_RISK:    '#FF4444',
  };

  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: 16,
      padding: 24,
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      gap: 20,
      fontFamily: 'Sora, sans-serif',
      color: '#fff'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ color: '#888', fontSize: 11, letterSpacing: 2, marginBottom: 4 }}>
            CLAIM EVIDENCE REVIEW
          </div>
          <div style={{ color: '#fff', fontFamily: 'Space Mono, monospace', fontSize: 13 }}>
            CUS-****-{claim?.account_id?.slice(-4)}
          </div>
        </div>
        
        {/* Fraud Score Ring */}
        <div style={{ position: 'relative', width: 72, height: 72 }}>
          <svg width={72} height={72} viewBox="0 0 72 72">
            <circle cx={36} cy={36} r={30} fill="none" 
              stroke="rgba(255,255,255,0.1)" strokeWidth={6} />
            <circle cx={36} cy={36} r={30} fill="none"
              stroke={tierColors[claim?.fraud_tier] || '#00FF88'} strokeWidth={6}
              strokeDasharray={`${(claim?.fraud_score / 100) * 188.5} 188.5`}
              strokeLinecap="round"
              transform="rotate(-90 36 36)"
              style={{ filter: `drop-shadow(0 0 6px ${tierColors[claim?.fraud_tier]})` }} />
          </svg>
          <div style={{
            position: 'absolute', inset: 0, display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            flexDirection: 'column'
          }}>
            <span style={{ color: '#fff', fontSize: 18, fontWeight: 700,
                           fontFamily: 'Space Mono, monospace' }}>
              {claim?.fraud_score}
            </span>
            <span style={{ color: '#888', fontSize: 9 }}>/ 100</span>
          </div>
        </div>
      </div>

      {/* Sub-scores */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 8 }}>
        {Object.entries(CATEGORY_ICONS).map(([key, { icon: Icon, label }]) => (
          <div key={key} style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 8, padding: '8px 4px', textAlign: 'center'
          }}>
            <Icon size={14} color="#00D4AA" style={{ marginBottom: 4 }} />
            <div style={{ color: '#fff', fontSize: 13, fontWeight: 700,
                          fontFamily: 'Space Mono, monospace' }}>
              +{claim?.sub_scores?.[key] || 0}
            </div>
            <div style={{ color: '#888', fontSize: 9, marginTop: 2 }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Evidence List */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ color: '#888', fontSize: 11, letterSpacing: 2, marginBottom: 4 }}>
          EVIDENCE LOG
        </div>
        {claim?.evidence?.map((ev, i) => {
          const style = SEVERITY_STYLES[ev.severity] || SEVERITY_STYLES.LOW;
          const Icon = style.icon;
          return (
            <div key={i} style={{
              background: style.bg,
              border: `1px solid ${style.border}`,
              borderRadius: 8, padding: '10px 14px',
              display: 'flex', gap: 10, alignItems: 'flex-start'
            }}>
              <Icon size={14} color={style.color} style={{ marginTop: 2, flexShrink: 0 }} />
              <div>
                <div style={{ color: style.color, fontSize: 10, letterSpacing: 1,
                              fontFamily: 'Space Mono, monospace', marginBottom: 2 }}>
                  {ev.type} · +{ev.score_added}pts
                </div>
                <div style={{ color: '#ccc', fontSize: 12 }}>{ev.detail}</div>
              </div>
            </div>
          );
        })}
        
        {(!claim?.evidence || claim.evidence.length === 0) && (
          <div style={{ color: '#555', textAlign: 'center', padding: 20 }}>
            <CheckCircle size={24} color="#00FF88" style={{ marginBottom: 8 }} />
            <div>No fraud signals detected</div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: 8 }}>
        <button onClick={() => onDecision('APPROVE')} style={{
          flex: 1, padding: '12px 0',
          background: 'rgba(0,255,136,0.15)', border: '1px solid #00FF88',
          borderRadius: 8, color: '#00FF88', cursor: 'pointer',
          fontFamily: 'Space Mono, monospace', fontSize: 12,
          transition: 'all 0.2s'
        }}>
          ✓ APPROVE
        </button>
        <button onClick={() => onDecision('REQUEST_INFO')} style={{
          flex: 1, padding: '12px 0',
          background: 'rgba(255,184,0,0.15)', border: '1px solid #FFB800',
          borderRadius: 8, color: '#FFB800', cursor: 'pointer',
          fontFamily: 'Space Mono, monospace', fontSize: 12
        }}>
          ? MORE INFO
        </button>
        <button onClick={() => onDecision('ESCALATE')} style={{
          flex: 1, padding: '12px 0',
          background: 'rgba(255,68,68,0.15)', border: '1px solid #FF4444',
          borderRadius: 8, color: '#FF4444', cursor: 'pointer',
          fontFamily: 'Space Mono, monospace', fontSize: 12
        }}>
          ↑ ESCALATE
        </button>
      </div>
    </div>
  );
}
