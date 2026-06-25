import { useEffect, useMemo, useRef, useState } from 'react'
import { Navbar } from './components/Navbar'
import { Storefront } from './components/Storefront'
import { TicketsView } from './components/TicketsView'
import { ChatWidget } from './components/ChatWidget'
import { type ChatMessage, type Ticket } from './data/mock'
import { getTicket, getTickets, postChat } from './lib/api'

type View = 'shop' | 'help'

const GREETING =
  "Hello — I'm the North Star guide. I can track an order, help with a return, " +
  'recommend gear, or connect you with a person. What do you need?'

const ERROR_REPLY =
  "Sorry — I'm having trouble reaching the assistant right now. Please try again in a moment."

const now = () =>
  new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

const message = (role: ChatMessage['role'], text: string): ChatMessage => ({
  id: crypto.randomUUID(),
  role,
  text,
  time: now(),
})

function App() {
  const [view, setView] = useState<View>('shop')
  const [chatOpen, setChatOpen] = useState(false)

  // Tickets are server-owned (loaded from the backend).
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [activeTicket, setActiveTicket] = useState<Ticket | null>(null)
  const [ticketTyping, setTicketTyping] = useState(false)

  // The widget conversation is caller-owned and shares the ChatMessage shape
  // with tickets — one model for both chat surfaces.
  const [widgetMessages, setWidgetMessages] = useState<ChatMessage[]>([message('bot', GREETING)])
  const [widgetTyping, setWidgetTyping] = useState(false)
  const [liveAgent, setLiveAgent] = useState(false)

  // Stable per-surface session ids (backend conversation memory).
  const widgetSession = useRef(crypto.randomUUID())

  const openCount = useMemo(
    () => tickets.filter((t) => t.status !== 'closed').length,
    [tickets],
  )

  async function refreshTickets() {
    try {
      setTickets(await getTickets())
    } catch (err) {
      console.error('Failed to load tickets', err)
    }
  }

  useEffect(() => {
    refreshTickets()
  }, [])

  // --- Floating widget ---
  async function handleWidgetSend(text: string) {
    const trimmed = text.trim()
    if (!trimmed) return
    setWidgetMessages((m) => [...m, message('user', trimmed)])
    setWidgetTyping(true)
    try {
      const res = await postChat(widgetSession.current, trimmed)
      setWidgetMessages((m) => [...m, message('bot', res.reply)])
      setLiveAgent(res.state === 'live_agent')
      if (res.handoff) refreshTickets() // a new In Progress ticket may exist
    } catch {
      setWidgetMessages((m) => [...m, message('bot', ERROR_REPLY)])
    } finally {
      setWidgetTyping(false)
    }
  }

  // --- In-ticket composer ---
  async function openTicket(id: string) {
    try {
      setActiveTicket(await getTicket(id))
    } catch (err) {
      console.error('Failed to open ticket', err)
    }
  }

  async function handleTicketSend(text: string) {
    const trimmed = text.trim()
    if (!activeTicket || !trimmed) return
    const id = activeTicket.id
    // Optimistic user bubble; the canonical transcript is refetched below.
    setActiveTicket((t) => (t ? { ...t, transcript: [...t.transcript, message('user', trimmed)] } : t))
    setTicketTyping(true)
    try {
      await postChat(`ticket-${id}`, trimmed, id)
      setActiveTicket(await getTicket(id)) // canonical transcript + status
      refreshTickets()
    } catch {
      setActiveTicket((t) =>
        t ? { ...t, transcript: [...t.transcript, message('bot', ERROR_REPLY)] } : t,
      )
    } finally {
      setTicketTyping(false)
    }
  }

  function navigate(next: View) {
    setView(next)
    if (next === 'help') {
      setActiveTicket(null)
      refreshTickets()
    }
  }

  return (
    <div className="min-h-screen bg-paper">
      <Navbar view={view} onNavigate={navigate} openTickets={openCount} />

      {view === 'shop' ? (
        <Storefront onAskBot={() => setChatOpen(true)} />
      ) : (
        <TicketsView
          tickets={tickets}
          active={activeTicket}
          typing={ticketTyping}
          onOpen={openTicket}
          onClose={() => setActiveTicket(null)}
          onSend={handleTicketSend}
          onBack={() => setView('shop')}
        />
      )}

      <ChatWidget
        open={chatOpen}
        onOpenChange={setChatOpen}
        messages={widgetMessages}
        typing={widgetTyping}
        liveAgent={liveAgent}
        onSend={handleWidgetSend}
      />
    </div>
  )
}

export default App
