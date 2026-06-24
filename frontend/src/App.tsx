import { useMemo, useState } from 'react'
import { Navbar } from './components/Navbar'
import { Storefront } from './components/Storefront'
import { TicketsView } from './components/TicketsView'
import { ChatWidget } from './components/ChatWidget'
import { CANNED, TICKETS, type ChatMessage, type Ticket } from './data/mock'
import { botReply } from './lib/botReply'

type View = 'shop' | 'help'

let mid = 0
const newMsgId = () => `t${++mid}`
const now = () =>
  new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

function App() {
  const [view, setView] = useState<View>('shop')
  const [chatOpen, setChatOpen] = useState(false)
  const [tickets, setTickets] = useState<Ticket[]>(TICKETS)
  const [typingId, setTypingId] = useState<string | null>(null)

  const openCount = useMemo(
    () => tickets.filter((t) => t.status !== 'closed').length,
    [tickets],
  )

  function appendMessage(ticketId: string, msg: ChatMessage, patch?: Partial<Ticket>) {
    setTickets((prev) =>
      prev.map((t) =>
        t.id === ticketId
          ? { ...t, ...patch, updated: 'Just now', transcript: [...t.transcript, msg] }
          : t,
      ),
    )
  }

  // Continue a conversation from inside an open ticket.
  function handleTicketSend(ticketId: string, text: string) {
    const ticket = tickets.find((t) => t.id === ticketId)
    if (!ticket) return

    appendMessage(ticketId, { id: newMsgId(), role: 'user', text, time: now() })
    setTypingId(ticketId)

    const live = ticket.status === 'in_progress'
    const reply = live ? { text: CANNED.agent, handoff: false } : botReply(text)

    window.setTimeout(() => {
      appendMessage(
        ticketId,
        { id: newMsgId(), role: 'bot', text: reply.text, time: now() },
        reply.handoff ? { status: 'in_progress', topic: 'Human handoff' } : undefined,
      )
      setTypingId(null)
    }, 750)
  }

  function handleHandoff() {
    // Reflect the live-agent handoff (from the floating widget) as a new In
    // Progress ticket, so the Help section stays consistent.
    setTickets((prev) => {
      if (prev.some((t) => t.id === 'NS-1071')) return prev
      const ticket: Ticket = {
        id: 'NS-1071',
        subject: 'Requested a live agent',
        status: 'in_progress',
        topic: 'Human handoff',
        updated: 'Just now',
        transcript: [
          { id: 'h1', role: 'user', text: 'I want to talk to a human.', time: now() },
          {
            id: 'h2',
            role: 'bot',
            text: 'Connecting you with a live agent — your ticket is now In Progress and a teammate will be with you shortly.',
            time: now(),
          },
        ],
      }
      return [ticket, ...prev]
    })
  }

  return (
    <div className="min-h-screen bg-paper">
      <Navbar view={view} onNavigate={setView} openTickets={openCount} />

      {view === 'shop' ? (
        <Storefront onAskBot={() => setChatOpen(true)} />
      ) : (
        <TicketsView
          tickets={tickets}
          typingId={typingId}
          onSend={handleTicketSend}
          onBack={() => setView('shop')}
        />
      )}

      <ChatWidget
        open={chatOpen}
        onOpenChange={setChatOpen}
        onHandoff={handleHandoff}
      />
    </div>
  )
}

export default App
