import { Link } from 'react-router-dom'

export function HomePage() {
  return (
    <>
      <section className="relative overflow-hidden pb-16 pt-6 md:pb-24 md:pt-10">
        <div
          aria-hidden
          className="pointer-events-none absolute -left-24 top-0 h-72 w-72 rounded-full bg-[var(--accent)]/15 blur-3xl motion-fade"
        />
        <div
          aria-hidden
          className="pointer-events-none absolute -right-16 top-10 h-80 w-80 rounded-full bg-[var(--accent-2)]/15 blur-3xl motion-fade-delayed"
        />
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--accent-2)] motion-rise">
          Explainable multimodal verification
        </p>
        <h1 className="brand mt-4 max-w-4xl text-5xl leading-[1.05] text-[var(--ink)] md:text-7xl motion-rise-delayed">
          TruthLens AI
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-relaxed text-[var(--muted)] motion-rise-delayed">
          Evidence-first decision support — credibility, confidence, and risk stay
          separate so you never confuse “sounds sure” with “is well supported.”
        </p>
        <div className="mt-8 flex flex-wrap gap-3 motion-rise-delayed">
          <Link
            to="/verify"
            className="rounded-md bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white transition hover:brightness-110"
          >
            Start verification
          </Link>
          <Link
            to="/about"
            className="rounded-md border border-[var(--line)] bg-[var(--panel)]/80 px-5 py-3 text-sm font-semibold transition hover:border-[var(--accent)]"
          >
            Why three metrics
          </Link>
        </div>
      </section>

      <section className="border-t border-[var(--line)]/80 pt-12">
        <h2 className="brand text-3xl">What faculty should notice</h2>
        <p className="mt-2 max-w-2xl text-[var(--muted)]">
          Not another Input → AI → Fake/Real wrapper. Backend engines own scores,
          risk, and actions; Gemini only returns structured reasoning over retrieved
          evidence.
        </p>
        <div className="mt-8 grid gap-8 md:grid-cols-3">
          {[
            {
              title: 'Evidence before verdict',
              body: 'Search + Wikipedia enrichment ranked by claim overlap — Gemini cannot invent URLs.',
            },
            {
              title: 'Credibility ≠ Confidence ≠ Risk',
              body: 'Three deterministic formulas. A claim can be weakly supported while the system is highly sure of that conclusion.',
            },
            {
              title: 'Actionable, not absolute',
              body: 'Rule-based recommendations, history, Plotly analytics, and admin monitoring for decision support.',
            },
          ].map((item) => (
            <div key={item.title}>
              <h3 className="brand text-xl text-[var(--accent)]">{item.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">
                {item.body}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-14 border-t border-[var(--line)]/80 pt-12">
        <h2 className="brand text-3xl">Pipeline</h2>
        <p className="mt-2 max-w-2xl text-[var(--muted)]">
          One auditable path from claim to recommendation.
        </p>
        <ol className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {[
            'Normalize claim',
            'Retrieve & enrich evidence',
            'Structured Gemini JSON',
            'Score / risk / action engines',
            'Persist report + analytics',
          ].map((step, index) => (
            <li key={step} className="border-l-2 border-[var(--accent)] pl-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--accent-2)]">
                Step {index + 1}
              </p>
              <p className="mt-1 text-sm font-medium text-[var(--ink)]">{step}</p>
            </li>
          ))}
        </ol>
      </section>
    </>
  )
}
