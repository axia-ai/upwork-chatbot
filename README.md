# North Star Outfitters — Support Chatbot

A customer-support chatbot for **North Star Outfitters**, a mock outdoor-apparel &
camping-gear store. A React storefront embeds a chat widget backed by a FastAPI
service that uses **Claude** (`claude-sonnet-4-6`) for intent handling and
**local semantic-embedding RAG** over a small knowledge base. Support
conversations become **tickets** (Open / In Progress / Closed) that persist in
SQLite.

## What it does

The bot handles the four required support flows plus a graceful fallback:

1. **Order tracking** — asks for an order number and returns its status
   (`#111` shipped, `#222` processing, `#333` delivered, anything else invalid —
   no fabricated statuses).
2. **Returns & exchanges** — explains the 30-day policy and links the returns
   portal, grounded in the knowledge base.
3. **Product recommendations** — asks one or two clarifying questions, then
   recommends a category and a fitting product from the catalog.
4. **Human handoff** — on an explicit request **or** two consecutive fallbacks,
   it escalates to a live agent and the conversation becomes an **In Progress**
   ticket, created server-side.

A **My Tickets** view lists the signed-in mock user's tickets and lets you keep
chatting inside a ticket.

## Architecture

```
frontend (React + Vite + TS + Tailwind)        backend (FastAPI + Claude + RAG + SQLite)
┌───────────────────────────────┐   /api/*     ┌──────────────────────────────────────┐
│ Storefront + chat widget       │  ─────────▶  │ POST /chat   — agent tool-calling loop │
│ My Tickets (list + transcript) │   (Vite      │ POST /reset  — clear a session         │
│ src/lib/api.ts (the API seam)  │    proxy)    │ GET/POST/PATCH /tickets — CRUD          │
└───────────────────────────────┘  ◀─────────  │ retriever.py — all-MiniLM-L6-v2 + cosine│
                                                │ SQLModel/SQLite — seeded mock tickets   │
                                                └──────────────────────────────────────┘
```

- **Agent** — a capped Claude tool-calling loop with three tools
  (`get_order_status`, `escalate_to_human`, `flag_not_understood`). Retrieved
  knowledge-base context is injected into the system prompt each turn.
- **RAG** — `sentence-transformers` (`all-MiniLM-L6-v2`) embeddings with cosine
  similarity over markdown docs in `backend/app/knowledge_base/`. Runs locally;
  no embeddings API or extra key.
- **Persistence** — tickets and transcripts in SQLite; a handoff turn creates or
  flips a ticket to In Progress and saves the messages. Chat sessions
  (history, live-agent flag, fallback counter) are in-memory.

## Tech stack

| | |
|---|---|
| Frontend | React, Vite, TypeScript, Tailwind CSS v4 |
| Backend | Python, FastAPI, SQLModel + SQLite |
| LLM | Claude `claude-sonnet-4-6` (Anthropic SDK) |
| Retrieval | sentence-transformers (`all-MiniLM-L6-v2`), local |

## Demo mode (evaluate without an API key)

The bot runs out of the box with **no Anthropic API key**. When `ANTHROPIC_API_KEY`
is unset, it serves deterministic, local responses (a mock language layer over the
same intent + RAG logic) so all four use cases — order tracking, returns/shipping,
product recommendations, and human handoff — can be evaluated locally at no cost.
A "● Demo mode" badge appears in the chat header.

Set `ANTHROPIC_API_KEY` to use live Claude (`claude-sonnet-4-6`). To force demo
mode while a key is set, also set `DEMO_MODE=true`.

## Quick start

You'll need **Python 3.9–3.12**, **Node 18+**, and an **Anthropic API key**.
(`sentence-transformers`/`torch` don't yet ship wheels for Python 3.13+, so a
newer interpreter fails to install — `./start.sh` auto-selects a supported one
if you have it.)

### Option A — one command (recommended)

```bash
./start.sh
```

