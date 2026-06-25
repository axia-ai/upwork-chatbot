"""Claude-driven support agent.

Runs a tool-calling loop against ``claude-sonnet-4-6`` with retrieved knowledge-
base context injected into the system prompt. The model drives intent handling;
three tools give the backend deterministic signals:

- ``get_order_status`` — order tracking (deterministic mock lookup).
- ``escalate_to_human`` — explicit human-handoff request.
- ``flag_not_understood`` — the turn was a fallback ("didn't catch that").

Handoff fires on an explicit request OR two consecutive fallbacks (the counter
lives on the session). The Anthropic client is injected so tests can mock it —
no key or network is needed to exercise the loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from app import orders
from app.config import get_settings
from app.session import Session

SYSTEM_PROMPT = """You are the North Star Guide, the support assistant for North \
Star Outfitters, an outdoor-apparel and camping-gear store. Be warm, concise, and \
helpful.

You can help with exactly four things:
1. Order tracking — if the user asks where an order is, ask for the order number \
if you don't have it, then call get_order_status. Never invent an order status.
2. Returns & exchanges and shipping — answer from the KNOWLEDGE BASE below. Quote \
the policy accurately and include the returns link when relevant. Do not invent \
policy details.
3. Product recommendations — ask one or two short clarifying questions (what trip, \
what conditions), then recommend a category and a fitting product from the \
knowledge base.
4. Human handoff — if the user explicitly asks to talk to a person, human, agent, \
or representative, call escalate_to_human and let them know a teammate is joining.

If the user's message doesn't fit any of those (it's unclear or off-topic), give a \
brief friendly reply that says you didn't quite catch that and lists what you can \
help with, and call flag_not_understood. Don't call flag_not_understood for \
greetings or supported topics you can handle.

Keep replies to a few sentences. Use only the facts in the knowledge base and the \
tools — never make up orders, policies, or products."""

TOOLS = [
    {
        "name": "get_order_status",
        "description": (
            "Look up the status of a customer order by its order number. Use "
            "whenever the user asks where their order is or provides an order number."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number (digits, optionally with a leading #).",
                }
            },
            "required": ["order_number"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Connect the user to a live human agent. Call this ONLY when the user "
            "explicitly asks to speak with a person, human, agent, or representative."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "flag_not_understood",
        "description": (
            "Call this when the user's message does not relate to order tracking, "
            "returns/exchanges, shipping, or product recommendations and you are "
            "giving a generic 'I didn't catch that' fallback reply."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]


# Safety cap on the tool-calling loop (each iteration is a paid model call).
MAX_TOOL_ITERATIONS = 5


@dataclass
class AgentResult:
    reply: str
    intent: str  # order | returns | recommend | handoff | fallback | general
    handoff: bool
    state: str  # "bot" | "live_agent"


@lru_cache
def get_client():
    """Real Anthropic client, created from the env-provided key."""
    import anthropic

    settings = get_settings()
    return anthropic.Anthropic(api_key=settings.anthropic_api_key or None)


def _build_system_prompt(kb_context: str) -> str:
    if not kb_context:
        return SYSTEM_PROMPT
    return f"{SYSTEM_PROMPT}\n\n--- KNOWLEDGE BASE ---\n{kb_context}"


def run_agent(
    client,
    session: Session,
    user_message: str,
    kb_context: str = "",
    *,
    model: str | None = None,
    max_tokens: int = 1024,
) -> AgentResult:
    """Run one chat turn through the tool-calling loop and update session state."""
    model = model or get_settings().claude_model
    system = _build_system_prompt(kb_context)
    messages = [*[dict(m) for m in session.history], {"role": "user", "content": user_message}]

    intent = "general"
    explicit_handoff = False
    fallback = False
    reply = ""

    # Tool-calling loop, capped so a misbehaving model can't spin (and bill) forever.
    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            tools=TOOLS,
            messages=messages,
        )
        # Keep the latest non-empty text: the model often delivers its user-facing
        # message in the same turn as a signal tool call (e.g. the fallback line
        # alongside flag_not_understood), and the follow-up turn can be empty.
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        if text:
            reply = text
        if response.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            is_error = False
            try:
                if block.name == "get_order_status":
                    intent = "order"
                    result = orders.get_order_status(block.input.get("order_number", "")).status
                elif block.name == "escalate_to_human":
                    intent = "handoff"
                    explicit_handoff = True
                    result = "Connected to a live agent. The ticket is now In Progress."
                elif block.name == "flag_not_understood":
                    intent = "fallback"
                    fallback = True
                    result = "Acknowledged — offer the user the supported options."
                else:
                    result = "Unknown tool."
                    is_error = True
            except Exception:  # noqa: BLE001 — surface the failure to the model, don't crash the turn
                result = "That lookup failed. Apologize briefly and offer to connect a human."
                is_error = True
            tool_result = {"type": "tool_result", "tool_use_id": block.id, "content": result}
            if is_error:
                tool_result["is_error"] = True
            tool_results.append(tool_result)
        messages.append({"role": "user", "content": tool_results})
    else:
        # Hit the iteration cap without a final text answer — degrade gracefully.
        if not reply:
            reply = (
                "Sorry — I'm having trouble completing that right now. "
                "Would you like me to connect you with a human?"
            )

    # Apply handoff / fallback state transitions (the 2-fallback rule).
    handoff = False
    if explicit_handoff:
        session.live_agent = True
        session.fallback_count = 0
        handoff = True
    elif fallback:
        session.fallback_count += 1
        if session.fallback_count >= 2:
            session.live_agent = True
            handoff = True  # auto-escalation
    else:
        session.fallback_count = 0

    # Persist a text-only view of the turn for multi-turn context.
    session.history.append({"role": "user", "content": user_message})
    session.history.append({"role": "assistant", "content": reply})

    state = "live_agent" if session.live_agent else "bot"
    return AgentResult(reply=reply, intent=intent, handoff=handoff, state=state)
