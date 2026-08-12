import { Link } from 'react-router-dom'

export function HomePage() {
  return (
    <section className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
      <div className="space-y-6">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--accent-2)]">
          Decision-support verification
        </p>
        <h1 className="brand max-w-3xl text-4xl leading-tight text-[var(--ink)] md:text-6xl">
          TruthLens AI
        </h1>
        <p className="max-w-2xl text-lg leading-relaxed text-[var(--muted)]">
          Verify claims with evidence retrieval, transparent credibility scoring,
          separate confidence estimates, risk assessment, and clear recommended actions —
          not a single fake/real label.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/verify"
            className="rounded-md bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:brightness-110"
          >
            Start verification
          </Link>
          <Link
            to="/about"
            className="rounded-md border border-[var(--line)] bg-[var(--panel)] px-5 py-3 text-sm font-semibold transition hover:border-[var(--accent)]"
          >
            How scoring works
          </Link>
        </div>
      </div>
      <div className="relative overflow-hidden rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-6 shadow-[0_20px_50px_rgba(15,28,23,0.08)]">
        <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)]" />
        <h2 className="brand text-2xl">Pipeline at a glance</h2>
        <ol className="mt-4 space-y-3 text-sm text-[var(--muted)]">
          {[
            'Claim extraction & normalization',
            'Evidence retrieval and ranking',
            'Structured Gemini reasoning',
            'Credibility ≠ Confidence ≠ Risk',
            'Explainable action recommendation',
          ].map((step, index) => (
            <li key={step} className="flex gap-3">
              <span className="font-semibold text-[var(--accent)]">{index + 1}.</span>
              <span>{step}</span>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
