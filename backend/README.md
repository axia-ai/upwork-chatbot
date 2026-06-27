# North Star Support Bot — Backend

Python + FastAPI backend for the North Star Outfitters support chatbot. Claude
(`claude-sonnet-4-6`) drives intent handling with **local semantic-embedding RAG**
(`sentence-transformers` / `all-MiniLM-L6-v2`) over a small knowledge base, and
tickets are persisted in SQLite.

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# API key — never hardcoded; read from the environment.
cp .env.example .env        # then edit .env, or just export the var:
export ANTHROPIC_API_KEY=sk-ant-...
```

The embedding model (~90 MB) downloads once on first use and is then cached
locally; no key or network is needed for it afterwards.

## Demo mode (evaluate without an API key)

The bot runs out of the box with **no Anthropic API key**. When `ANTHROPIC_API_KEY`
is unset, it serves deterministic, local responses (a mock language layer over the
same intent + RAG logic) so all four use cases — order tracking, returns/shipping,
product recommendations, and human handoff — can be evaluated locally at no cost.
A "● Demo mode" badge appears in the chat header.

Set `ANTHROPIC_API_KEY` to use live Claude (`claude-sonnet-4-6`). To force demo
mode while a key is set, also set `DEMO_MODE=true`.

## Run

```bash
uvicorn app.main:app --reload --port 8000
# http://localhost:8000  (seeds northstar.db with the mock tickets on first run)
# Interactive API docs at http://localhost:8000/docs
```

## Test

```bash
pytest        # 32 tests, fully offline — Claude is mocked, throwaway DB, no key needed
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/chat` | `{session_id, message, ticket_id?}` → `{reply, state, handoff, intent, ticket_id}` |
| `POST` | `/reset` | Clear a conversation session |
| `GET` | `/tickets` | List the mock user's tickets (newest first) |
| `GET` | `/tickets/{id}` | One ticket with its transcript |
| `POST` | `/tickets` | Create a ticket |
| `PATCH` | `/tickets/{id}` | Update a ticket's status |
| `GET` | `/health` | Liveness check |

## How it works

- **Agent** ([app/agent.py](app/agent.py)) — a capped Claude tool-calling loop with
  three tools: `get_order_status`, `escalate_to_human`, and `flag_not_understood`.
  Retrieved knowledge-base context is injected into the system prompt each turn.
- **Handoff** — fires on an explicit request **or** two consecutive fallbacks; the
  consecutive-fallback counter lives on the in-memory session and resets on any
  successful turn. On handoff the linked ticket is created or flipped to
  **In Progress** server-side and the turn's messages are saved to its transcript.
- **Retrieval** ([app/retriever.py](app/retriever.py)) — cosine similarity over
  embedded markdown docs in `app/knowledge_base/`.
- **Persistence** — SQLModel + SQLite (`northstar.db`), seeded with the three mock
  tickets. Conversation sessions are in-memory and ephemeral.

## Mock data

Per the brief: orders `#111` (shipped, arriving tomorrow), `#222` (processing,
ships in 24h), `#333` (delivered — offers a follow-up), anything else is invalid.
Returns are 30-day on unused items in original packaging. A small mock product
catalog (`app/knowledge_base/products.md`) fills the recommendation gap, since the
brief provides no catalog.

## Notes / scope

- Sessions are in-memory (cleared on restart or `POST /reset`); fine for a sample,
  not for production.
- Tickets are scoped to a single mock user — no per-ticket auth, by design.
