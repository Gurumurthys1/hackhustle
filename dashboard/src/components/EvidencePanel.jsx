import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle, 
         Eye, FileText, Network, Package } from 'lucide-react';

const SEVERITY_STYLES = {
  CRITICAL: { bg: '#2C1D1D', border: '#5C2D2D', icon: XCircle, color: '#E57373' },
  HIGH:     { bg: '#2A2016', border: '#5C4020', icon: AlertTriangle, color: '#FFB74D' },
  MEDIUM:   { bg: '#2A2616', border: '#5C5420', icon: AlertTriangle, color: '#FFF176' },
  LOW:      { bg: '#162A24', border: '#205C46', icon: Shield, color: '#81C784' },
};

const CATEGORY_ICONS = {
  image:     { icon: Eye, label: 'Image Forensics' },
  receipt:   { icon: FileText, label: 'Receipt Validation' },
  behavioral:{ icon: Shield, label: 'Behavioral Analysis' },
  carrier:   { icon: Package, label: 'Carrier Validation' },
  graph:     { icon: Network, label: 'Network Analysis' },
};

const SIGNAL_CATEGORY_MAP = {
  'IMAGE': 'image',
  'EXIF': 'image',
  'PRODUCT_MISMATCH': 'image',
  'RECEIPT': 'receipt',
  'BEHAVIORAL': 'behavioral',
  'SHARED_DEVICE': 'behavioral',
  'SHARED_IP': 'behavioral',
  'HIGH_INR': 'behavioral',
  'CARRIER': 'carrier',
  'FRAUD_RING': 'graph',
  'NETWORK': 'graph',
};

