import { Link } from 'react-router-dom'

export function AboutPage() {
  return (
    <section className="max-w-3xl space-y-10">
      <div>
        <h1 className="brand text-3xl md:text-4xl">Method & limits</h1>
        <p className="mt-3 text-[var(--muted)]">
          TruthLens AI is a <strong>decision-support</strong> platform. Gemini
          contributes structured multimodal reasoning; backend engines own
          credibility, confidence, risk, and recommended actions.
        </p>
      </div>

      <div>
        <h2 className="brand text-2xl">Why three metrics (not one score)</h2>
        <div className="mt-4 space-y-4 text-sm leading-relaxed text-[var(--muted)]">
          <p>
            <strong className="text-[var(--ink)]">Credibility</strong> — how
            well-supported the claim appears from retrieved evidence (support
            strength, source reliability, agreement, contradictions).
          </p>
          <p>
            <strong className="text-[var(--ink)]">Confidence</strong> — how sure
            the system is in <em>this</em> conclusion (coverage, quality, model
            signal, verdict clarity). High confidence does not mean “true.”
          </p>
          <p>
            <strong className="text-[var(--ink)]">Risk</strong> — potential
            decision risk if someone acted on the report (low credibility under
            high certainty, contradictions, weak sources, sensitive categories).
          </p>
        </div>
        <div className="mt-5 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5">
          <p className="text-xs uppercase tracking-wide text-[var(--accent-2)]">
            Worked example for viva
          </p>
          <p className="mt-2 text-sm text-[var(--muted)]">
            Claim: “The capital of India is Mumbai.” → verdict{' '}
            <strong className="text-[var(--ink)]">REFUTED</strong>. Credibility can
            be low (claim is poorly supported / contradicted) while confidence is
            high (evidence clearly establishes New Delhi). Risk rises because
            sharing the claim would be misleading.
          </p>
        </div>
      </div>

      <div>
        <h2 className="brand text-2xl">Formulas (transparent heuristics)</h2>
        <pre className="mt-3 overflow-x-auto rounded-xl border border-[var(--line)] bg-white/70 p-4 text-xs leading-relaxed text-[var(--ink)]">
{`credibility =
  w_s·support + w_r·source_reliability + w_a·agreement
  + w_c·consistency − w_x·contradiction − w_i·insufficiency

confidence =
  w_e·coverage + w_q·quality + w_m·model_confidence
  + w_v·verdict_clarity − w_u·uncertainty`}
        </pre>
        <p className="mt-3 text-sm text-[var(--muted)]">
          Weights are configurable. These are engineering heuristics pending
          formal evaluation — we do not claim scientific truth measurement.
        </p>
      </div>

      <div>
        <h2 className="brand text-2xl">Hard limits</h2>
        <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-[var(--muted)]">
          <li>OCR extracts text from images — it does not prove authenticity.</li>
          <li>
            Evidence can be insufficient; the system prefers{' '}
            <code>INSUFFICIENT_EVIDENCE</code> over guessing.
          </li>
          <li>Gemini never invents source URLs; only provided evidence is used.</li>
          <li>We do not claim absolute determination of online truth.</li>
        </ul>
      </div>

      <p className="text-sm text-[var(--muted)]">
        Deep dive: <code>docs/pipeline.md</code>, <code>docs/scoring.md</code>,{' '}
        <code>docs/research.md</code>, <code>docs/viva.md</code>.{' '}
        <Link to="/verify" className="font-semibold text-[var(--accent)]">
          Try a verification →
        </Link>
      </p>
    </section>
  )
}
