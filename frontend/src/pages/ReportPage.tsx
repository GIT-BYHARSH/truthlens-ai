import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../services/api'
import type { VerificationReport } from '../services/api'

function ScoreCard({
  label,
  value,
  hint,
}: {
  label: string
  value: string
  hint: string
}) {
  return (
    <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4">
      <p className="text-xs uppercase tracking-wide text-[var(--muted)]">{label}</p>
      <p className="brand mt-2 text-3xl">{value}</p>
      <p className="mt-1 text-xs text-[var(--muted)]">{hint}</p>
    </div>
  )
}

export function ReportPage() {
  const { id } = useParams()
  const [report, setReport] = useState<VerificationReport | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    api
      .getVerification(id)
      .then(setReport)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Failed to load report')
      })
  }, [id])

  if (error) {
    return <p className="text-[var(--danger)]">{error}</p>
  }
  if (!report) {
    return <p className="text-[var(--muted)]">Loading verification report…</p>
  }

  const supporting = report.evidence.filter((e) => e.evidence_type === 'support')
  const contradicting = report.evidence.filter((e) => e.evidence_type === 'contradict')
  const neutral = report.evidence.filter((e) => e.evidence_type === 'neutral')

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-[var(--accent-2)]">
            Verification report
          </p>
          <h1 className="brand mt-1 text-3xl md:text-4xl">{report.verdict ?? 'PENDING'}</h1>
          <p className="mt-2 max-w-3xl text-[var(--muted)]">{report.claim}</p>
        </div>
        <Link
          to="/verify"
          className="rounded-md border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm font-semibold"
        >
          New verification
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <ScoreCard
          label="Credibility"
          value={report.credibility_score?.toFixed(1) ?? '—'}
          hint="How well-supported the claim appears"
        />
        <ScoreCard
          label="Confidence"
          value={report.confidence_score?.toFixed(1) ?? '—'}
          hint="How sure the system is in this conclusion"
        />
        <ScoreCard
          label="Risk"
          value={report.risk_level ?? '—'}
          hint={report.risk_score != null ? `Score ${report.risk_score.toFixed(1)}/100` : 'Decision risk'}
        />
        <ScoreCard
          label="Category"
          value={report.claim_category ?? 'general'}
          hint={`${report.processing_ms ?? '—'} ms · ${report.input_type}`}
        />
      </div>

      {report.extracted_text && report.input_type === 'image' && (
        <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5">
          <h2 className="brand text-2xl">OCR extracted text</h2>
          <p className="mt-2 text-xs uppercase tracking-wide text-[var(--muted)]">
            EasyOCR extracts text only — it does not prove image authenticity
          </p>
          <p className="mt-3 whitespace-pre-wrap text-sm text-[var(--muted)]">
            {report.extracted_text}
          </p>
        </div>
      )}
        <p className="mt-2 text-[var(--ink)]">{report.recommendation_text}</p>
        {report.recommendation_code && (
          <p className="mt-2 text-xs uppercase tracking-wide text-[var(--muted)]">
            Rule: {report.recommendation_code}
          </p>
        )}
      </div>

      {report.explanation && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5">
            <h2 className="brand text-2xl">Explanation</h2>
            <p className="mt-3 text-sm text-[var(--muted)]">
              {report.explanation.verdict_rationale}
            </p>
            <p className="mt-3 text-sm text-[var(--muted)]">
              {report.explanation.credibility_rationale}
            </p>
            <p className="mt-3 text-sm text-[var(--muted)]">
              {report.explanation.confidence_rationale}
            </p>
          </div>
          <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5">
            <h2 className="brand text-2xl">Uncertainties & sources</h2>
            <p className="mt-3 text-sm text-[var(--muted)]">
              {report.explanation.source_reasoning}
            </p>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-[var(--muted)]">
              {report.explanation.uncertainties.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <EvidenceBlock title="Supporting evidence" items={supporting} />
      <EvidenceBlock title="Contradicting evidence" items={contradicting} />
      <EvidenceBlock title="Contextual evidence" items={neutral} />
    </section>
  )
}

function EvidenceBlock({
  title,
  items,
}: {
  title: string
  items: VerificationReport['evidence']
}) {
  return (
    <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5">
      <h2 className="brand text-2xl">
        {title}{' '}
        <span className="text-base text-[var(--muted)]">({items.length})</span>
      </h2>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-[var(--muted)]">None recorded for this run.</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {items.map((item) => (
            <li
              key={item.id}
              className="rounded-xl border border-[var(--line)] bg-white/70 px-4 py-3"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-medium">{item.title || item.domain || 'Source'}</p>
                <p className="text-xs text-[var(--muted)]">
                  reliability {item.source_reliability_score?.toFixed(0) ?? '—'} · relevance{' '}
                  {item.relevance_score?.toFixed(0) ?? '—'}
                </p>
              </div>
              {item.snippet && (
                <p className="mt-2 text-sm text-[var(--muted)]">{item.snippet}</p>
              )}
              {item.url && (
                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-2 inline-block text-xs font-semibold text-[var(--accent)]"
                >
                  {item.domain || 'Open source'}
                </a>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
