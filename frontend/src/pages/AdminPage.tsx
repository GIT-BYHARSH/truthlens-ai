import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { AdminOverview } from '../services/api'

export function AdminPage() {
  const [overview, setOverview] = useState<AdminOverview | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .adminOverview()
      .then(setOverview)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Admin overview unavailable.')
      })
  }, [])

  return (
    <section className="space-y-6">
      <div>
        <h1 className="brand text-3xl md:text-4xl">Admin monitoring</h1>
        <p className="mt-2 max-w-2xl text-[var(--muted)]">
          System health signals for verification volume, failures, and event types.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-[var(--danger)]/30 bg-white px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      )}

      {overview && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            ['Total requests', overview.total_verifications],
            ['Completed', overview.completed],
            ['Failed', overview.failed],
            ['Failures (24h)', overview.recent_failures],
          ].map(([label, value]) => (
            <div
              key={String(label)}
              className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4"
            >
              <p className="text-xs uppercase tracking-wide text-[var(--muted)]">{label}</p>
              <p className="brand mt-2 text-3xl">{value}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
