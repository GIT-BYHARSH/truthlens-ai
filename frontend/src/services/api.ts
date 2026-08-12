const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export type Health = {
  status: string
  app: string
  version: string
  evidence_provider: string
  gemini_configured: boolean
}

export type AnalyticsSummary = {
  total_verifications: number
  avg_credibility: number | null
  avg_confidence: number | null
  high_risk_share: number | null
  insufficient_evidence_share: number | null
  verdict_counts: Record<string, number>
  input_type_counts: Record<string, number>
  risk_counts: Record<string, number>
  category_counts: Record<string, number>
}

export type Insight = { code: string; message: string }

export type TrendPoint = {
  day: string | null
  count: number
  avg_credibility: number | null
  avg_confidence: number | null
}

export type AnalyticsTrends = {
  points: TrendPoint[]
}

export type AdminOverview = {
  total_verifications: number
  completed: number
  failed: number
  recent_failures: number
  event_counts: Record<string, number>
}

export type EvidenceItem = {
  id: string
  url: string | null
  title: string | null
  domain: string | null
  evidence_type: 'support' | 'contradict' | 'neutral'
  relevance_score: number | null
  snippet: string | null
  source_reliability_score: number | null
  rank_position: number | null
}

export type Explanation = {
  claim_summary: string
  verdict_rationale: string
  key_evidence: string[]
  supporting_points: string[]
  contradicting_points: string[]
  source_reasoning: string
  uncertainties: string[]
  credibility_rationale: string
  confidence_rationale: string
  recommended_action: string
}

export type VerificationReport = {
  id: string
  input_type: string
  extracted_text: string | null
  claim: string | null
  claim_category: string | null
  verdict: string | null
  credibility_score: number | null
  confidence_score: number | null
  risk_level: string | null
  risk_score: number | null
  recommendation_code: string | null
  recommendation_text: string | null
  explanation: Explanation | null
  evidence: EvidenceItem[]
  pipeline_status: string
  processing_ms: number | null
  created_at: string
}

export type VerificationListItem = {
  id: string
  input_type: string
  claim: string | null
  verdict: string | null
  credibility_score: number | null
  confidence_score: number | null
  risk_level: string | null
  pipeline_status: string
  created_at: string
}

export type PaginatedVerifications = {
  items: VerificationListItem[]
  total: number
  page: number
  page_size: number
}

export const api = {
  health: () => request<Health>('/health'),
  analyticsSummary: () => request<AnalyticsSummary>('/analytics/summary'),
  insights: () => request<Insight[]>('/analytics/insights'),
  analyticsTrends: () => request<AnalyticsTrends>('/analytics/trends'),
  adminOverview: () => request<AdminOverview>('/admin/overview'),
  verifyText: (text: string, sessionId?: string) =>
    request<VerificationReport>('/verify/text', {
      method: 'POST',
      body: JSON.stringify({ text, session_id: sessionId ?? null }),
    }),
  verifyUrl: (url: string, sessionId?: string) =>
    request<VerificationReport>('/verify/url', {
      method: 'POST',
      body: JSON.stringify({ url, session_id: sessionId ?? null }),
    }),
  verifyImage: async (file: File, sessionId?: string) => {
    const form = new FormData()
    form.append('file', file)
    if (sessionId) form.append('session_id', sessionId)
    const response = await fetch(`${API_BASE}/verify/image`, {
      method: 'POST',
      body: form,
    })
    if (!response.ok) {
      const detail = await response.text()
      throw new Error(detail || `Request failed (${response.status})`)
    }
    return response.json() as Promise<VerificationReport>
  },
  listVerifications: (page = 1) =>
    request<PaginatedVerifications>(`/verifications?page=${page}&page_size=20`),
  getVerification: (id: string) =>
    request<VerificationReport>(`/verifications/${id}`),
}
