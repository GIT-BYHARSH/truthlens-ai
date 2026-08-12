import { useState } from 'react'

const METRICS = [
  {
    id: 'cred',
    title: 'Credibility',
    short: 'Support strength',
    color: 'var(--accent)',
    body: 'How well-supported the claim appears from evidence — sources, agreement, contradictions.',
    example: 28,
  },
  {
    id: 'conf',
    title: 'Confidence',
    short: 'Certainty of conclusion',
    color: 'var(--accent-2)',
    body: 'How sure the system is in this verdict — coverage, quality, model signal. High ≠ true.',
    example: 84,
  },
  {
    id: 'risk',
    title: 'Risk',
    short: 'Decision caution',
    color: 'var(--danger)',
    body: 'Potential harm if someone acted on the report — especially low support under high certainty.',
    example: 62,
  },
] as const

export function MetricPlayground() {
  const [active, setActive] = useState<(typeof METRICS)[number]['id']>('cred')
  const current = METRICS.find((m) => m.id === active) ?? METRICS[0]

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {METRICS.map((m) => (
          <button
            key={m.id}
            type="button"
            onClick={() => setActive(m.id)}
            className={`rounded-xl px-4 py-2 text-sm font-bold transition ${
              active === m.id
                ? 'bg-[var(--ink)] text-[var(--panel)]'
                : 'border border-[var(--line)] bg-[var(--panel)] text-[var(--muted)] hover:border-[var(--accent)]'
            }`}
          >
            {m.title}
          </button>
        ))}
      </div>

      <div className="ui-shell overflow-hidden rounded-3xl">
        <div className="grid gap-0 md:grid-cols-[1.1fr_0.9fr]">
          <div className="border-b border-[var(--line)] p-6 md:border-b-0 md:border-r">
            <p
              className="text-xs font-bold uppercase tracking-[0.18em]"
              style={{ color: current.color }}
            >
              {current.short}
            </p>
            <h3 className="brand mt-2 text-3xl">{current.title}</h3>
            <p className="mt-3 text-sm leading-relaxed text-[var(--muted)]">
              {current.body}
            </p>
            <p className="mt-5 text-xs text-[var(--muted)]">
              Interactive viva aid — click each metric to explain the split.
            </p>
          </div>
          <div className="relative bg-[var(--ink)] p-6 text-[var(--panel)]">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-white/55">
              Mumbai capital example
            </p>
            <p className="brand mt-3 text-5xl" style={{ color: current.color }}>
              {current.example}
            </p>
            <p className="mt-2 text-sm text-white/70">
              REFUTED · credibility stays low while confidence can stay high.
            </p>
            <div className="mt-6 space-y-3">
              {METRICS.map((m) => (
                <div key={m.id}>
                  <div className="mb-1 flex justify-between text-xs">
                    <span className="text-white/60">{m.title}</span>
                    <span>{m.example}</span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-sm bg-white/15">
                    <div
                      className="h-full rounded-sm transition-all duration-500"
                      style={{
                        width: `${m.example}%`,
                        background: m.color,
                        opacity: active === m.id ? 1 : 0.35,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