export function EvidencePanel({ claim, onDecision }) {
  const [activeTab, setActiveTab] = useState('overview');

  const tierColors = {
    TRUSTED:      '#81C784',
    CAUTION:      '#FFF176',
    ELEVATED_RISK:'#FFB74D',
    HIGH_RISK:    '#E57373',
  };

  const computedSubScores = { image: 0, receipt: 0, behavioral: 0, carrier: 0, graph: 0 };
  
  if (claim?.evidence) {
    claim.evidence.forEach(ev => {
      const type = ev.signal || ev.type || '';
      const points = ev.points || ev.score_added || 0;
      
      let category = 'behavioral'; // fallback
      for (const [key, val] of Object.entries(SIGNAL_CATEGORY_MAP)) {
        if (type.includes(key)) {
          category = val;
          break;
        }
      }
      computedSubScores[category] += points;
    });
  }

  const finalSubScores = claim?.sub_scores || computedSubScores;

  return (
    <div style={{
      background: '#1A1C20', // Clean dark grey background
      border: '1px solid #2A2D35',
      borderRadius: 12,
      padding: 24,
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      gap: 20,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      color: '#E0E0E0'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ color: '#88909D', fontSize: 12, fontWeight: 600, letterSpacing: 0.5, marginBottom: 4 }}>
            Claim Evidence Review
          </div>
          <div style={{ color: '#FFFFFF', fontSize: 16, fontWeight: 500 }}>
            {claim?.account_id ? `CUS-${claim.account_id.slice(0,4)}...${claim.account_id.slice(-4)}` : 'Unknown Account'}
          </div>
        </div>
        
        {/* Modern Flat Score Meter */}
        <div style={{ position: 'relative', width: 64, height: 64 }}>
          <svg width={64} height={64} viewBox="0 0 64 64">
            <circle cx={32} cy={32} r={28} fill="none" 
              stroke="#2A2D35" strokeWidth={5} />
            <circle cx={32} cy={32} r={28} fill="none"
              stroke={tierColors[claim?.fraud_tier] || '#81C784'} strokeWidth={5}
              strokeDasharray={`${(claim?.fraud_score / 100) * 175.9} 175.9`}
              strokeLinecap="round"
              transform="rotate(-90 32 32)" />
          </svg>
          <div style={{
            position: 'absolute', inset: 0, display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            flexDirection: 'column'
          }}>
            <span style={{ color: '#FFFFFF', fontSize: 16, fontWeight: 600 }}>
              {claim?.fraud_score || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Sub-scores */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10 }}>
        {Object.entries(CATEGORY_ICONS).map(([key, { icon: Icon, label }]) => (
          <div key={key} style={{
            background: '#202329',
            border: '1px solid #2A2D35',
            borderRadius: 8, padding: '12px 8px', textAlign: 'center'
          }}>
            <Icon size={16} color="#88909D" style={{ marginBottom: 6 }} />
            <div style={{ color: '#FFFFFF', fontSize: 14, fontWeight: 600, marginBottom: 4 }}>
              +{finalSubScores[key] || 0}
            </div>
            <div style={{ color: '#88909D', fontSize: 10, lineHeight: 1.2 }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Visual Image Comparison */}
      {(claim?.expected_product_image || claim?.captured_image_base64) && (
        <div style={{ background: '#202329', border: '1px solid #2A2D35', borderRadius: 8, padding: 16 }}>
          <div style={{ color: '#88909D', fontSize: 12, fontWeight: 600, marginBottom: 12 }}>
            Visual Inspection
          </div>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
            {claim?.expected_product_image && (
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 11, color: '#88909D', marginBottom: 8, textTransform: 'uppercase' }}>Expected Item</div>
                <img src={claim.expected_product_image} alt="Expected" style={{ width: '100%', height: 140, objectFit: 'cover', borderRadius: 6, border: '1px solid #2A2D35' }} />
              </div>
            )}
            {claim?.captured_image_base64 && (
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 11, color: '#88909D', marginBottom: 8, textTransform: 'uppercase' }}>Returned Item</div>
                <img src={claim.captured_image_base64} alt="Returned" style={{ width: '100%', height: 140, objectFit: 'cover', borderRadius: 6, border: '1px solid #2A2D35' }} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Evidence List */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ color: '#88909D', fontSize: 12, fontWeight: 600, marginTop: 4 }}>
          Evidence Log
        </div>
        {claim?.evidence?.map((ev, i) => {
          const type = ev.signal || ev.type || 'UNKNOWN_SIGNAL';
          const points = ev.points || ev.score_added || 0;
          let severity = ev.severity;
          if (!severity) {
             if (points >= 30) severity = 'CRITICAL';
             else if (points >= 20) severity = 'HIGH';
             else if (points >= 10) severity = 'MEDIUM';
             else severity = 'LOW';
          }
          const style = SEVERITY_STYLES[severity] || SEVERITY_STYLES.LOW;
          const Icon = style.icon;
          return (
            <div key={i} style={{
              background: style.bg,
              border: `1px solid ${style.border}`,
              borderRadius: 8, padding: '12px 16px',
              display: 'flex', gap: 12, alignItems: 'flex-start'
            }}>
              <Icon size={16} color={style.color} style={{ marginTop: 2, flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <span style={{ color: style.color, fontSize: 13, fontWeight: 600 }}>{type}</span>
                  <span style={{ color: style.color, fontSize: 12, fontWeight: 500, background: `${style.color}20`, padding: '2px 6px', borderRadius: 4 }}>+{points} pts</span>
                </div>
                <div style={{ color: '#B0B5BF', fontSize: 13, lineHeight: 1.4 }}>{ev.detail}</div>
              </div>
            </div>
          );
        })}
        
        {(!claim?.evidence || claim.evidence.length === 0) && (
          <div style={{ color: '#88909D', textAlign: 'center', padding: 32, background: '#202329', borderRadius: 8, border: '1px dashed #2A2D35' }}>
            <CheckCircle size={24} color="#81C784" style={{ marginBottom: 12, marginInline: 'auto' }} />
            <div style={{ fontSize: 14 }}>No fraud signals detected</div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: 12, marginTop: 'auto' }}>
        <button onClick={() => onDecision('APPROVE')} style={{
          flex: 1, padding: '12px 0',
          background: '#2E4C3E', border: '1px solid #3A6350',
          borderRadius: 6, color: '#A5D6B7', cursor: 'pointer',
          fontWeight: 600, fontSize: 13,
          transition: 'all 0.2s'
        }}>
          Approve
        </button>
        <button onClick={() => onDecision('REQUEST_INFO')} style={{
          flex: 1, padding: '12px 0',
          background: '#4A3E26', border: '1px solid #635334',
          borderRadius: 6, color: '#FFE082', cursor: 'pointer',
          fontWeight: 600, fontSize: 13
        }}>
          Request Info
        </button>
        <button onClick={() => onDecision('ESCALATE')} style={{
          flex: 1, padding: '12px 0',
          background: '#5C2D2D', border: '1px solid #7D3B3B',
          borderRadius: 6, color: '#EF9A9A', cursor: 'pointer',
          fontWeight: 600, fontSize: 13
        }}>
          Escalate
        </button>
      </div>
    </div>
  );
}
