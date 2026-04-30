/**
 * dashboard/src/api.js
 * Centralized API client — all backend calls go through here.
 * Falls back to mock data when the API is unreachable.
 */

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`)
  return res.json()
}

// ── Claims Queue ─────────────────────────────────────────
export async function fetchClaims(tier = 'ALL', limit = 50) {
  const q = tier !== 'ALL' ? `?tier=${tier}&limit=${limit}` : `?limit=${limit}`
  return apiFetch(`/api/v1/claims${q}`)
}

export async function fetchClaim(claimId) {
  return apiFetch(`/api/v1/claims/${claimId}`)
}

// ── Fraud Rings ───────────────────────────────────────────
export async function fetchRings() {
  return apiFetch('/api/v1/rings')
}

// ── Intelligence Center ───────────────────────────────────
export async function fetchKPIs() {
  return apiFetch('/api/v1/dashboard/kpis')
}

export async function fetchGraph() {
  return apiFetch('/api/v1/graph')
}

// ── Model Performance ────────────────────────────────────
export async function fetchMetrics() {
  return apiFetch('/api/v1/metrics')
}

// ── Audit Log ─────────────────────────────────────────────
export async function fetchAuditLog(actorType = 'ALL', limit = 50) {
  const q = actorType !== 'ALL'
    ? `?actor_type=${actorType}&limit=${limit}`
    : `?limit=${limit}`
  return apiFetch(`/api/v1/audit${q}`)
}
