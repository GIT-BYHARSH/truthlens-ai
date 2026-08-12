import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { AnalyticsSummary, Insight } from '../services/api'

export function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [insights, setInsights] = useState<Insight[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.analyticsSummary(), api.insights()])
      .then(([s, i]) => {
        setSummary(s)
        setInsights(i)
      })
      .catch((err: unknown) => {
        setError(
          err instanceof Error
            ? err.message
            : 'Analytics unavailable (is the API and database running?)',
        )
      })
  }, [])

  return (
    <section className="space-y-6">
      <div>
        <h1 className="brand text-3xl md:text-4xl">Analytics</h1>
        <p className="mt-2 max-w-2xl text-[var(--muted)]">
          KPIs and insights are computed from stored verifications only — never fabricated.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-[var(--danger)]/30 bg-white px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      )}

      {summary && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            ['Total verifications', String(summary.total_verifications)],
            [
              'Avg credibility',
              summary.avg_credibility == null ? '—' : summary.avg_credibility.toFixed(1),
            ],
            [
              'Avg confidence',
              summary.avg_confidence == null ? '—' : summary.avg_confidence.toFixed(1),
            ],
            [
              'High-risk share',
              summary.high_risk_share == null
                ? '—'
                : `${(summary.high_risk_share * 100).toFixed(0)}%`,
            ],
          ].map(([label, value]) => (
            <div
              key={label}
              className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4"
            >
              <p className="text-xs uppercase tracking-wide text-[var(--muted)]">{label}</p>
              <p className="brand mt-2 text-3xl">{value}</p>
            </div>
          ))}
        </div>
      )}

      <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5">
        <h2 className="brand text-2xl">Insights</h2>
        <ul className="mt-3 space-y-2 text-sm text-[var(--muted)]">
          {insights.map((insight) => (
            <li key={insight.code}>• {insight.message}</li>
          ))}
        </ul>
      </div>
    </section>
  )
}
