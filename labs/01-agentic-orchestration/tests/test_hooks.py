"""Tests hors ligne de l'exercice 4 (hooks). LAB_TARGET=starter (défaut) ou solution."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parent.parent
TARGET = os.environ.get("LAB_TARGET", "starter")
_spec = importlib.util.spec_from_file_location("hooks_under_test", LAB / TARGET / "hooks.py")
hooks = importlib.util.module_from_spec(_spec)
sys.modules["hooks_under_test"] = hooks
_spec.loader.exec_module(hooks)


def run(coro):
    return asyncio.run(coro)


def pre(tool_name, **tool_input):
    return {"hook_event_name": "PreToolUse", "tool_name": tool_name, "tool_input": tool_input, "tool_use_id": "t1"}


def post(tool_name, response):
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": tool_name,
        "tool_input": {},
        "tool_response": response,
        "tool_use_id": "t1",
    }


def updated(out):
    return out["hookSpecificOutput"]["updatedToolOutput"]


# --- PreToolUse ---------------------------------------------------------------

def test_pre_hook_denies_refund_over_limit():
    out = run(hooks.block_large_refund(pre("mcp__support__process_refund", order_id="O-1002", amount_eur=250.0), "t1", None))
    decision = out["hookSpecificOutput"]
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    assert "escalate_to_human" in decision["permissionDecisionReason"]


def test_pre_hook_allows_refund_within_limit():
    out = run(hooks.block_large_refund(pre("mcp__support__process_refund", order_id="O-1001", amount_eur=42.0), "t1", None))
    assert out == {}


def test_pre_hook_accepts_unprefixed_tool_name():
    out = run(hooks.block_large_refund(pre("process_refund", order_id="O-1002", amount_eur=250.0), "t1", None))
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_pre_hook_ignores_other_tools():
    out = run(hooks.block_large_refund(pre("mcp__support__lookup_order", order_id="O-1002"), "t1", None))
    assert out == {}


# --- PostToolUse --------------------------------------------------------------

def test_post_hook_converts_unix_timestamps_to_iso():
    out = run(hooks.normalize_tool_result(post("mcp__support__lookup_order", {"order_id": "O-1", "created_at": 1767225600}), "t1", None))
    assert updated(out)["created_at"] == "2026-01-01T00:00:00Z"
    assert updated(out)["order_id"] == "O-1"


def test_post_hook_handles_milliseconds_and_nested_data():
    response = {"orders": [{"order_id": "O-1", "shipped_at": 1767225600000}]}
    out = run(hooks.normalize_tool_result(post("mcp__support__lookup_order", response), "t1", None))
    assert updated(out)["orders"][0]["shipped_at"] == "2026-01-01T00:00:00Z"


def test_post_hook_converts_status_codes_to_labels():
    out = run(hooks.normalize_tool_result(post("mcp__support__lookup_order", {"order_id": "O-1", "status_code": 2}), "t1", None))
    assert updated(out) == {"order_id": "O-1", "status": "delivered"}


def test_post_hook_leaves_clean_results_untouched():
    clean = {"order_id": "O-1", "created_at": "2026-01-01T00:00:00Z", "status": "delivered"}
    assert run(hooks.normalize_tool_result(post("mcp__support__lookup_order", clean), "t1", None)) == {}


def test_post_hook_does_not_touch_small_numbers_or_booleans():
    response = {"quantity_at": 3, "flag_date": True}
    assert run(hooks.normalize_tool_result(post("mcp__support__lookup_order", response), "t1", None)) == {}


def test_post_hook_handles_json_strings_and_plain_text():
    as_json = json.dumps({"created_at": 1767225600})
    out = run(hooks.normalize_tool_result(post("mcp__support__lookup_order", as_json), "t1", None))
    assert json.loads(updated(out)) == {"created_at": "2026-01-01T00:00:00Z"}
    assert run(hooks.normalize_tool_result(post("mcp__support__lookup_order", "Commande introuvable"), "t1", None)) == {}


# --- branchement --------------------------------------------------------------

def test_build_hooks_registers_both_events():
    pytest.importorskip("claude_agent_sdk")
    built = hooks.build_hooks()
    assert set(built) == {"PreToolUse", "PostToolUse"}
    pre_matcher = built["PreToolUse"][0]
    assert pre_matcher.matcher.endswith("process_refund")
    assert hooks.block_large_refund in pre_matcher.hooks
    assert hooks.normalize_tool_result in built["PostToolUse"][0].hooks
