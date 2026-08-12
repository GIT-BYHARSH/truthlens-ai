import { Link } from 'react-router-dom'
import { MetricPlayground } from '../components/MetricPlayground'

export function AboutPage() {
  return (
    <section className="space-y-12">
      <div className="max-w-3xl">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-[var(--accent-2)]">
          Method lab
        </p>
        <h1 className="brand mt-3 text-4xl md:text-6xl">How TruthLens thinks</h1>
        <p className="mt-4 text-lg text-[var(--muted)]">
          Decision support, not a Fake/Real oracle. Gemini structures evidence
          reasoning — backend engines own scores, risk, and actions.
        </p>
      </div>

      <div>
        <h2 className="brand text-3xl">Three meters. Click to explore.</h2>
        <p className="mt-2 max-w-2xl text-[var(--muted)]">
          This is the academic differentiator — one number can never mean both
          “true” and “sure.”
        </p>
        <div className="mt-6">
          <MetricPlayground />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="ui-shell rounded-3xl p-6">
          <h2 className="brand text-2xl">Formulas</h2>
          <pre className="mt-4 overflow-x-auto rounded-2xl bg-[var(--ink)] p-4 text-xs leading-relaxed text-[var(--panel)]">
{`credibility =
  w_s·support + w_r·source + w_a·agreement
  + w_c·consistency − penalties

confidence =
  w_e·coverage + w_q·quality + w_m·model
  + w_v·clarity − uncertainty`}
          </pre>
          <p className="mt-3 text-sm text-[var(--muted)]">
            Transparent heuristics — documented, testable, not claimed as
            scientific truth.
          </p>
        </div>
        <div className="ui-shell rounded-3xl p-6">
          <h2 className="brand text-2xl">Hard limits</h2>
          <ul className="mt-4 space-y-3 text-sm text-[var(--muted)]">
            {[
              'OCR extracts text — never proves image authenticity.',
              'Weak evidence → INSUFFICIENT_EVIDENCE, not a guess.',
              'Gemini cannot invent source URLs.',
              'We do not claim absolute online truth.',
            ].map((item) => (
              <li
                key={item}
                className="border-l-2 border-[var(--accent-2)] pl-3 leading-relaxed"
              >
                {item}
              </li>
            ))}
          </ul>
          <Link
            to="/verify"
            className="mt-6 inline-flex rounded-xl bg-[var(--accent)] px-5 py-3 text-sm font-bold text-white"
          >
            Run a live claim →
          </Link>
        </div>
      </div>
    </section>
  )
}
