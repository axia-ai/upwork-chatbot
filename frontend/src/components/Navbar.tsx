import { NorthStar } from './Topo'
import { MOCK_USER } from '../data/mock'

type View = 'shop' | 'help'

export function Navbar({
  view,
  onNavigate,
  openTickets,
}: {
  view: View
  onNavigate: (v: View) => void
  openTickets: number
}) {
  return (
    <header className="sticky top-0 z-30">
      {/* Utility bar */}
      <div className="bg-spruce text-bone/90">
        <div className="mx-auto max-w-6xl px-5 py-1.5 text-center sm:px-8">
          <p className="eyebrow text-[0.65rem] text-bone/80">
            Free shipping over $150 · 90-day trail guarantee
          </p>
        </div>
      </div>

      {/* Main bar */}
      <div className="border-b border-ink/12 bg-paper/90 backdrop-blur-md">
        <div className="mx-auto flex h-[4.5rem] max-w-6xl items-center justify-between px-5 sm:px-8">
          <button onClick={() => onNavigate('shop')} className="flex items-center gap-3">
            <span className="text-spruce">
              <NorthStar className="h-7 w-7" />
            </span>
            <span className="text-left leading-none">
              <span className="block font-display text-[1.4rem] font-semibold tracking-tight text-spruce">
                North Star
              </span>
              <span className="eyebrow mt-0.5 block text-[0.6rem] text-stone">
                Outfitters · est. 1971
              </span>
            </span>
          </button>

          <nav className="hidden items-center gap-9 text-[0.95rem] font-medium text-ink/75 md:flex">
            <a className="transition-colors hover:text-spruce" href="#shop">Shop</a>
            <a className="transition-colors hover:text-spruce" href="#field">Field Journal</a>
            <a className="transition-colors hover:text-spruce" href="#about">Our Story</a>
          </nav>

          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate('help')}
              className={`group flex items-center gap-2 border px-3.5 py-2 text-[0.8rem] font-semibold transition-colors ${
                view === 'help'
                  ? 'border-spruce bg-spruce text-bone'
                  : 'border-ink/15 text-spruce hover:border-spruce'
              }`}
            >
              <span className="eyebrow text-[0.68rem]">Support</span>
              {openTickets > 0 && (
                <span
                  className={`grid h-4.5 min-w-4.5 place-items-center px-1 font-mono text-[0.62rem] ${
                    view === 'help' ? 'bg-bone text-spruce' : 'bg-ochre text-bone'
                  }`}
                >
                  {openTickets}
                </span>
              )}
            </button>
            <span className="grid h-9 w-9 place-items-center border border-ink/15 bg-bone font-mono text-[0.72rem] font-semibold text-spruce">
              {MOCK_USER.initials}
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}