On the first run this installs both apps' dependencies and asks for your
Anthropic API key (saved locally to `backend/.env`, never committed), then starts
the backend and frontend and opens **http://localhost:5173** in your browser.
Press **Ctrl+C** to stop. Works on macOS and Linux (and Git Bash / WSL on Windows).

### Option B — run each app manually

Use two terminals — one for the backend, one for the frontend.

#### 1. Backend (`:8000`)

Use a Python 3.9–3.12 interpreter here (e.g. `python3.12`); 3.13+ has no
`torch`/`sentence-transformers` wheel yet and `pip install` will fail.

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate   # or python3.11 / 3.10 / 3.9
pip install -r requirements.txt

cp .env.example .env          # then put your key in .env:
#   ANTHROPIC_API_KEY=sk-ant-...
# (or: export ANTHROPIC_API_KEY=sk-ant-...)

uvicorn app.main:app --reload --port 8000
```

The embedding model (~90 MB) downloads once on first use, then is cached. The
SQLite DB seeds three mock tickets on first run. API docs: http://localhost:8000/docs

#### 2. Frontend (`:5173`)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The Vite dev server proxies `/api/*` to the
backend, so no CORS setup is needed.

## Try it (manual scenario checklist)

Open the chat bubble (bottom-right) and try:

- [ ] **Order tracking** — "Where is my order #111?" → shipped, arriving tomorrow.
      Try `#222`, `#333`, and an invalid number like `#999`.
- [ ] **Returns** — "How do I return a jacket that runs small?" → 30-day policy + link.
- [ ] **Recommendations** — "I need a sleeping bag for cold-weather backpacking" →
      a clarifying question, then a specific product.
- [ ] **Human handoff** — "I'd like to talk to a person" → live-agent banner; open
      **My Tickets** and see the new **In Progress** ticket.
- [ ] **Fallback → auto-escalation** — send two unintelligible messages in a row →
      the second escalates to a live agent automatically.
- [ ] **Tickets** — open a ticket from My Tickets to read its transcript and reply
      inside it.

## Testing

```bash
cd backend && pytest        # 33 tests, fully offline — Claude mocked, throwaway DB
```

The suite covers the four order cases, retrieval relevance, explicit + automatic
handoff, the fallback counter, ticket CRUD, the chat→ticket link, error
degradation (clean 503), and the tool-loop safety cap. No API key or network is
needed to run it.

## Mock data

Per the brief: orders `#111` (shipped, arriving tomorrow), `#222` (processing,
ships in 24h), `#333` (delivered — offers a follow-up); anything else is invalid.
Returns are 30-day on unused items in original packaging; shipping is Standard
3–5 days / Expedited 1–2 days. A small mock product catalog
(`backend/app/knowledge_base/products.md`) fills the recommendation gap, since the
brief provides no catalog.

## Project structure

```
backend/
  app/
    main.py            # FastAPI app, CORS, DB seeding on startup
    routers/           # chat.py, tickets.py
    agent.py           # Claude tool-calling loop + system prompt
    retriever.py       # local embeddings + cosine retrieval
    orders.py          # deterministic mock order lookup
    session.py         # in-memory session state
    models.py / db.py  # SQLModel tables + seed
    knowledge_base/    # returns, shipping, products, faq (markdown)
  tests/               # offline pytest suite (Claude mocked)
frontend/
  src/
    App.tsx            # orchestrator: view, chat + ticket state
    components/        # Storefront, ChatWidget, TicketsView, Navbar, …
    lib/api.ts         # typed backend client (the integration seam)
    data/mock.ts       # storefront/UI data + shared types
```

## Scope notes

- Chat sessions are in-memory (cleared on restart or `POST /reset`) — fine for a
  sample, not for production.
- Tickets are scoped to a single mock user ("Riley Carter"); there is no
  per-ticket auth, by design.
- The API key is read from `ANTHROPIC_API_KEY` and never hardcoded or logged.
