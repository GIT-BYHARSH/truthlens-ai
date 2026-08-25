import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { LensMark } from '../components/LensMark'
import { api } from '../services/api'

const DEMO_CLAIMS = [
  {
    label: 'Supported',
    title: 'Chandrayaan-3',
    text: 'India successfully landed Chandrayaan-3 near the lunar south pole in August 2023.',
  },
  {
    label: 'Refuted',
    title: 'Mumbai capital',
    text: 'The capital of India is Mumbai.',
  },
  {
    label: 'Supported',
    title: 'WHO pandemic',
    text: 'The World Health Organization declared COVID-19 a pandemic in March 2020.',
  },
]

const DEMO_IMAGES = [
  {
    label: 'Refuted',
    title: 'Mumbai OCR',
    src: '/demo/ocr_refuted_mumbai.png',
    filename: 'ocr_refuted_mumbai.png',
  },
  {
    label: 'Supported',
    title: 'Chandrayaan OCR',
    src: '/demo/ocr_supported_chandrayaan.png',
    filename: 'ocr_supported_chandrayaan.png',
  },
]

const LIVE_STEPS = [
  'Validating input',
  'OCR (images) / claim prep',
  'Retrieving evidence',
  'Enriching snippets',
  'Gemini structured reasoning',
  'Scoring credibility / confidence / risk',
  'Writing report',
]

type Tab = 'text' | 'image' | 'url'

