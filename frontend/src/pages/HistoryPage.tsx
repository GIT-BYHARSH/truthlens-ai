import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import type { VerificationListItem } from '../services/api'

export function HistoryPage() {
  const [items, setItems] = useState<VerificationListItem[]>([])
  const [total, setTotal] = useState(0)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listVerifications(1)
      .then((data) => {
        setItems(data.items)
        setTotal(data.total)
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Failed to load history')
      })
  }, [])

  return (
    <section className="space-y-4">
      <div>
        <h1 className="brand text-3xl md:text-4xl">Verification history</h1>
        <p className="mt-2 max-w-2xl text-[var(--muted)]">
          Stored verification events from PostgreSQL ({total} total).
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-[var(--danger)]/30 bg-white px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      )}

      {items.length === 0 && !error ? (
        <div className="rounded-2xl border border-dashed border-[var(--line)] bg-[var(--panel)] px-5 py-10 text-center text-sm text-[var(--muted)]">
          No verification records yet. Run one from the Verify page.
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <Link
              key={item.id}
              to={`/report/${item.id}`}
              className="block rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-4 transition hover:border-[var(--accent)]"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-semibold">{item.verdict ?? 'PENDING'}</p>
                <p className="text-xs text-[var(--muted)]">
                  {new Date(item.created_at).toLocaleString()}
                </p>
              </div>
              <p className="mt-2 line-clamp-2 text-sm text-[var(--muted)]">
                {item.claim || 'No claim text'}
              </p>
              <p className="mt-2 text-xs text-[var(--muted)]">
                credibility {item.credibility_score?.toFixed(1) ?? '—'} · confidence{' '}
                {item.confidence_score?.toFixed(1) ?? '—'} · risk {item.risk_level ?? '—'} ·{' '}
                {item.input_type}
              </p>
            </Link>
          ))}
        </div>
      )}
    </section>
  )
}
