export function AboutPage() {
  return (
    <section className="prose-like max-w-3xl space-y-4">
      <h1 className="brand text-3xl md:text-4xl">Method & limits</h1>
      <p className="text-[var(--muted)]">
        TruthLens AI separates <strong>source reliability</strong>,{' '}
        <strong>claim credibility</strong>, and <strong>AI confidence</strong>. Gemini
        contributes structured reasoning; backend engines own scores, risk, and actions.
      </p>
      <ul className="list-disc space-y-2 pl-5 text-sm text-[var(--muted)]">
        <li>OCR extracts text from images — it does not prove authenticity.</li>
        <li>Evidence may be insufficient; the system will say so instead of guessing.</li>
        <li>Scoring formulas are documented heuristics pending formal evaluation.</li>
        <li>We do not claim absolute determination of online truth.</li>
      </ul>
      <p className="text-sm text-[var(--muted)]">
        See repository docs: <code>docs/pipeline.md</code>, <code>docs/scoring.md</code>,{' '}
        <code>docs/research.md</code>.
      </p>
    </section>
  )
}
