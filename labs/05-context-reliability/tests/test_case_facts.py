"""Exercice 1 : faits critiques, troncature de l'historique, sorties d'outils réduites."""
from __future__ import annotations

import json
from types import SimpleNamespace as NS

import pytest

from helpers05 import case_facts as cf
from helpers05 import fixtures05 as fx


def ledger_after_the_case() -> cf.FactsLedger:
    led = cf.FactsLedger()
    fx.replay(fx.case_events(), led)
    return led


# --- registre --------------------------------------------------------------------------------------------------

def test_a_newer_fact_replaces_the_older_one_and_keeps_its_trace():
    led = cf.FactsLedger()
    led.record("amount_discussed_eur", "80 EUR", "agent", 2)
    led.record("amount_discussed_eur", "60 EUR", "agent", 3)
    assert led.get("amount_discussed_eur") == "60 EUR"
    assert "remplace : 80 EUR" in led.render()


def test_recording_the_same_value_again_changes_nothing():
    led = cf.FactsLedger()
    led.record("order_id", "O-1001", "outil lookup_order", 1)
    led.record("order_id", "O-1001", "outil lookup_order", 9)
    assert "tour 1" in led.render() and "tour 9" not in led.render() and "remplace" not in led.render()


def test_a_long_value_is_clipped():
    led = cf.FactsLedger()
    led.record("commitment", "x" * 500, "agent", 1)
    v = led.get("commitment")
    assert len(v) == cf.MAX_VALUE_CHARS and v.endswith("…")
    assert led.get("absent") is None


def test_tool_results_are_captured_automatically():
    led = cf.FactsLedger()
    led.capture_tool_result("get_customer", {"email": "a@b.c"}, {"customer_id": "C-77"}, 1)
    led.capture_tool_result("lookup_order", {"order_id": "O-1"}, {"order_id": "O-1", "status": "delivered", "total_eur": 5}, 1)
    led.capture_tool_result("process_refund", {}, {"refund_id": "R-9"}, 2)
    led.capture_tool_result("escalate_to_human", {"reason": "refund_over_limit", "summary": "s"}, {"ticket": "T-1"}, 3)
    assert [led.get(k) for k in ("customer_id", "order_id", "order_status", "refund_id", "escalation")] == [
        "C-77", "O-1", "delivered", "R-9", "refund_over_limit"]
    assert "outil get_customer" in led.render()


def test_an_error_result_records_nothing():
    led = cf.FactsLedger()
    led.capture_tool_result("lookup_order", {"order_id": "O-X"}, {"isError": True, "order_id": "O-X", "message": "introuvable"}, 1)
    assert led.get("order_id") is None


def test_an_unknown_tool_result_records_nothing():
    led = cf.FactsLedger()
    led.capture_tool_result("weather", {}, {"customer_id": "ZZ"}, 1)
    assert led.keys() == []


def test_note_fact_accepts_a_known_key_and_rejects_the_others_with_a_way_out():
    led = cf.FactsLedger()
    assert led.handle_note_fact({"key": "commitment", "value": "Rappel jeudi"}, 4) == {"ok": True, "key": "commitment"}
    assert led.get("commitment") == "Rappel jeudi"
    bad = led.handle_note_fact({"key": "mood", "value": "énervé"}, 5)
    assert bad["isError"] is True and bad["retryable"] is False and bad["category"] == "validation"
    assert all(k in bad["message"] for k in cf.NOTE_KEYS), "le message doit citer les clés autorisées"
    assert led.get("mood") is None
    empty = led.handle_note_fact({"key": "commitment", "value": "  "}, 6)
    assert empty["isError"] is True and led.get("commitment") == "Rappel jeudi"


def test_the_note_fact_tool_description_says_when_what_and_what_not():
    d = cf.NOTE_FACT_TOOL["description"].lower()
    assert len(d.split()) >= 25, "trop courte pour orienter le choix de l'outil"
    assert "montant" in d and "engagement" in d, "donnez des exemples de faits"
    assert any(p in d for p in ("ne sert pas", "n'est pas pour", "pas à consigner", "ne pas utiliser")), "dites ce qui n'est pas pour cet outil"
    assert cf.NOTE_FACT_TOOL["input_schema"]["properties"]["key"]["enum"] == list(cf.NOTE_KEYS)


def test_render_is_ordered_stable_and_delimited():
    led = cf.FactsLedger()
    led.record("mmm_custom", "m", "agent", 1)
    led.record("zzz_custom", "z", "agent", 1)
    led.record("aaa_custom", "a", "agent", 1)
    led.record("commitment", "c", "agent", 1)
    led.record("customer_id", "C-1", "outil get_customer", 1)
    text = led.render()
    assert text.startswith("<case_facts>") and text.endswith("</case_facts>")
    assert text.index("customer_id") < text.index("commitment") < text.index("aaa_custom") < text.index("mmm_custom") < text.index("zzz_custom")
    assert led.render() == text, "un bloc stable d'un tour à l'autre"


