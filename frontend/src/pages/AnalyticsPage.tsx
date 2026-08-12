import { lazy, Suspense, useEffect, useState } from 'react'
import { api } from '../services/api'
import type { AnalyticsSummary, AnalyticsTrends, Insight } from '../services/api'

const CountsBarChart = lazy(() =>
  import('../components/AnalyticsCharts').then((m) => ({
    default: m.CountsBarChart,
  })),
)
const TrendsChart = lazy(() =>
  import('../components/AnalyticsCharts').then((m) => ({
    default: m.TrendsChart,
  })),
)

export function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [trends, setTrends] = useState<AnalyticsTrends | null>(null)
  const [insights, setInsights] = useState<Insight[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([api.analyticsSummary(), api.insights(), api.analyticsTrends()])
      .then(([s, i, t]) => {
        setSummary(s)
        setInsights(i)
        setTrends(t)
      })
      .catch((err: unknown) => {
        setError(
          err instanceof Error
            ? err.message
            : 'Analytics unavailable (is the API and database running?)',
        )
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <section className="space-y-6">
      <div>
        <h1 className="brand text-3xl md:text-4xl">Analytics</h1>
        <p className="mt-2 max-w-2xl text-[var(--muted)]">
          KPIs and Plotly charts are computed from stored verifications only —
          never fabricated.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-[var(--danger)]/30 bg-white px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      )}

      {loading && !summary && !error && (
        <p className="text-sm text-[var(--muted)]">Loading analytics…</p>
      )}

      {summary && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {[
            ['Total verifications', String(summary.total_verifications)],
            [
              'Avg credibility',
              summary.avg_credibility == null
                ? '—'
                : summary.avg_credibility.toFixed(1),
            ],
            [
              'Avg confidence',
              summary.avg_confidence == null
                ? '—'
                : summary.avg_confidence.toFixed(1),
            ],
            [
              'High-risk share',
              summary.high_risk_share == null
                ? '—'
                : `${(summary.high_risk_share * 100).toFixed(0)}%`,
            ],
            [
              'Insufficient evidence',
              summary.insufficient_evidence_share == null
                ? '—'
                : `${(summary.insufficient_evidence_share * 100).toFixed(0)}%`,
            ],
          ].map(([label, value]) => (
            <div
              key={label}
              className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4"
            >
              <p className="text-xs uppercase tracking-wide text-[var(--muted)]">
                {label}
              </p>
              <p className="brand mt-2 text-3xl">{value}</p>
            </div>
          ))}
        </div>
      )}

      <Suspense
        fallback={
          <p className="text-sm text-[var(--muted)]">Loading charts…</p>
        }
      >
        {summary && (
          <div className="grid gap-4 lg:grid-cols-2">
            <CountsBarChart
              title="Verdict distribution"
              counts={summary.verdict_counts}
            />
            <CountsBarChart title="Risk levels" counts={summary.risk_counts} />
            <CountsBarChart
              title="Input types"
              counts={summary.input_type_counts}
              orientation="h"
            />
            <CountsBarChart
              title="Claim categories"
              counts={summary.category_counts}
              orientation="h"
            />
          </div>
        )}

        {trends && <TrendsChart points={trends.points} />}
      </Suspense>

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
