"""Exercice 2 : serveur MCP et erreurs structurées. LAB_TARGET=starter (défaut) ou solution.

Les tests parlent au serveur comme un vrai client MCP (en mémoire) : ils lisent le drapeau `isError` du protocole.
"""
from __future__ import annotations

import json

import pytest

import shop_server
from helpers02 import TOOL_NAMES, mcp_compat, run, shop_backend, tool_defs

CATEGORIES = {"transient", "validation", "permission", "business"}


@pytest.fixture(autouse=True)
def fresh_backend():
    shop_server.BACKEND = shop_backend.ShopBackend()
    return shop_server.BACKEND


def call(name, **arguments):
    async def go():
        async with mcp_compat.in_memory_session(shop_server.server) as session:
            return await session.call_tool(name, arguments)

    return run(go())


def error_of(outcome):
    assert outcome.is_error, f"un échec prévisible doit lever le drapeau isError : {outcome.text[:120]}"
    payload = outcome.json()
    assert CATEGORIES >= {payload["errorCategory"]}
    assert isinstance(payload["isRetryable"], bool)
    assert payload["message"].strip() and payload["nextStep"].strip()
    return payload


# --- catalogue -------------------------------------------------------------------------------

def test_server_exposes_the_three_tools_with_the_descriptions_of_exercise_1():
    async def go():
        async with mcp_compat.in_memory_session(shop_server.server) as session:
            return await session.list_tools()

    tools = {t.name: t for t in run(go())}
    assert set(tools) == TOOL_NAMES
    for name, tool in tools.items():
        assert tool.description == tool_defs.DESCRIPTIONS[name]
    assert set(tools["lookup_order"].input_schema["required"]) == {"order_id", "customer_email"}


def test_status_glossary_is_published_as_a_resource():
    async def go():
        async with mcp_compat.in_memory_session(shop_server.server) as session:
            return await session.list_resources(), await session.read_resource("shop://status-glossary")

    uris, text = run(go())
    assert "shop://status-glossary" in uris
    assert set(json.loads(text)) == set(shop_backend.STATUS_GLOSSARY)


# --- lookup_order ----------------------------------------------------------------------------

def test_lookup_returns_the_order_to_its_owner():
    out = call("lookup_order", order_id="CMD-10002", customer_email="marie@example.com")
    assert not out.is_error
    assert out.json()["status"] == "shipped" and out.json()["items"] == ["Casque Bluetooth"]


def test_invalid_order_number_is_a_validation_error_that_says_how_to_fix_it():
    err = error_of(call("lookup_order", order_id="10002", customer_email="marie@example.com"))
    assert err["errorCategory"] == "validation" and err["isRetryable"] is False
    assert "CMD-" in err["nextStep"]


def test_invalid_email_is_a_validation_error():
    err = error_of(call("lookup_order", order_id="CMD-10002", customer_email="marie"))
    assert err["errorCategory"] == "validation"


def test_order_of_another_customer_is_a_permission_error_that_leaks_nothing():
    out = call("lookup_order", order_id="CMD-10003", customer_email="marie@example.com")
    err = error_of(out)
    assert err["errorCategory"] == "permission" and err["isRetryable"] is False
    leaked = out.text.lower()
    assert "paul" not in leaked and "housse" not in leaked and "45" not in leaked


def test_unknown_and_archived_orders_are_business_errors():
    unknown = error_of(call("lookup_order", order_id="CMD-99999", customer_email="marie@example.com"))
    archived = error_of(call("lookup_order", order_id="CMD-10005", customer_email="lea@example.com"))
    assert unknown["errorCategory"] == "business" and archived["errorCategory"] == "business"
    assert unknown["isRetryable"] is False and archived["isRetryable"] is False
    assert "support" in archived["nextStep"].lower()


def test_timeout_is_a_retryable_transient_error_and_the_retry_succeeds(fresh_backend):
    fresh_backend.fail_next("timeout")
    err = error_of(call("lookup_order", order_id="CMD-10002", customer_email="marie@example.com"))
    assert err["errorCategory"] == "transient" and err["isRetryable"] is True
    assert not call("lookup_order", order_id="CMD-10002", customer_email="marie@example.com").is_error


def test_unavailable_service_is_transient_for_every_tool(fresh_backend):
    fresh_backend.down = True
    for name, args in (
        ("lookup_order", {"order_id": "CMD-10002", "customer_email": "marie@example.com"}),
        ("find_orders", {"customer_email": "marie@example.com"}),
        ("search_orders", {"text": "casque"}),
    ):
        err = error_of(call(name, **args))
        assert err["errorCategory"] == "transient" and err["isRetryable"] is True, name


# --- find_orders -----------------------------------------------------------------------------

def test_find_orders_lists_the_orders_of_one_customer():
    out = call("find_orders", customer_email="marie@example.com")
    assert not out.is_error
    assert out.json()["count"] == 3
    assert {o["order_id"] for o in out.json()["orders"]} == {"CMD-10001", "CMD-10002", "CMD-10006"}


def test_find_orders_filters_by_status():
    out = call("find_orders", customer_email="paul@example.com", status="delivered")
    assert [o["order_id"] for o in out.json()["orders"]] == ["CMD-10004"]


def test_customer_without_orders_is_a_valid_empty_answer_not_an_error():
    out = call("find_orders", customer_email="nadia@example.com")
    assert out.is_error is False and out.json() == {"count": 0, "orders": []}


def test_find_orders_validates_its_inputs():
    assert error_of(call("find_orders", customer_email="pas-un-mail"))["errorCategory"] == "validation"
    assert error_of(call("find_orders", customer_email="marie@example.com", status="perdu"))["errorCategory"] == "validation"


# --- search_orders ---------------------------------------------------------------------------

def test_search_finds_items_without_exposing_customer_data():
    out = call("search_orders", text="casque")
    assert not out.is_error and out.json()["count"] == 2
    assert "@" not in out.text and "marie" not in out.text.lower()


def test_search_honours_the_date_range_and_returns_valid_empty_results():
    after = call("search_orders", text="casque", date_from="2026-10-10")
    assert [m["order_id"] for m in after.json()["matches"]] == ["CMD-10002"]
    none = call("search_orders", text="licorne")
    assert none.is_error is False and none.json()["count"] == 0


def test_search_validates_text_and_dates():
    assert error_of(call("search_orders", text=" "))["errorCategory"] == "validation"
    assert error_of(call("search_orders", text="casque", date_from="12/10/2026"))["errorCategory"] == "validation"