export function VerifyPage() {
  const navigate = useNavigate()
  const [tab, setTab] = useState<Tab>('text')
  const [text, setText] = useState('')
  const [url, setUrl] = useState('')
  const [image, setImage] = useState<File | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [liveStep, setLiveStep] = useState(0)
  const [selectedDemo, setSelectedDemo] = useState<string | null>(null)
  const [backendOk, setBackendOk] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    async function check() {
      try {
        await api.health()
        if (!cancelled) setBackendOk(true)
      } catch {
        if (!cancelled) setBackendOk(false)
      }
    }
    void check()
    const id = window.setInterval(check, 12_000)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [])

  useEffect(() => {
    if (!busy) {
      setLiveStep(0)
      return
    }
    const id = window.setInterval(() => {
      setLiveStep((prev) => (prev + 1) % LIVE_STEPS.length)
    }, 1800)
    return () => window.clearInterval(id)
  }, [busy])

  async function pickDemoImage(demo: (typeof DEMO_IMAGES)[number]) {
    setSelectedDemo(demo.title)
    setMessage(`Loading demo image: ${demo.title}…`)
    try {
      const response = await fetch(demo.src)
      if (!response.ok) throw new Error('Demo image missing from frontend/public/demo.')
      const blob = await response.blob()
      const file = new File([blob], demo.filename, { type: blob.type || 'image/png' })
      setImage(file)
      setMessage(`Ready: ${demo.filename}. Click Run verification.`)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Could not load demo image.')
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setMessage(null)
    try {
      if (tab === 'text') {
        setMessage('Running full verification pipeline…')
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
      if (!image) {
        setMessage('Please choose an image file first.')
        return
      }
      setMessage(
        'Running EasyOCR → claim → evidence → report… First OCR load can take 1–2 minutes.',
      )
      const report = await api.verifyImage(image)
      navigate(`/report/${report.id}`)
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : 'Verification request failed.',
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="space-y-8">
      <div className="max-w-2xl">
        <h1 className="brand text-4xl md:text-5xl">Verify</h1>
        <p className="mt-3 text-[var(--muted)]">
          Pick a demo claim or write your own. Watch the live pipeline while the
          engines work.
        </p>
        {backendOk === false && (
          <p className="mt-3 rounded-xl border border-[var(--danger)]/40 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger)]">
            Backend offline. Keep API running on port 8002, then refresh. From
            project root: <code className="font-semibold">.\start-dev.ps1</code>
          </p>
        )}
        {backendOk === true && (
          <p className="mt-3 text-xs font-semibold text-[var(--accent)]">
            Backend connected
          </p>
        )}
      </div>

      <div className="inline-flex rounded-xl border border-[var(--line)] bg-[var(--panel)] p-1">
        {(['text', 'image', 'url'] as Tab[]).map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setTab(item)}
            className={`rounded-lg px-4 py-2 text-sm font-bold capitalize transition ${
              tab === item
                ? 'bg-[var(--ink)] text-[var(--panel)]'
                : 'text-[var(--muted)] hover:text-[var(--ink)]'
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      <form onSubmit={onSubmit} className="space-y-5">
        {tab === 'text' && (
          <>
            <div className="grid gap-3 md:grid-cols-3">
              {DEMO_CLAIMS.map((demo) => {
                const active = selectedDemo === demo.title
                return (
                  <button
                    key={demo.title}
                    type="button"
                    onClick={() => {
                      setSelectedDemo(demo.title)
                      setText(demo.text)
                    }}
                    className={`ui-shell ui-interactive rounded-2xl p-4 text-left ${
                      active ? 'border-[var(--accent)] ring-2 ring-[var(--accent)]/30' : ''
                    }`}
                  >
                    <p
                      className={`text-xs font-bold uppercase tracking-[0.14em] ${
                        demo.label === 'Refuted'
                          ? 'text-[var(--danger)]'
                          : 'text-[var(--accent)]'
                      }`}
                    >
                      Expect {demo.label}
                    </p>
                    <p className="brand mt-2 text-xl">{demo.title}</p>
                    <p className="mt-2 line-clamp-3 text-xs text-[var(--muted)]">
                      {demo.text}
                    </p>
                  </button>
                )
              })}
            </div>
            <textarea
              value={text}
              onChange={(e) => {
                setText(e.target.value)
                setSelectedDemo(null)
              }}
              rows={6}
              placeholder="Paste any claim to verify…"
              className="w-full rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm outline-none ring-[var(--accent)] transition focus:ring-2"
              required
              minLength={8}
            />
          </>
        )}

        {tab === 'url' && (
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/article"
            className="w-full rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm outline-none ring-[var(--accent)] focus:ring-2"
            required
          />
        )}

        {tab === 'image' && (
          <>
            <div className="grid gap-3 md:grid-cols-2">
              {DEMO_IMAGES.map((demo) => {
                const active = selectedDemo === demo.title
                return (
                  <button
                    key={demo.title}
                    type="button"
                    onClick={() => void pickDemoImage(demo)}
                    className={`ui-shell ui-interactive rounded-2xl p-4 text-left ${
                      active ? 'border-[var(--accent)] ring-2 ring-[var(--accent)]/30' : ''
                    }`}
                  >
                    <p
                      className={`text-xs font-bold uppercase tracking-[0.14em] ${
                        demo.label === 'Refuted'
                          ? 'text-[var(--danger)]'
                          : 'text-[var(--accent)]'
                      }`}
                    >
                      Expect {demo.label}
                    </p>
                    <p className="brand mt-2 text-xl">{demo.title}</p>
                    <p className="mt-2 text-xs text-[var(--muted)]">
                      Loads a ready OCR demo image for viva.
                    </p>
                  </button>
                )
              })}
            </div>
            <label className="ui-shell ui-interactive flex cursor-pointer flex-col items-start gap-2 rounded-2xl border-dashed p-6">
              <span className="text-sm font-bold text-[var(--ink)]">
                Drop or choose an image
              </span>
              <span className="text-xs text-[var(--muted)]">
                EasyOCR extracts text only — not authenticity. Prefer clear
                screenshots with readable claim text.
              </span>
              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg,image/webp,image/bmp"
                onChange={(e) => {
                  setImage(e.target.files?.[0] ?? null)
                  setSelectedDemo(null)
                }}
                className="mt-2 block w-full text-sm text-[var(--muted)]"
                required={!image}
              />
              {image && (
                <span className="text-xs font-semibold text-[var(--accent)]">
                  {image.name} ({Math.round(image.size / 1024)} KB)
                </span>
              )}
            </label>
          </>
        )}

        <button
          type="submit"
          disabled={busy}
          className="inline-flex items-center gap-2 rounded-xl bg-[var(--accent)] px-6 py-3.5 text-sm font-bold text-white transition hover:-translate-y-0.5 disabled:opacity-60"
        >
          {busy ? (
            <>
              <LensMark className="h-4 w-4" spinning />
              Verifying…
            </>
          ) : (
            'Run verification'
          )}
        </button>
      </form>

      {busy && (
        <div className="ui-shell rounded-2xl p-5">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-[var(--accent-2)]">
            Live pipeline
          </p>
          <ul className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {LIVE_STEPS.map((step, index) => {
              const active = index === liveStep
              const done = index < liveStep
              return (
                <li
                  key={step}
                  className={`rounded-xl border px-3 py-2 text-sm transition ${
                    active
                      ? 'border-[var(--accent)] bg-[var(--accent)]/10 font-semibold text-[var(--ink)]'
                      : done
                        ? 'border-[var(--accent)]/30 text-[var(--accent)]'
                        : 'border-[var(--line)] text-[var(--muted)]'
                  }`}
                >
                  {done ? '✓ ' : active ? '● ' : `${index + 1}. `}
                  {step}
                </li>
              )
            })}
          </ul>
        </div>
      )}

      {message && (
        <div className="rounded-xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--muted)]">
          {message}
        </div>
      )}
    </section>
  )
}
