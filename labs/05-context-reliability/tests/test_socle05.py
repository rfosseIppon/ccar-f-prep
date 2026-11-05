"""Intégrité du socle fourni (passe quelle que soit la cible)."""
from __future__ import annotations

import json

from helpers05 import LAB, escalation, fixtures05, reachable


def test_the_case_has_15_turns_and_the_three_critical_facts_come_early():
    ev = fixtures05.case_events()
    assert len(ev) == 15
    early = json.dumps(ev[:4], ensure_ascii=False)
    assert "O-1001" in early and "60 EUR" in early and "5 jours ouvrés" in early
    late = json.dumps(ev[4:], ensure_ascii=False)
    assert "5 jours ouvrés" not in late and "60 EUR" not in late


def test_the_history_is_a_valid_message_sequence():
    h = fixtures05.build_history(fixtures05.case_events())
    seen: set[str] = set()
    for m in h:
        if isinstance(m["content"], list):
            for b in m["content"]:
                if b["type"] == "tool_use":
                    seen.add(b["id"])
                if b["type"] == "tool_result":
                    assert b["tool_use_id"] in seen
    assert h[0]["role"] == "user" and isinstance(h[0]["content"], str)


def test_the_order_lookup_is_verbose_enough_to_need_trimming():
    assert len(json.dumps(fixtures05.LOOKUP_ORDER_VERBOSE)) > 2000


def test_the_fake_repository_has_520_files_and_the_dependency_graph_is_a_dag():
    assert len(fixtures05.DEPS) * fixtures05.FILES_PER_PACKAGE == 520
    for start in fixtures05.DEPS:
        for dep in fixtures05.DEPS[start]:
            assert start not in reachable(dep), f"cycle {start} <-> {dep}"
    assert len(reachable("payments")) < len(fixtures05.DEPS) / 2


def test_the_explorer_stand_in_reads_a_package_and_reports_its_dependencies(tmp_path):
    repo = fixtures05.make_repo(tmp_path / "r")
    assert len(list(repo.rglob("*.py"))) == 520
    deps, raw = fixtures05.explore_module(repo, "payments")
    assert deps == sorted(fixtures05.DEPS["payments"]) and raw > 20_000


def test_the_provided_human_request_heuristic():
    yes = ["Je veux parler à un conseiller", "Passez-moi un humain", "Can I speak to a human?", "I want a real person", "Je voudrais parler à quelqu'un"]
    no = ["Où est ma commande ?", "Je n'ai pas besoin d'un conseiller", "Merci pour votre aide", "Le conseiller précédent était sympa"]
    assert all(escalation.asks_for_human(t) for t in yes), [t for t in yes if not escalation.asks_for_human(t)]
    assert not any(escalation.asks_for_human(t) for t in no), [t for t in no if escalation.asks_for_human(t)]


def test_the_lab_ships_both_targets():
    for t in ("starter", "solution"):
        for f in ("case_facts", "escalation", "partial_failure", "exploration"):
            assert (LAB / t / f"{f}.py").exists()
