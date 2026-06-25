// Static storefront/UI data and shared types for the North Star Outfitters app.
// Chat and tickets are served by the FastAPI backend (see src/lib/api.ts); the
// product catalogue and status styling below are presentation-only.

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

// Quick-reply chips in the chat widget — each sends its label to the backend.
export const QUICK_REPLIES = [
  { key: 'track', label: 'Track my order' },
  { key: 'returns', label: 'Returns & exchanges' },
  { key: 'recommend', label: 'Recommend gear' },
  { key: 'human', label: 'Talk to a human' },
]
