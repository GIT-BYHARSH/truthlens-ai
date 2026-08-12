export function LensMark({
  className = '',
  spinning = false,
}: {
  className?: string
  spinning?: boolean
}) {
  return (
    <svg
      viewBox="0 0 64 64"
      className={`${spinning ? 'lens-spin' : ''} ${className}`}
      aria-hidden
    >
      <circle
        cx="32"
        cy="32"
        r="26"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        opacity="0.9"
      />
      <circle
        cx="32"
        cy="32"
        r="14"
        fill="none"
        stroke="var(--accent-2)"
        strokeWidth="2"
      />
      <circle cx="32" cy="32" r="3.5" fill="currentColor" />
      <path
        d="M46 46L56 56"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  )
}
