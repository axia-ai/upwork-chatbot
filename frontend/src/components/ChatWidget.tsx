import { useEffect, useRef, useState } from 'react'
import { ChatIcon, CloseIcon, SendIcon } from './icons'
import { NorthStar } from './Topo'
import { QUICK_REPLIES } from '../data/mock'
import { botReply } from '../lib/botReply'

type Msg = { id: number; role: 'bot' | 'user'; text: string }

let counter = 0
const nextId = () => ++counter

export function ChatWidget({
  open,
  onOpenChange,
  onHandoff,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  onHandoff: () => void
}) {
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: nextId(),
      role: 'bot',
      text: "Hello — I'm the North Star guide. I can track an order, help with a return, recommend gear, or connect you with a person. What do you need?",
    },
  ])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const [liveAgent, setLiveAgent] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, typing, open])

  function botSay(text: string, after = 650) {
    setTyping(true)
    window.setTimeout(() => {
      setTyping(false)
      setMessages((m) => [...m, { id: nextId(), role: 'bot', text }])
    }, after)
  }

  function send(text: string) {
    const trimmed = text.trim()
    if (!trimmed) return
    setMessages((m) => [...m, { id: nextId(), role: 'user', text: trimmed }])
    setInput('')
    const reply = botReply(trimmed)
    if (reply.handoff) {
      setLiveAgent(true)
      onHandoff()
    }
    botSay(reply.text)
  }

  function quick(key: string) {
    const label = QUICK_REPLIES.find((q) => q.key === key)?.label ?? key
    setMessages((m) => [...m, { id: nextId(), role: 'user', text: label }])
    if (key === 'human') {
      setLiveAgent(true)
      onHandoff()
    }
    botSay(botReply(label).text)
  }

  return (
    <div className="fixed bottom-5 right-5 z-40 flex flex-col items-end gap-3 sm:bottom-6 sm:right-6">
      {open && (
        <div className="anim-panel-in flex h-[34rem] max-h-[80vh] w-[22.5rem] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden rounded-lg border border-ink/15 bg-bone shadow-[0_24px_60px_-20px_rgba(29,36,31,0.45)]">
          {/* Header */}
          <div className="flex items-center justify-between gap-3 border-b border-bone/15 bg-spruce px-4 py-3.5 text-bone">
            <div className="flex items-center gap-3">
              <span className="grid h-9 w-9 place-items-center border border-bone/25 text-ochre-soft">
                <NorthStar className="h-5 w-5" />
              </span>
              <div className="leading-tight">
                <p className="font-display text-[1.05rem] font-semibold">North Star Guide</p>
                <p className="eyebrow mt-0.5 text-[0.6rem] text-bone/70">
                  {liveAgent ? 'Connecting a human' : 'Support · online'}
                </p>
              </div>
            </div>
            <button
              onClick={() => onOpenChange(false)}
              className="p-1.5 text-bone/70 transition-colors hover:text-bone"
              aria-label="Close chat"
            >
              <CloseIcon className="h-5 w-5" />
            </button>
          </div>

          {liveAgent && (
            <div className="eyebrow flex items-center gap-2 border-b border-ochre/30 bg-ochre/12 px-4 py-2 text-[0.62rem] text-rust">
              <span className="h-1.5 w-1.5 rounded-full bg-ochre" />
              Live agent · ticket In Progress
            </div>
          )}

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`anim-msg-in flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[84%] px-3.5 py-2.5 text-sm leading-relaxed ${
                    m.role === 'user'
                      ? 'rounded-lg rounded-br-sm bg-spruce text-bone'
                      : 'rounded-lg rounded-bl-sm border border-ink/12 bg-white text-ink'
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}

            {typing && (
              <div className="flex justify-start">
                <div className="flex gap-1 rounded-lg rounded-bl-sm border border-ink/12 bg-white px-3.5 py-3">
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

          {/* Quick replies */}
          {messages.length <= 2 && !typing && (
            <div className="flex flex-wrap gap-2 px-4 pb-2">
              {QUICK_REPLIES.map((q) => (
                <button
                  key={q.key}
                  onClick={() => quick(q.key)}
                  className="border border-ink/15 bg-white px-3 py-1.5 text-xs font-medium text-spruce transition-colors hover:border-spruce hover:bg-spruce hover:text-bone"
                >
                  {q.label}
                </button>
              ))}
            </div>
          )}

          {/* Composer */}
          <form
            onSubmit={(e) => {
              e.preventDefault()
              send(input)
            }}
            className="flex items-center gap-2 border-t border-ink/12 bg-bone px-3 py-3"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message…"
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
          <p className="eyebrow bg-bone pb-2 text-center text-[0.56rem] text-stone/70">
            Prototype · responses mocked until backend is connected
          </p>
        </div>
      )}

      {/* Bubble */}
      <button
        onClick={() => onOpenChange(!open)}
        className="grid h-14 w-14 place-items-center rounded-xl bg-spruce text-ochre-soft shadow-[0_14px_30px_-10px_rgba(29,36,31,0.6)] transition-transform hover:-translate-y-0.5"
        aria-label={open ? 'Close support chat' : 'Open support chat'}
      >
        {open ? <CloseIcon className="h-6 w-6 text-bone" /> : <ChatIcon className="h-6 w-6" />}
      </button>
    </div>
  )
}
