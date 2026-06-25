// Typed client for the FastAPI backend. This is the integration seam that
// replaced the old mock `botReply` — the widget and the in-ticket composer both
// talk to the backend through here.
import type { ChatMessage, Ticket, TicketStatus } from '../data/mock'

const API = '/api'

export interface ChatResponse {
  reply: string
  state: 'bot' | 'live_agent'
  handoff: boolean
  intent: string
  ticket_id: string | null
}

async function unwrap<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (body?.detail) detail = body.detail
    } catch {
      /* non-JSON error body — keep the generic message */
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

export async function postChat(
  sessionId: string,
  message: string,
  ticketId?: string | null,
): Promise<ChatResponse> {
  const res = await fetch(`${API}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message, ticket_id: ticketId ?? null }),
  })
  return unwrap<ChatResponse>(res)
}

interface TicketDTO {
  id: string
  subject: string
  status: TicketStatus
  topic: string
  updated: string // ISO-8601
  transcript?: ChatMessage[]
}

function toTicket(dto: TicketDTO): Ticket {
  return {
    id: dto.id,
    subject: dto.subject,
    status: dto.status,
    topic: dto.topic,
    updated: formatUpdated(dto.updated),
    transcript: dto.transcript ?? [],
  }
}

export async function getTickets(): Promise<Ticket[]> {
  const data = await unwrap<TicketDTO[]>(await fetch(`${API}/tickets`))
  return data.map(toTicket)
}

export async function getTicket(id: string): Promise<Ticket> {
  return toTicket(await unwrap<TicketDTO>(await fetch(`${API}/tickets/${id}`)))
}

// Render the API's ISO timestamp as a short relative label for the ticket list.
export function formatUpdated(iso: string): string {
  const then = new Date(iso).getTime()
  if (Number.isNaN(then)) return ''
  const secs = Math.max(0, (Date.now() - then) / 1000)
  if (secs < 60) return 'Just now'
  const mins = Math.floor(secs / 60)
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  return new Date(iso).toLocaleDateString()
}
