declare module 'plotly.js-dist-min' {
  const Plotly: unknown
  export default Plotly
}

declare module 'react-plotly.js/factory' {
  import type { ComponentType } from 'react'

  type PlotParams = {
    data: unknown[]
    layout?: Record<string, unknown>
    config?: Record<string, unknown>
    style?: React.CSSProperties
    useResizeHandler?: boolean
  }

  export default function createPlotlyComponent(
    plotly: unknown,
  ): ComponentType<PlotParams>
}
