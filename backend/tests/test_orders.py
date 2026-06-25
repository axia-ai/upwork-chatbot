"""The four order-lookup cases from the brief."""

import pytest

from app.orders import get_order_status


@pytest.mark.parametrize(
    "query, expected_substring",
    [
        ("111", "shipped"),
        ("#111", "arriving tomorrow"),
        ("222", "processing"),
        ("333", "delivered"),
    ],
)
def test_valid_orders(query, expected_substring):
    result = get_order_status(query)
    assert result.found is True
    assert expected_substring in result.status.lower()


def test_unknown_order_is_not_fabricated():
    result = get_order_status("999")
    assert result.found is False
    assert "couldn't find" in result.status.lower()


def test_empty_input_is_not_found():
    result = get_order_status("")
    assert result.found is False
