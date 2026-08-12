export function CircularMeter({
  label,
  value,
  hint,
  tone = 'accent',
  delayMs = 0,
}: {
  label: string
  value: number | null | undefined
  hint: string
  tone?: 'accent' | 'ember' | 'danger' | 'warn'
  delayMs?: number
}) {
  const numeric =
    value == null || Number.isNaN(value) ? null : Math.max(0, Math.min(100, value))
  const pct = numeric == null ? 0 : numeric
  const color =
    tone === 'ember'
      ? 'var(--accent-2)'
      : tone === 'danger'
        ? 'var(--danger)'
        : tone === 'warn'
          ? 'var(--warn)'
          : 'var(--accent)'
  const r = 42
  const c = 2 * Math.PI * r
  const offset = c - (pct / 100) * c

  return (
    <div className="ui-shell ui-interactive group rounded-3xl p-5">
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-[var(--muted)]">
        {label}
      </p>
      <div className="relative mx-auto mt-4 grid h-36 w-36 place-items-center">
        <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
          <circle
            cx="50"
            cy="50"
            r={r}
            fill="none"
            stroke="var(--line)"
            strokeWidth="8"
            opacity="0.55"
          />
          <circle
            cx="50"
            cy="50"
            r={r}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={c}
            strokeDashoffset={offset}
            className="meter-ring"
            style={{ animationDelay: `${delayMs}ms` }}
          />
        </svg>
        <p className="brand absolute text-3xl" style={{ color }}>
          {numeric == null ? '—' : numeric.toFixed(0)}
        </p>
      </div>
      <p className="mt-2 text-center text-xs text-[var(--muted)]">{hint}</p>
    </div>
  )
}
