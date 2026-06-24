import { CANNED, ORDER_STATUS } from '../data/mock'

// Shared mock routing for the prototype, used by both the floating widget and
// the in-ticket composer. Replaced by the real backend later.
export function botReply(raw: string): { text: string; handoff: boolean } {
  const t = raw.toLowerCase()

  const order = raw.match(/\b(111|222|333)\b/)
  if (order) return { text: ORDER_STATUS[order[1]], handoff: false }
  if (/\b\d{3,}\b/.test(raw))
    return {
      text: "I couldn't find that order number. Please double-check it (try #111, #222, or #333).",
      handoff: false,
    }
  if (/(track|order|package|where.*order|shipment|delivery)/.test(t))
    return { text: CANNED.track, handoff: false }
  if (/(return|refund|exchange|send.*back)/.test(t))
    return { text: CANNED.returns, handoff: false }
  if (/(recommend|suggest|gear|tent|jacket|bag|boots|backpack|what should)/.test(t))
    return { text: CANNED.recommend, handoff: false }
  if (/(human|agent|person|representative|someone|talk to)/.test(t))
    return { text: CANNED.human, handoff: true }

  return { text: CANNED.fallback, handoff: false }
}
