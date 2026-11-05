"""Exercice 4 : exploration d'un gros dépôt."""
from __future__ import annotations

import json

from helpers05 import exploration as ex
from helpers05 import fixtures05 as fx
from helpers05 import reachable, run_exploration


# --- notes -------------------------------------------------------------------------------------------------------

def test_notes_are_appended_one_per_line_and_never_rewritten(tmp_path):
    pad = ex.Scratchpad(tmp_path / "n.jsonl")
    pad.add("p1", "api appelle payments")
    first = (tmp_path / "n.jsonl").read_text(encoding="utf-8")
    pad.add("p2", "payments appelle billing")
    text = (tmp_path / "n.jsonl").read_text(encoding="utf-8")
    assert text.startswith(first) and len(text.splitlines()) == 2
    assert [json.loads(l)["phase"] for l in text.splitlines()] == ["p1", "p2"]


def test_notes_survive_a_context_loss_because_they_live_in_a_file(tmp_path):
    ex.Scratchpad(tmp_path / "n.jsonl").add("p1", "api appelle payments")
    reborn = ex.Scratchpad(tmp_path / "n.jsonl")  # nouvelle session, nouvel objet
    assert reborn.entries() == [{"phase": "p1", "finding": "api appelle payments"}]


def test_no_file_means_no_notes(tmp_path):
    pad = ex.Scratchpad(tmp_path / "absent.jsonl")
    assert pad.entries() == [] and pad.render() == "(aucune note)"


def test_render_is_chronological_and_drops_the_oldest_when_short_of_space(tmp_path):
    pad = ex.Scratchpad(tmp_path / "n.jsonl")
    for i in range(5):
        pad.add(f"p{i}", f"note numéro {i} " + "x" * 30)
    full = pad.render().splitlines()
    assert full[0].startswith("- [p0]") and full[-1].startswith("- [p4]")
    short = pad.render(max_chars=120).splitlines()
    assert 0 < len(short) < 5 and short[-1].startswith("- [p4]") and not any("[p0]" in l for l in short)
    assert len(pad.render(max_chars=120)) <= 120


def test_unicode_notes_round_trip(tmp_path):
    pad = ex.Scratchpad(tmp_path / "n.jsonl")
    pad.add("é", "dépendance « résolue » ✓")
    assert pad.entries()[0]["finding"] == "dépendance « résolue » ✓"


# --- synthèses et consignes --------------------------------------------------------------------------------------

def test_a_short_synthesis_is_kept_with_normalised_spaces():
    assert ex.bound_synthesis("  api   appelle\npayments. ") == "api appelle payments."


def test_a_long_synthesis_is_cut_below_the_limit_with_a_marker_at_a_sentence_end():
    text = ". ".join(f"Phrase numéro {i} qui décrit un module" for i in range(80)) + "."
    out = ex.bound_synthesis(text, 300)
    assert len(out) <= 300 and out.endswith("[tronqué]")
    body = out[: -len(" [tronqué]")]
    assert body.endswith("."), "coupure à une fin de phrase"


def test_a_long_text_without_punctuation_is_still_bounded():
    out = ex.bound_synthesis("mot " * 1000, 100)
    assert len(out) <= 100 and out.endswith("[tronqué]")


def test_the_brief_is_self_contained_and_reads_the_scratchpad(tmp_path):
    pad = ex.Scratchpad(tmp_path / "n.jsonl")
    pad.add("p1", "api appelle payments")
    brief = ex.phase_brief(pad, "p2", "Qui dépend de billing ?", "payments")
    for needed in ("Qui dépend de billing ?", "p2", "payments", "api appelle payments", str(ex.MAX_SYNTHESIS_CHARS)):
        assert needed in brief, needed


def test_the_brief_of_a_new_session_includes_what_the_previous_one_found(tmp_path):
    ex.Scratchpad(tmp_path / "n.jsonl").add("p1", "découverte capitale")
    brief = ex.phase_brief(ex.Scratchpad(tmp_path / "n.jsonl"), "p2", "Q", "m")
    assert "découverte capitale" in brief


# --- décomposition adaptative ------------------------------------------------------------------------------------

F = ex.Finding


def test_next_subtasks_follow_what_was_discovered_most_cited_first():
    findings = [F("api", ["auth", "orders", "payments"]), F("orders", ["models", "billing"]), F("payments", ["billing", "db"])]
    assert ex.next_subtasks(findings, {"api", "orders", "payments"}, 10) == ["billing", "auth", "db", "models"]


def test_explored_modules_are_never_proposed_again_and_the_budget_is_respected():
    findings = [F("a", ["b", "c", "d"]), F("b", ["c"])]
    assert ex.next_subtasks(findings, {"a", "b"}, 1) == ["c"]
    assert ex.next_subtasks(findings, {"a", "b", "c"}, 5) == ["d"]
    assert ex.next_subtasks(findings, {"a", "b", "c", "d"}, 5) == []
    assert ex.next_subtasks(findings, set(), 0) == []
    assert ex.next_subtasks([], set(), 3) == []


def test_a_dependency_cycle_cannot_make_the_exploration_loop_forever():
    findings = [F("a", ["b"]), F("b", ["a"])]
    assert ex.next_subtasks(findings, {"a", "b"}, 3) == []


def test_nothing_new_discovered_means_nothing_to_do():
    assert ex.next_subtasks([F("a", [])], {"a"}, 3) == []


# --- exploration complète sur 520 fichiers -----------------------------------------------------------------------

def test_adaptive_exploration_of_520_files_follows_the_dependencies_and_keeps_the_main_context_small(tmp_path):
    repo = fx.make_repo(tmp_path / "repo")
    explored, raw, returned = run_exploration(repo, "payments", tmp_path, budget=2)
    assert explored == reachable("payments"), "tout ce qui est atteignable, et rien d'autre"
    assert len(explored) < len(fx.DEPS)
    assert raw > 100_000, "volume réellement lu par les sous-agents"
    assert returned < 0.1 * raw, "le contexte principal ne reçoit que des synthèses"


def test_the_exploration_notes_cover_every_explored_module(tmp_path):
    repo = fx.make_repo(tmp_path / "repo")
    explored, _, _ = run_exploration(repo, "orders", tmp_path, budget=1)
    notes = ex.Scratchpad(tmp_path / "notes.jsonl").entries()
    assert len(notes) == len(explored)
    assert {n["finding"].split()[0] for n in notes} == explored
