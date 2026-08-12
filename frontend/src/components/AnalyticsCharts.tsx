import type { ReactNode } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-dist-min'

const Plot = createPlotlyComponent(Plotly)

const COLORS = {
  ink: '#0f1c17',
  muted: '#5c675f',
  accent: '#0f6b4c',
  accent2: '#c45c26',
  line: '#d7d0c3',
  panel: '#fffdf8',
  series: ['#0f6b4c', '#c45c26', '#2f5d8c', '#9a6b12', '#6b4c7a', '#4a7c59'],
}

const baseLayout = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'IBM Plex Sans, Segoe UI, sans-serif', color: COLORS.ink, size: 12 },
  margin: { t: 28, r: 16, b: 48, l: 48 },
  legend: { orientation: 'h' as const, y: 1.12 },
}

type CountsChartProps = {
  title: string
  counts: Record<string, number>
  orientation?: 'v' | 'h'
}

export function CountsBarChart({
  title,
  counts,
  orientation = 'v',
}: CountsChartProps) {
  const labels = Object.keys(counts)
  const values = Object.values(counts)
  if (!labels.length) {
    return <EmptyChart title={title} />
  }

  const data =
    orientation === 'h'
      ? [
          {
            type: 'bar' as const,
            orientation: 'h' as const,
            y: labels,
            x: values,
            marker: { color: COLORS.series.slice(0, labels.length) },
            hovertemplate: '%{y}: %{x}<extra></extra>',
          },
        ]
      : [
          {
            type: 'bar' as const,
            x: labels,
            y: values,
            marker: { color: COLORS.series.slice(0, labels.length) },
            hovertemplate: '%{x}: %{y}<extra></extra>',
          },
        ]

  return (
    <ChartShell title={title}>
      <Plot
        data={data}
        layout={{
          ...baseLayout,
          title: { text: '' },
          xaxis: {
            title: orientation === 'v' ? undefined : 'Count',
            tickangle: orientation === 'v' ? -20 : 0,
            automargin: true,
          },
          yaxis: {
            title: orientation === 'h' ? undefined : 'Count',
            automargin: true,
          },
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: 280 }}
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
          margin: { ...baseLayout.margin, t: 40 },
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
      <div className="mt-2">{children}</div>
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
