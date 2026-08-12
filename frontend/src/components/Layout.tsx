import { NavLink } from 'react-router-dom'
import { LensMark } from './LensMark'

const links = [
  { to: '/', label: 'Home' },
  { to: '/verify', label: 'Verify' },
  { to: '/history', label: 'History' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/admin', label: 'Admin' },
  { to: '/about', label: 'Method' },
]

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-40 border-b border-[var(--line)]/70 bg-[var(--panel)]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3.5">
          <NavLink
            to="/"
            className="group flex items-center gap-2.5 text-[var(--accent)]"
          >
            <span className="relative grid h-9 w-9 place-items-center rounded-full border border-[var(--accent)]/30 bg-[var(--accent)]/5">
              <span className="pointer-events-none absolute inset-0 rounded-full border border-[var(--accent-2)]/40 pulse-ring" />
              <LensMark className="h-5 w-5" />
            </span>
            <span className="brand text-xl tracking-tight md:text-2xl">
              TruthLens AI
            </span>
          </NavLink>
          <nav className="flex flex-wrap items-center gap-1 text-sm font-semibold text-[var(--muted)]">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-1.5 transition ${
                    isActive
                      ? 'bg-[var(--ink)] text-[var(--panel)]'
                      : 'hover:bg-[var(--accent)]/10 hover:text-[var(--ink)]'
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8 md:py-12">{children}</main>
    </div>
  )
}
