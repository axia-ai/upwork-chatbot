"""Deterministic mock order lookup.

The brief defines exactly three valid orders; anything else is invalid. The bot
must never fabricate a status, so this returns a clear "not found" result for
unknown numbers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Order facts straight from the brief.
_ORDERS: dict[str, str] = {
    "111": "Order #111 has shipped and is arriving tomorrow.",
    "222": "Order #222 is processing and ships within 24 hours.",
    "333": "Order #333 was delivered.",
}


@dataclass
class OrderResult:
    found: bool
    order_number: str
    status: str


def _normalize(order_number: str) -> str:
    """Strip a leading '#' and surrounding whitespace; keep the digits."""
    match = re.search(r"\d+", order_number or "")
    return match.group(0) if match else ""


def get_order_status(order_number: str) -> OrderResult:
    """Look up a mock order. Unknown numbers return ``found=False`` (no fabrication)."""
    number = _normalize(order_number)
    if number in _ORDERS:
        return OrderResult(found=True, order_number=number, status=_ORDERS[number])
    return OrderResult(
        found=False,
        order_number=number,
        status=(
            "I couldn't find that order number. Please double-check it "
            "(try #111, #222, or #333)."
        ),
    )