def test_an_empty_ledger_still_renders_a_valid_block():
    text = cf.FactsLedger().render()
    assert text.startswith("<case_facts>") and text.endswith("</case_facts>")


# --- les trois faits après 15 tours ------------------------------------------------------------------------------

def test_the_three_critical_facts_are_exact_after_15_turns_even_when_the_history_is_truncated():
    ev = fx.case_events()
    led = ledger_after_the_case()
    history = fx.build_history(ev)
    req = cf.build_request("Tu es l'agent de support.", led, history, keep_last_turns=4)
    kept = cf.to_json(req["messages"])
    # le piège : l'historique tronqué a perdu le montant et l'engagement...
    assert "5 jours ouvrés" not in kept and "un article abîmé" not in kept
    # ... mais le bloc de faits les restitue exactement
    for exact in ("O-1001", "C-77", "60 EUR (un article abîmé)", "Remboursement de 60 EUR sous 5 jours ouvrés, confirmation par e-mail"):
        assert exact in req["system"], exact
    assert "remplace : 80 EUR demandés" in req["system"]


def test_the_facts_come_right_after_the_instructions_not_buried_in_the_history():
    led = ledger_after_the_case()
    req = cf.build_request("CONSIGNES", led, fx.build_history(fx.case_events()), 4)
    assert req["system"].startswith("CONSIGNES")
    assert req["system"].index("CONSIGNES") < req["system"].index("<case_facts>")
    assert "<case_facts>" not in cf.to_json(req["messages"])


def test_the_request_is_much_smaller_than_the_full_history():
    led = ledger_after_the_case()
    history = fx.build_history(fx.case_events())
    req = cf.build_request("S", led, history, 4)
    assert len(cf.to_json(req["messages"])) + len(req["system"]) < 0.5 * len(cf.to_json(history))


# --- troncature --------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("keep", range(1, 16))
def test_truncation_keeps_whole_turns_and_never_orphans_a_tool_result(keep):
    history = fx.build_history(fx.case_events())
    kept = cf.truncate_history(history, keep)
    assert kept[0]["role"] == "user" and isinstance(kept[0]["content"], str), "doit commencer par un message utilisateur"
    starts = [m for m in kept if m["role"] == "user" and isinstance(m["content"], str)]
    assert len(starts) == keep
    seen: set[str] = set()
    for m in kept:
        if isinstance(m["content"], list):
            for b in m["content"]:
                if b["type"] == "tool_use":
                    seen.add(b["id"])
                if b["type"] == "tool_result":
                    assert b["tool_use_id"] in seen, f"tool_result orphelin : {b['tool_use_id']}"
    assert kept == history[len(history) - len(kept):], "on garde la fin de l'historique, sans le réécrire"


def test_a_short_history_is_kept_whole_and_zero_keeps_nothing():
    history = fx.build_history(fx.case_events()[:3])
    assert cf.truncate_history(history, 10) == history
    assert cf.truncate_history(history, 0) == []


def test_truncation_accepts_sdk_style_blocks():
    history = [
        {"role": "user", "content": "q1"},
        {"role": "assistant", "content": [NS(type="tool_use", id="a", name="t", input={})]},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "a", "content": "{}"}]},
        {"role": "assistant", "content": [NS(type="text", text="r1")]},
        {"role": "user", "content": [{"type": "text", "text": "q2"}]},
        {"role": "assistant", "content": [NS(type="text", text="r2")]},
    ]
    kept = cf.truncate_history(history, 1)
    assert kept == history[4:], "un message utilisateur en blocs de texte ouvre un tour"
    assert cf.truncate_history(history, 2) == history


# --- sorties d'outils --------------------------------------------------------------------------------------------

def test_a_verbose_tool_result_is_reduced_to_the_useful_fields():
    full = fx.LOOKUP_ORDER_VERBOSE
    small = cf.trim_tool_output(full, ("order_id", "status", "total_eur", "items", "absent"), max_items=3)
    assert set(small) == {"order_id", "status", "total_eur", "items", "items_truncated"}
    assert small["items"] == full["items"][:3] and small["items_truncated"] == "9 éléments omis sur 12"
    assert "internal_notes" not in small and "audit_trail" not in small
    assert len(json.dumps(small)) < 0.25 * len(json.dumps(full))


def test_a_short_list_is_not_marked_as_truncated():
    small = cf.trim_tool_output({"items": [1, 2], "x": 1}, ("items",), max_items=5)
    assert small == {"items": [1, 2]}
