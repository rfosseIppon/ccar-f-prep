"""Intégrité du socle fourni (passe quelle que soit la cible)."""
from __future__ import annotations

import collections

import pytest

from helpers02 import TOOL_NAMES, baseline, builtin_tasks, mcp_compat, selection, shop_backend, tools15


def test_twenty_queries_with_a_known_expected_tool():
    queries = selection.load_queries()
    assert len(queries) == 20
    assert len({q["id"] for q in queries}) == 20
    counts = collections.Counter(q["expected"] for q in queries)
    assert set(counts) == TOOL_NAMES and min(counts.values()) >= 5


def test_baseline_descriptions_are_vague_on_purpose():
    assert all(len(d.split()) < 6 for d in baseline.VAGUE_DESCRIPTIONS.values())
    assert [t["name"] for t in baseline.BASELINE_TOOLS] == ["search_orders", "find_orders", "lookup_order"]


def test_backend_can_be_made_to_fail_on_demand():
    backend = shop_backend.ShopBackend()
    backend.fail_next("timeout")
    with pytest.raises(shop_backend.BackendTimeout):
        backend.get_order("CMD-10001")
    assert backend.get_order("CMD-10001")["customer"] == "marie@example.com"
    backend.down = True
    with pytest.raises(shop_backend.BackendUnavailable):
        backend.orders_of("marie@example.com")


def test_backend_hides_archived_orders_from_lists_and_search():
    backend = shop_backend.ShopBackend()
    assert backend.orders_of("lea@example.com") == []
    assert backend.search_items("clavier") == []
    assert backend.get_order("CMD-10005")["status"] == "archived"


def test_error_and_ok_results_carry_the_mcp_error_flag():
    # `isError` en v1, `is_error` en v2 côté Python ; sur le fil, le nom est le même.
    assert mcp_compat.error_result({"a": 1}).model_dump(by_alias=True)["isError"] is True
    assert mcp_compat.ok_result({"a": 1}).model_dump(by_alias=True)["isError"] is False


def test_tools15_and_builtin_tasks_are_consistent():
    assert len(tools15.TOOLS_15) == 15 and len({n for n, _, _ in tools15.TOOLS_15}) == 15
    assert set(builtin_tasks.TASKS) == set(builtin_tasks.ACCEPTED)
    assert all(a <= builtin_tasks.ALLOWED for a in builtin_tasks.ACCEPTED.values())
