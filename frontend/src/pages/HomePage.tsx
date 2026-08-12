import { Link } from 'react-router-dom'
import { LensMark } from '../components/LensMark'

export function HomePage() {
  return (
    <>
      <section className="relative min-h-[78vh] overflow-hidden pb-16 pt-8 md:pb-24 md:pt-14">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 -z-10"
        >
          <div className="absolute left-1/2 top-8 h-[34rem] w-[34rem] -translate-x-1/2 rounded-full border border-[var(--accent)]/25 lens-spin" />
          <div className="absolute left-1/2 top-24 h-[22rem] w-[22rem] -translate-x-1/2 rounded-full border border-[var(--accent-2)]/35" />
          <div className="absolute left-1/2 top-40 h-[10rem] w-[10rem] -translate-x-1/2 rounded-full bg-[var(--accent)]/10 blur-2xl" />
        </div>

        <div className="relative mx-auto max-w-4xl text-center">
          <div className="mx-auto mb-6 grid h-16 w-16 place-items-center rounded-full border border-[var(--accent)]/30 bg-[var(--panel)]/70 text-[var(--accent)] motion-fade">
            <LensMark className="h-9 w-9" spinning />
          </div>
          <h1 className="brand text-6xl leading-[0.95] text-[var(--ink)] md:text-8xl motion-rise">
            TruthLens AI
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-[var(--muted)] md:text-xl motion-rise-delayed">
            Look through evidence — not a single Fake/Real label. Credibility,
            confidence, and risk stay separate by design.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-3 motion-rise-delayed">
            <Link
              to="/verify"
              className="rounded-xl bg-[var(--ink)] px-6 py-3.5 text-sm font-bold text-[var(--panel)] transition hover:-translate-y-0.5 hover:bg-[var(--accent)]"
            >
              Start verification
            </Link>
            <Link
              to="/about"
              className="rounded-xl border border-[var(--line)] bg-[var(--panel)]/80 px-6 py-3.5 text-sm font-bold transition hover:border-[var(--accent)]"
            >
              Why three metrics
            </Link>
          </div>
        </div>
      </section>

      <section className="border-t border-[var(--line)]/80 pt-14">
        <h2 className="brand text-3xl md:text-4xl">Built to stand out in viva</h2>
        <p className="mt-3 max-w-2xl text-[var(--muted)]">
          Backend engines own the decision. Gemini only reasons over retrieved
          evidence in structured JSON.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {[
            {
              kicker: '01',
              title: 'Evidence before verdict',
              body: 'Claim-aware retrieval + long Wikipedia extracts. No invented URLs.',
            },
            {
              kicker: '02',
              title: 'Three separate meters',
              body: 'Credibility ≠ confidence ≠ risk — so “sounds sure” never means “is true.”',
            },
            {
              kicker: '03',
              title: 'Actionable reports',
              body: 'Recommendations, pipeline trace, Plotly analytics, printable PDF.',
            },
          ].map((item) => (
            <article
              key={item.title}
              className="ui-shell ui-interactive rounded-2xl p-5"
            >
              <p className="text-xs font-bold tracking-[0.18em] text-[var(--accent-2)]">
                {item.kicker}
              </p>
              <h3 className="brand mt-3 text-2xl">{item.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">
                {item.body}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="mt-16 border-t border-[var(--line)]/80 pt-14">
        <h2 className="brand text-3xl md:text-4xl">Pipeline</h2>
        <p className="mt-3 max-w-2xl text-[var(--muted)]">
          One auditable path from claim to recommendation.
        </p>
        <ol className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {[
            'Normalize claim',
            'Retrieve & enrich',
            'Gemini JSON',
            'Score engines',
            'Persist + analyze',
          ].map((step, index) => (
            <li
              key={step}
              className="ui-shell ui-interactive rounded-2xl p-4"
              style={{ transitionDelay: `${index * 40}ms` }}
            >
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-[var(--accent)]">
                Step {index + 1}
              </p>
              <p className="mt-2 text-sm font-semibold text-[var(--ink)]">{step}</p>
            </li>
          ))}
        </ol>
      </section>
    </>
  )
}
