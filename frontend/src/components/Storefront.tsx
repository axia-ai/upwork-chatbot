import { Topo } from './Topo'
import { PRODUCTS } from '../data/mock'

const TINTS = [
  'bg-spruce text-ochre-soft',
  'bg-rust text-bone',
  'bg-moss text-bone',
  'bg-spruce-700 text-ochre-soft',
  'bg-ink text-moss',
  'bg-ochre text-bone',
]

export function Storefront({ onAskBot }: { onAskBot: () => void }) {
  return (
    <main className="relative">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-ink/12 bg-spruce text-bone">
        <div className="pointer-events-none absolute -right-24 top-1/2 hidden h-[140%] w-[42rem] -translate-y-1/2 text-bone/10 md:block">
          <Topo className="h-full w-full" strokeWidth={1.1} />
        </div>

        <div className="relative mx-auto max-w-6xl px-5 py-20 sm:px-8 md:py-28">
          <div className="max-w-2xl anim-rise">
            <p className="eyebrow text-ochre-soft">Pacific Northwest · Outfitters since 1971</p>
            <h1 className="mt-6 font-display text-[3.25rem] font-semibold leading-[0.98] tracking-tight sm:text-7xl">
              Gear made to be
              <br />
              <span className="italic text-ochre-soft">mended, not replaced.</span>
            </h1>
            <p className="mt-7 max-w-lg text-lg leading-relaxed text-bone/80">
              Apparel and camping kit for cold mornings and long trails — built
              by people who'd rather repair a jacket than sell you a new one.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-4">
              <a
                href="#shop"
                className="bg-ochre px-7 py-3.5 text-sm font-semibold text-bone transition-colors hover:bg-ochre-soft hover:text-spruce"
              >
                Shop the catalogue
              </a>
              <button
                onClick={onAskBot}
                className="border border-bone/30 px-7 py-3.5 text-sm font-semibold text-bone transition-colors hover:border-bone"
              >
                Talk to a guide
              </button>
            </div>
          </div>
        </div>

        {/* meta strip */}
        <div className="relative border-t border-bone/15">
          <div className="mx-auto grid max-w-6xl grid-cols-2 divide-x divide-bone/15 sm:grid-cols-4">
            {[
              ['01', 'Field-tested'],
              ['02', 'Lifetime repairs'],
              ['03', 'Carbon-neutral shipping'],
              ['04', '40k+ trail miles logged'],
            ].map(([n, label]) => (
              <div key={n} className="px-5 py-5 sm:px-6">
                <span className="eyebrow text-ochre-soft">No. {n}</span>
                <p className="mt-1 text-sm font-medium text-bone/85">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Catalogue */}
      <section id="shop" className="mx-auto max-w-6xl px-5 py-16 sm:px-8 md:py-24">
        <div className="flex items-end justify-between border-b border-ink/15 pb-5">
          <div>
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-rust">
              The field catalogue
            </p>
            <h2 className="mt-2 font-sans text-3xl font-semibold tracking-tight text-spruce sm:text-[2.5rem]">
              Built for the next ridge
            </h2>
          </div>
          <span className="hidden font-mono text-xs text-stone sm:block">
            {PRODUCTS.length} of 124 styles
          </span>
        </div>

        <div className="mt-10 grid gap-x-8 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
          {PRODUCTS.map((p, i) => (
            <article
              key={p.id}
              className="group anim-rise"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div
                className={`relative aspect-[4/5] overflow-hidden ${TINTS[i % TINTS.length]}`}
              >
                <div className="absolute inset-0 opacity-30 transition-transform duration-700 group-hover:scale-110">
                  <Topo className="h-full w-full" strokeWidth={1} />
                </div>
                <span className="absolute left-4 top-4 font-mono text-[0.7rem] text-current">
                  No. {String(i + 1).padStart(2, '0')}
                </span>
                <span className="eyebrow absolute bottom-4 left-4 text-current">
                  {p.category}
                </span>
              </div>
              <div className="mt-4 flex items-baseline justify-between gap-3 border-t border-ink/15 pt-3">
                <h3 className="font-display text-xl font-semibold text-spruce">{p.name}</h3>
                <span className="font-mono text-sm text-rust">{p.price}</span>
              </div>
              <p className="mt-1.5 text-sm leading-relaxed text-stone">{p.blurb}</p>
            </article>
          ))}
        </div>
      </section>

      {/* Support band */}
      <section id="about" className="relative overflow-hidden border-t border-ink/12 bg-bone">
        <div className="pointer-events-none absolute -left-20 top-1/2 h-[120%] w-[30rem] -translate-y-1/2 text-spruce/8">
          <Topo className="h-full w-full" strokeWidth={1.1} />
        </div>
        <div className="relative mx-auto flex max-w-6xl flex-col items-start gap-4 px-5 py-16 sm:px-8 md:flex-row md:items-center md:justify-between">
          <div className="max-w-xl">
            <p className="eyebrow text-rust">Support desk</p>
            <h2 className="mt-2 font-display text-3xl font-semibold tracking-tight text-spruce">
              Questions on the trail?
            </h2>
            <p className="mt-3 max-w-md text-sm leading-relaxed text-stone">
              Our guide handles order tracking, returns, and gear advice — and
              hands you to a human the moment you need one.
            </p>
          </div>
          <button
            onClick={onAskBot}
            className="bg-spruce px-7 py-3.5 text-sm font-semibold text-bone transition-colors hover:bg-spruce-700"
          >
            Open the support desk
          </button>
        </div>
      </section>
    </main>
  )
}
