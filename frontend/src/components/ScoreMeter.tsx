export function ScoreMeter({
  label,
  value,
  max = 100,
  hint,
  tone = 'accent',
  delayMs = 0,
}: {
  label: string
  value: number | null | undefined
  max?: number
  hint: string
  tone?: 'accent' | 'ember' | 'danger' | 'warn'
  delayMs?: number
}) {
  const numeric = value == null || Number.isNaN(value) ? null : Math.max(0, Math.min(max, value))
  const pct = numeric == null ? 0 : (numeric / max) * 100
  const color =
    tone === 'ember'
      ? 'var(--accent-2)'
      : tone === 'danger'
        ? 'var(--danger)'
        : tone === 'warn'
          ? 'var(--warn)'
          : 'var(--accent)'

  return (
    <div className="ui-shell ui-interactive rounded-2xl p-4">
      <div className="flex items-end justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">
          {label}
        </p>
        <p className="brand text-3xl leading-none" style={{ color }}>
          {numeric == null ? '—' : numeric.toFixed(1)}
        </p>
      </div>
      <div className="mt-4 h-2 overflow-hidden rounded-sm bg-[var(--line)]/60">
        <div
          className="meter-fill h-full rounded-sm"
          style={{
            width: `${pct}%`,
            background: color,
            animationDelay: `${delayMs}ms`,
          }}
        />
      </div>
      <p className="mt-2 text-xs text-[var(--muted)]">{hint}</p>
    </div>
  )
}
