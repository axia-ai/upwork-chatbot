import { useEffect, useRef, useState } from 'react'
import { BackIcon, SendIcon } from './icons'
import { NorthStar } from './Topo'
import { STATUS_META, MOCK_USER, type Ticket } from '../data/mock'

// Controlled by App: the list comes from GET /tickets and the open ticket (with
// its transcript) from GET /tickets/{id}. Sending a message round-trips through
// the backend, which persists the transcript and any status change.
export function TicketsView({
  tickets,
  active,
  typing,
  onOpen,
  onClose,
  onSend,
  onBack,
}: {
  tickets: Ticket[]
  active: Ticket | null
  typing: boolean
  onOpen: (ticketId: string) => void
  onClose: () => void
  onSend: (text: string) => void
  onBack: () => void
}) {
  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [active?.transcript.length, typing, active?.id])

  function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!active || !input.trim()) return
    onSend(input.trim())
    setInput('')
  }

  return (
    <main className="relative mx-auto max-w-4xl px-5 py-12 sm:px-8">
      <button
        onClick={active ? onClose : onBack}
        className="eyebrow mb-7 inline-flex items-center gap-1.5 text-[0.66rem] text-spruce transition-colors hover:text-rust"
      >
        <BackIcon className="h-4 w-4" />
        {active ? 'All tickets' : 'Back to shop'}
      </button>

      {!active && (
        <>
          <div className="anim-rise border-b border-ink/15 pb-6">
            <p className="eyebrow text-rust">{MOCK_USER.name} · Support desk</p>
            <h1 className="mt-2 font-display text-4xl font-semibold tracking-tight text-spruce">
              My Tickets
            </h1>
            <div className="mt-5 flex flex-wrap gap-2">
              {(['open', 'in_progress', 'closed'] as const).map((s) => {
                const n = tickets.filter((t) => t.status === s).length
                return (
                  <span
                    key={s}
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-[0.7rem] font-semibold ${STATUS_META[s].chip}`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${STATUS_META[s].dot}`} />
                    {STATUS_META[s].label}
                    <span className="font-mono text-stone">{n}</span>
                  </span>
                )
              })}
            </div>
          </div>

          {tickets.length === 0 ? (
            <p className="anim-rise py-12 text-center text-sm text-stone">
              No tickets yet. Start a chat from the shop and ask for a human to open one.
            </p>
          ) : (
            <ul className="anim-rise divide-y divide-ink/12 border-b border-ink/12">
              {tickets.map((t) => (
                <li key={t.id}>
                  <button
                    onClick={() => onOpen(t.id)}
                    className="group grid w-full grid-cols-[auto_1fr_auto] items-center gap-4 py-5 text-left transition-colors hover:bg-bone/60"
                  >
                    <span className="font-mono text-xs text-stone">{t.id}</span>
                    <div className="min-w-0">
                      <h3 className="truncate font-display text-lg font-semibold text-spruce">
                        {t.subject}
                      </h3>
                      <p className="eyebrow mt-0.5 text-[0.62rem] text-stone">
                        {t.topic} · {t.updated}
                      </p>
                    </div>
                    <span className="flex items-center gap-3">
                      <span
                        className={`hidden items-center gap-1.5 px-2.5 py-0.5 text-[0.7rem] font-semibold sm:inline-flex ${STATUS_META[t.status].chip}`}
                      >
                        <span className={`h-1.5 w-1.5 rounded-full ${STATUS_META[t.status].dot}`} />
                        {STATUS_META[t.status].label}
                      </span>
                      <span className="text-stone transition-transform group-hover:translate-x-1">→</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}

      {active && (
        <div className="anim-panel-in flex h-[70vh] flex-col overflow-hidden border border-ink/15 bg-bone">
          {/* Header */}
          <div className="flex items-center justify-between gap-3 border-b border-ink/12 bg-white px-5 py-4">
            <div>
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-xs text-stone">{active.id}</span>
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 text-[0.7rem] font-semibold ${STATUS_META[active.status].chip}`}
                >
                  <span className={`h-1.5 w-1.5 rounded-full ${STATUS_META[active.status].dot}`} />
                  {STATUS_META[active.status].label}
                </span>
              </div>
              <h2 className="mt-1 font-display text-xl font-semibold text-spruce">
                {active.subject}
              </h2>
            </div>
            <span className="grid h-9 w-9 place-items-center border border-ink/15 text-spruce">
              <NorthStar className="h-5 w-5" />
            </span>
          </div>

          {/* Transcript */}
          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-5 py-5">
            {active.transcript.map((m) => (
              <div
                key={m.id}
                className={`anim-msg-in flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[78%] px-4 py-2.5 text-sm leading-relaxed ${
                    m.role === 'user'
                      ? 'rounded-lg rounded-br-sm bg-spruce text-bone'
                      : 'rounded-lg rounded-bl-sm border border-ink/12 bg-white text-ink'
                  }`}
                >
                  {m.text}
                  <span
                    className={`eyebrow mt-1.5 block text-[0.55rem] ${
                      m.role === 'user' ? 'text-bone/60' : 'text-stone'
                    }`}
                  >
                    {m.time}
                  </span>
                </div>
              </div>
            ))}

            {typing && (
              <div className="flex justify-start">
                <div className="flex gap-1 rounded-lg rounded-bl-sm border border-ink/12 bg-white px-4 py-3">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="h-1.5 w-1.5 rounded-full bg-stone"
                      style={{ animation: `bounce-dot 1.2s ${i * 0.15}s infinite` }}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Composer — chat directly inside the ticket */}
          <form
            onSubmit={submit}
            className="flex items-center gap-2 border-t border-ink/12 bg-bone px-4 py-3"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                active.status === 'in_progress' ? 'Message the live agent…' : 'Type a message…'
              }
              className="min-w-0 flex-1 border border-ink/15 bg-white px-3.5 py-2.5 text-sm text-ink outline-none placeholder:text-stone/70 focus:border-spruce"
            />
            <button
              type="submit"
              className="grid h-10 w-10 shrink-0 place-items-center bg-spruce text-bone transition-colors hover:bg-spruce-700 disabled:opacity-40"
              disabled={!input.trim()}
              aria-label="Send"
            >
              <SendIcon className="h-5 w-5" />
            </button>
          </form>
        </div>
      )}
    </main>
  )
}
