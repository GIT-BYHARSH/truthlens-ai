import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { AdminOverview, SystemEvent } from '../services/api'

export function AdminPage() {
  const [overview, setOverview] = useState<AdminOverview | null>(null)
  const [events, setEvents] = useState<SystemEvent[]>([])
  const [error, setError] = useState<string | null>(null)
  const [resetMsg, setResetMsg] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function load() {
    const [o, e] = await Promise.all([api.adminOverview(), api.adminEvents(30)])
    setOverview(o)
    setEvents(e)
  }

  useEffect(() => {
    load().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Admin overview unavailable.')
    })
  }, [])

  async function onDemoReset() {
    const ok = window.confirm(
      'Delete ALL verification history? Use this before a clean viva demo, then re-run the 3 demo claims.',
    )
    if (!ok) return
    setBusy(true)
    setResetMsg(null)
    try {
      const result = await api.adminDemoReset()
      setResetMsg(result.message)
      await load()
    } catch (err: unknown) {
      setResetMsg(err instanceof Error ? err.message : 'Reset failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="brand text-3xl md:text-4xl">Admin monitoring</h1>
          <p className="mt-2 max-w-2xl text-[var(--muted)]">
            System health, event stream, and demo-reset for clean Analytics.
          </p>
        </div>
        <button
          type="button"
          disabled={busy}
          onClick={onDemoReset}
          className="rounded-md border border-[var(--danger)]/40 bg-white px-4 py-2 text-sm font-semibold text-[var(--danger)] disabled:opacity-60"
        >
          {busy ? 'Resetting…' : 'Demo reset (clear history)'}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-[var(--danger)]/30 bg-white px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      )}
      {resetMsg && (
        <div className="rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm text-[var(--muted)]">
          {resetMsg}
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
              <p className="text-xs uppercase tracking-wide text-[var(--muted)]">
                {label}
              </p>
              <p className="brand mt-2 text-3xl">{value}</p>
            </div>
          ))}
        </div>
      )}

      {overview && Object.keys(overview.event_counts).length > 0 && (
        <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5">
          <h2 className="brand text-2xl">Event type counts</h2>
          <ul className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(overview.event_counts)
              .sort((a, b) => b[1] - a[1])
              .map(([type, count]) => (
                <li
                  key={type}
                  className="flex items-center justify-between rounded-lg border border-[var(--line)] bg-white/70 px-3 py-2 text-sm"
                >
                  <span className="text-[var(--muted)]">{type}</span>
                  <span className="font-semibold text-[var(--ink)]">{count}</span>
                </li>
              ))}
          </ul>
        </div>
      )}

      <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5">
        <h2 className="brand text-2xl">Recent system events</h2>
        {events.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--muted)]">No events yet.</p>
        ) : (
          <ul className="mt-4 space-y-2">
            {events.map((event) => (
              <li
                key={event.id}
                className="rounded-xl border border-[var(--line)] bg-white/70 px-4 py-3 text-sm"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-semibold text-[var(--ink)]">
                    {event.event_type}
                  </span>
                  <span className="text-xs text-[var(--muted)]">
                    {new Date(event.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="mt-1 text-[var(--muted)]">{event.message}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
