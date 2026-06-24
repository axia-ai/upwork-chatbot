// Mock data for the North Star Outfitters prototype.
// NOTE: this is placeholder UI data only — the real bot will be wired to the
// FastAPI backend + Claude later. Order / policy / shipping facts mirror the brief.

export type TicketStatus = 'open' | 'in_progress' | 'closed'

export type ChatMessage = {
  id: string
  role: 'bot' | 'user'
  text: string
  time: string
}

export type Ticket = {
  id: string
  subject: string
  status: TicketStatus
  topic: string
  updated: string
  transcript: ChatMessage[]
}

export type Product = {
  id: string
  name: string
  category: string
  price: string
  blurb: string
  tone: string // tailwind gradient classes for the mock product "image"
}

export const PRODUCTS: Product[] = [
  {
    id: 'p1',
    name: 'Summit Down Parka',
    category: 'Insulated Jackets',
    price: '$289',
    blurb: '800-fill responsibly sourced down for alpine cold.',
    tone: 'from-pine-700 to-pine-900',
  },
  {
    id: 'p2',
    name: 'Wildwood 3P Tent',
    category: 'Tents',
    price: '$349',
    blurb: 'Three-season, two-vestibule shelter under 5 lbs.',
    tone: 'from-clay-500 to-clay-600',
  },
  {
    id: 'p3',
    name: 'Polaris -10° Bag',
    category: 'Sleeping Bags',
    price: '$219',
    blurb: 'Mummy-cut down bag rated for frosty nights.',
    tone: 'from-amber-400 to-clay-500',
  },
  {
    id: 'p4',
    name: 'Trailhead 45 Pack',
    category: 'Backpacks',
    price: '$179',
    blurb: 'Weekend-load carry with a ventilated trampoline back.',
    tone: 'from-pine-600 to-pine-800',
  },
  {
    id: 'p5',
    name: 'Granite GTX Boots',
    category: 'Hiking Footwear',
    price: '$199',
    blurb: 'Waterproof leather mid with a grippy lugged sole.',
    tone: 'from-stone to-pine-800',
  },
  {
    id: 'p6',
    name: 'Aurora Base Layer',
    category: 'Insulated Jackets',
    price: '$64',
    blurb: 'Merino crew that regulates from dawn patrol to camp.',
    tone: 'from-amber-500 to-amber-400',
  },
]

export const CATEGORIES = [
  'Tents',
  'Sleeping Bags',
  'Insulated Jackets',
  'Hiking Footwear',
  'Backpacks',
]

export const MOCK_USER = { name: 'Riley Carter', initials: 'RC' }

export const TICKETS: Ticket[] = [
  {
    id: 'NS-1063',
    subject: 'Damaged tent pole on arrival',
    status: 'in_progress',
    topic: 'Human handoff',
    updated: '2h ago',
    transcript: [
      { id: 'm1', role: 'user', text: 'My new tent arrived with a cracked pole. I want to talk to a person.', time: '10:02' },
      { id: 'm2', role: 'bot', text: "I'm sorry about the damaged pole, Riley. I'm connecting you with a live agent now — your ticket is open and a teammate will jump in shortly.", time: '10:02' },
      { id: 'm3', role: 'bot', text: 'Live agent Dana has joined the conversation.', time: '10:05' },
    ],
  },
  {
    id: 'NS-1057',
    subject: 'Return a jacket that runs small',
    status: 'open',
    topic: 'Returns & exchanges',
    updated: 'Yesterday',
    transcript: [
      { id: 'm1', role: 'user', text: 'How do I return a jacket?', time: '16:41' },
      { id: 'm2', role: 'bot', text: 'Happy to help! We offer 30-day returns on unused items in their original packaging. You can start your return here: northstar.example.com/returns', time: '16:41' },
      { id: 'm3', role: 'user', text: 'Great, thanks!', time: '16:42' },
    ],
  },
  {
    id: 'NS-1042',
    subject: 'Where is order #111?',
    status: 'closed',
    topic: 'Order tracking',
    updated: '3 days ago',
    transcript: [
      { id: 'm1', role: 'user', text: 'Where is my order?', time: '09:12' },
      { id: 'm2', role: 'bot', text: "I can track that for you — what's your order number?", time: '09:12' },
      { id: 'm3', role: 'user', text: '#111', time: '09:13' },
      { id: 'm4', role: 'bot', text: 'Good news! Order #111 has shipped and is arriving tomorrow. Anything else I can help with?', time: '09:13' },
      { id: 'm5', role: 'user', text: "That's all, thanks!", time: '09:14' },
    ],
  },
]

export const STATUS_META: Record<TicketStatus, { label: string; dot: string; chip: string }> = {
  open: {
    label: 'Open',
    dot: 'bg-moss',
    chip: 'border border-moss/40 bg-moss/10 text-spruce',
  },
  in_progress: {
    label: 'In Progress',
    dot: 'bg-ochre',
    chip: 'border border-ochre/45 bg-ochre/10 text-rust',
  },
  closed: {
    label: 'Closed',
    dot: 'bg-stone',
    chip: 'border border-stone/35 bg-stone/8 text-stone',
  },
}

// Canned bot replies so the prototype demonstrates each flow without a backend.
export const QUICK_REPLIES = [
  { key: 'track', label: 'Track my order' },
  { key: 'returns', label: 'Returns & exchanges' },
  { key: 'recommend', label: 'Recommend gear' },
  { key: 'human', label: 'Talk to a human' },
]

export const CANNED: Record<string, string> = {
  track: "I can help track your order — what's your order number? (Try #111, #222, or #333.)",
  returns:
    'We offer 30-day returns on unused items in their original packaging. Start your return here: northstar.example.com/returns. Anything else?',
  recommend:
    "Love it — let's find the right gear. What are you heading out for: backpacking, car camping, or day hikes? And what conditions — summer, shoulder-season, or deep cold?",
  human:
    "Of course — I'm connecting you with a live agent. This conversation is now a ticket marked In Progress, and a teammate will be with you shortly.",
  fallback:
    "I didn't quite catch that. I can help with order tracking, returns and exchanges, product recommendations, or connect you with a human — which would you like?",
  // Live-agent persona reply used inside In Progress tickets.
  agent:
    "Thanks for the details — Dana from the gear team here. I've got this logged and I'm on it. Anything else I can help with while we sort it out?",
}

// Mock order statuses (mirrors the brief).
export const ORDER_STATUS: Record<string, string> = {
  '111': 'Order #111 has shipped and is arriving tomorrow. Anything else I can help with?',
  '222': 'Order #222 is processing and ships within 24 hours. Anything else I can help with?',
  '333': 'Order #333 was delivered. Did everything arrive in good shape?',
}
