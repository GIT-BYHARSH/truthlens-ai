import type { ReactNode } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-dist-min'

const Plot = createPlotlyComponent(Plotly)

const COLORS = {
  ink: '#0f1c17',
  muted: '#5c675f',
  accent: '#0f6b4c',
  accent2: '#c45c26',
  series: ['#0f6b4c', '#c45c26', '#2f5d8c', '#9a6b12', '#6b4c7a', '#4a7c59'],
}

const LABEL_MAP: Record<string, string> = {
  SUPPORTED: 'Supported',
  REFUTED: 'Refuted',
  PARTIALLY_SUPPORTED: 'Partial',
  INSUFFICIENT_EVIDENCE: 'Insufficient',
  UNVERIFIED: 'Unverified',
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
  CRITICAL: 'Critical',
  text: 'Text',
  url: 'URL',
  image: 'Image',
}

const VERDICT_COLORS: Record<string, string> = {
  SUPPORTED: '#0f6b4c',
  REFUTED: '#9b2c2c',
  PARTIALLY_SUPPORTED: '#9a6b12',
  INSUFFICIENT_EVIDENCE: '#c45c26',
  UNVERIFIED: '#5c675f',
}

const RISK_COLORS: Record<string, string> = {
  LOW: '#0f6b4c',
  MEDIUM: '#9a6b12',
  HIGH: '#c45c26',
  CRITICAL: '#9b2c2c',
}

const baseLayout = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'IBM Plex Sans, Segoe UI, sans-serif', color: COLORS.ink, size: 12 },
  margin: { t: 12, r: 24, b: 24, l: 96 },
}

function prettyLabel(raw: string): string {
  return LABEL_MAP[raw] ?? raw.replaceAll('_', ' ').toLowerCase()
}

function sortedEntries(counts: Record<string, number>): [string, number][] {
  return Object.entries(counts).sort((a, b) => b[1] - a[1])
}

type CountsChartProps = {
  title: string
  counts: Record<string, number>
  colorMode?: 'verdict' | 'risk' | 'default'
}

export function CountsBarChart({
  title,
  counts,
  colorMode = 'default',
}: CountsChartProps) {
  const entries = sortedEntries(counts)
  if (!entries.length) {
    return <EmptyChart title={title} />
  }

  const keys = entries.map(([k]) => k)
  const labels = keys.map(prettyLabel)
  const values = entries.map(([, v]) => v)
  const colors = keys.map((key, idx) => {
    if (colorMode === 'verdict') return VERDICT_COLORS[key] ?? COLORS.series[idx % COLORS.series.length]
    if (colorMode === 'risk') return RISK_COLORS[key] ?? COLORS.series[idx % COLORS.series.length]
    return COLORS.series[idx % COLORS.series.length]
  })

  const height = Math.max(260, 56 + entries.length * 42)

  return (
    <ChartShell title={title}>
      <Plot
        data={[
          {
            type: 'bar',
            orientation: 'h',
            y: labels,
            x: values,
            text: values.map(String),
            textposition: 'outside',
            cliponaxis: false,
            marker: { color: colors },
            hovertemplate: '%{y}: %{x}<extra></extra>',
          },
        ]}
        layout={{
          ...baseLayout,
          height,
          yaxis: {
            automargin: true,
            categoryorder: 'array',
            categoryarray: labels.slice().reverse(),
          },
          xaxis: {
            title: 'Count',
            rangemode: 'tozero',
            automargin: true,
            // room for outside bar labels
            range: [0, Math.max(...values) * 1.18],
          },
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height }}
        useResizeHandler
      />
    </ChartShell>
  )
}

type TrendPoint = {
  day: string | null
  count: number
  avg_credibility: number | null
  avg_confidence: number | null
}

export function TrendsChart({ points }: { points: TrendPoint[] }) {
  if (!points.length) {
    return <EmptyChart title="Daily verification volume" />
  }

  const days = points.map((p) => (p.day ? p.day.slice(0, 10) : 'unknown'))
  const counts = points.map((p) => p.count)
  const cred = points.map((p) => p.avg_credibility)
  const conf = points.map((p) => p.avg_confidence)

  return (
    <ChartShell title="Daily volume and score means">
      <Plot
        data={[
          {
            type: 'bar',
            name: 'Verifications',
            x: days,
            y: counts,
            marker: { color: COLORS.accent },
            yaxis: 'y',
            hovertemplate: '%{x}<br>Count: %{y}<extra></extra>',
          },
          {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Avg credibility',
            x: days,
            y: cred,
            line: { color: COLORS.accent2, width: 2 },
            yaxis: 'y2',
            hovertemplate: '%{x}<br>Credibility: %{y:.1f}<extra></extra>',
          },
          {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Avg confidence',
            x: days,
            y: conf,
            line: { color: '#2f5d8c', width: 2, dash: 'dot' },
            yaxis: 'y2',
            hovertemplate: '%{x}<br>Confidence: %{y:.1f}<extra></extra>',
          },
        ]}
        layout={{
          ...baseLayout,
          margin: { t: 40, r: 48, b: 48, l: 48 },
          height: 320,
          legend: { orientation: 'h', y: 1.14 },
          yaxis: { title: 'Count', rangemode: 'tozero' },
          yaxis2: {
            title: 'Score',
            overlaying: 'y',
            side: 'right',
            range: [0, 100],
            showgrid: false,
          },
          xaxis: { automargin: true },
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: 320 }}
        useResizeHandler
      />
    </ChartShell>
  )
}

function ChartShell({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4">
      <h2 className="brand text-xl">{title}</h2>
      <div className="mt-2 min-h-[240px]">{children}</div>
    </div>
  )
}

function EmptyChart({ title }: { title: string }) {
  return (
    <ChartShell title={title}>
      <p className="py-10 text-center text-sm text-[var(--muted)]">
        No data yet for this chart.
      </p>
    </ChartShell>
  )
}
