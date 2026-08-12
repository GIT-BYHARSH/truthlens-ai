import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'

type Tab = 'text' | 'image' | 'url'

export function VerifyPage() {
  const navigate = useNavigate()
  const [tab, setTab] = useState<Tab>('text')
  const [text, setText] = useState('')
  const [url, setUrl] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setMessage(null)
    try {
      if (tab === 'text') {
        setMessage('Running pipeline: claim → evidence → Gemini → scores → report…')
        const report = await api.verifyText(text.trim())
        navigate(`/report/${report.id}`)
        return
      }
      if (tab === 'url') {
        setMessage('Fetching URL and verifying…')
        const report = await api.verifyUrl(url.trim())
        navigate(`/report/${report.id}`)
        return
      }
      setMessage('Image + EasyOCR verification is scheduled for Phase 3.')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Verification request failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="brand text-3xl md:text-4xl">Verify information</h1>
        <p className="mt-2 max-w-2xl text-[var(--muted)]">
          Submit a claim. TruthLens retrieves evidence, runs structured Gemini reasoning,
          then computes credibility, confidence, risk, and a recommended action.
        </p>
      </div>

      <div className="flex gap-2">
        {(['text', 'image', 'url'] as Tab[]).map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setTab(item)}
            className={`rounded-md px-4 py-2 text-sm font-semibold capitalize ${
              tab === item
                ? 'bg-[var(--accent)] text-white'
                : 'border border-[var(--line)] bg-[var(--panel)]'
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      <form
        onSubmit={onSubmit}
        className="space-y-4 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm"
      >
        {tab === 'text' && (
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={7}
            placeholder='Example: "Company X has announced that it will stop hiring in 2026."'
            className="w-full rounded-lg border border-[var(--line)] bg-white px-3 py-3 text-sm outline-none ring-[var(--accent)] focus:ring-2"
            required
            minLength={8}
          />
        )}
        {tab === 'url' && (
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/article"
            className="w-full rounded-lg border border-[var(--line)] bg-white px-3 py-3 text-sm outline-none ring-[var(--accent)] focus:ring-2"
            required
          />
        )}
        {tab === 'image' && (
          <input
            type="file"
            accept="image/*"
            className="block w-full text-sm text-[var(--muted)]"
          />
        )}
        <button
          type="submit"
          disabled={busy}
          className="rounded-md bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
        >
          {busy ? 'Verifying…' : 'Run verification'}
        </button>
      </form>

      {message && (
        <div className="rounded-xl border border-[var(--line)] bg-white/80 px-4 py-3 text-sm text-[var(--muted)]">
          {message}
        </div>
      )}
    </section>
  )
}
