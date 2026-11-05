"""Exercice 3 : panne partielle, provenance, contradictions."""
from __future__ import annotations

import pytest

from helpers05 import partial_failure as pf

C = pf.Claim


def src(name, text, date="2026-10-01", metric="", value=None):
    return C(text, name, f"https://{name}.example/page", date, metric, value)


# --- reprise locale ----------------------------------------------------------------------------------------------

def flaky(fail_times, exc=TimeoutError("délai dépassé"), then=None):
    state = {"n": 0}

    def fetch():
        state["n"] += 1
        if state["n"] <= fail_times:
            raise exc
        return then if then is not None else [src("a", "fait")]

    fetch.state = state
    return fetch


def test_a_transient_error_is_retried_locally_then_succeeds():
    fetch = flaky(2)
    r = pf.run_with_recovery("a", fetch, max_attempts=3)
    assert (r.status, r.attempts, len(r.claims)) == ("ok", 3, 1) and fetch.state["n"] == 3


def test_a_persistent_transient_error_is_reported_with_what_was_tried():
    fetch = flaky(99)
    r = pf.run_with_recovery("a", fetch, max_attempts=3)
    assert (r.status, r.attempts, r.claims) == ("timeout", 3, []) and "TimeoutError" in r.error and "délai dépassé" in r.error
    assert fetch.state["n"] == 3, "pas une tentative de plus que le plafond"


@pytest.mark.parametrize("exc", [PermissionError("403"), FileNotFoundError("404"), ValueError("format")])
def test_a_non_transient_error_is_not_retried(exc):
    fetch = flaky(99, exc)
    r = pf.run_with_recovery("a", fetch, max_attempts=3)
    assert r.status == "unreachable" and r.attempts == 1 and fetch.state["n"] == 1 and type(exc).__name__ in r.error


def test_an_empty_answer_is_a_valid_result_not_a_failure():
    r = pf.run_with_recovery("a", lambda: [], max_attempts=3)
    assert (r.status, r.error, r.attempts) == ("empty", "", 1)


def test_connection_errors_count_as_transient():
    assert pf.run_with_recovery("a", flaky(99, ConnectionError("reset")), 2).status == "timeout"


# --- contradictions ----------------------------------------------------------------------------------------------

def test_different_values_from_different_sources_are_a_conflict_not_a_choice():
    a = src("insee", "Population : 67,8 M", "2024-01-01", "population_fr", 67.8)
    b = src("onu", "Population : 68,4 M", "2025-07-01", "population_fr", 68.4)
    k = pf.find_conflicts([a, b])
    assert len(k) == 1 and k[0].metric == "population_fr" and set(k[0].claims) == {a, b} and k[0].same_period is False


def test_same_date_conflict_is_flagged_as_same_period():
    a = src("x", "t", "2025-01-01", "m", 1.0)
    b = src("y", "t", "2025-01-01", "m", 2.0)
    assert pf.find_conflicts([a, b])[0].same_period is True


def test_no_conflict_when_values_agree_sources_agree_or_claims_are_unsourced():
    assert pf.find_conflicts([src("x", "t", metric="m", value=1.0), src("y", "t", metric="m", value=1.0)]) == []
    assert pf.find_conflicts([src("x", "t", "2025-01-01", "m", 1.0), src("x", "t", "2026-01-01", "m", 2.0)]) == [], "une même source qui se met à jour"
    assert pf.find_conflicts([src("x", "t", metric="m", value=1.0), C("t", metric="m", value=2.0)]) == []
    assert pf.find_conflicts([src("x", "t"), src("y", "t")]) == []


# --- rapport -----------------------------------------------------------------------------------------------------

def scenario():
    return [
        pf.SubResult("registre", "ok", [src("registre", "Société fondée en 2009", "2026-09-30"), src("registre", "Siège à Paris", "2026-09-30")]),
        pf.SubResult("presse", "empty"),
        pf.SubResult("api-finance", "timeout", [], "TimeoutError: délai dépassé", attempts=3),
        pf.SubResult("base-interne", "unreachable", [], "PermissionError: 403"),
        pf.SubResult("rapport-annuel", "ok", [src("rapport-annuel", "Effectif : 250", "2025-12-31", "effectif", 250.0)]),
        pf.SubResult("linkedin", "ok", [src("linkedin", "Effectif : 310", "2026-09-01", "effectif", 310.0)]),
    ]


def sections(report):
    return {line[3:].split(" (")[0]: i for i, line in enumerate(report.splitlines()) if line.startswith("## ")}


def test_the_report_opens_with_the_coverage_then_confirmed_then_gaps():
    r = pf.build_report("Dossier ACME", scenario())
    assert r.splitlines()[0].startswith("# Dossier ACME")
    assert "4 source(s) consultée(s) sur 6" in "\n".join(r.splitlines()[:4]), "la couverture doit être en tête"
    s = sections(r)
    assert s["Confirmé"] < s["Contradictions"] < s["Lacunes"]


def test_every_confirmed_claim_carries_its_source_url_and_date():
    r = pf.build_report("Q", scenario())
    confirmed = r.split("## Confirmé")[1].split("## ")[0]
    for text, name, date in [("Société fondée en 2009", "registre", "2026-09-30"), ("Siège à Paris", "registre", "2026-09-30")]:
        line = next(l for l in confirmed.splitlines() if text in l)
        assert f"source : {name}" in line and f"https://{name}.example/page" in line and date in line


def test_a_conflict_shows_both_values_with_their_sources_and_dates_and_picks_none():
    r = pf.build_report("Q", scenario())
    confirmed = r.split("## Confirmé")[1].split("## ")[0]
    assert "Effectif" not in confirmed, "une affirmation contestée n'est pas « confirmée »"
    conflict = r.split("## Contradictions")[1].split("## ")[0]
    assert "Effectif : 250" in conflict and "rapport-annuel" in conflict and "2025-12-31" in conflict
    assert "Effectif : 310" in conflict and "linkedin" in conflict and "2026-09-01" in conflict
    assert "périodes différentes" in conflict


def test_failures_appear_only_under_gaps_with_their_reason_and_never_with_claims():
    r = pf.build_report("Q", scenario())
    before_gaps, gaps = r.split("## Lacunes")
    assert "api-finance" not in before_gaps and "base-interne" not in before_gaps
    uncovered = gaps.split("### À retenter")[0]
    retry = gaps.split("### À retenter")[1]
    assert "base-interne" in uncovered and "PermissionError: 403" in uncovered and "api-finance" not in uncovered
    assert "api-finance" in retry and "3 tentative(s)" in retry and "TimeoutError" in retry and "base-interne" not in retry


def test_an_empty_source_is_reported_as_absence_of_result_not_as_a_gap():
    r = pf.build_report("Q", scenario())
    assert "presse" in r.split("## Lacunes")[0]
    assert "absence de résultat" in r.split("## Lacunes")[0]
    assert "presse" not in r.split("## Lacunes")[1]


def test_unsourced_claims_are_set_apart_not_confirmed():
    res = [pf.SubResult("blog", "ok", [C("Rumeur de rachat"), src("blog", "Fait vérifiable")])]
    r = pf.build_report("Q", res)
    assert "Rumeur de rachat" not in r.split("## Confirmé")[1].split("## ")[0]
    assert "Rumeur de rachat" in r.split("## Non vérifié")[1].split("## ")[0]
    assert "Fait vérifiable" in r.split("## Confirmé")[1].split("## ")[0]


def test_when_everything_fails_the_report_says_so_and_invents_nothing():
    res = [pf.SubResult("a", "timeout", [], "TimeoutError: x", 3), pf.SubResult("b", "unreachable", [], "PermissionError: 403")]
    r = pf.build_report("Q", res)
    assert "Aucun constat confirmé." in r and "0 source(s) consultée(s) sur 2" in r
    assert "- a :" in r and "- b :" in r


def test_the_empty_gap_sections_are_explicit():
    r = pf.build_report("Q", [pf.SubResult("a", "ok", [src("a", "fait")])])
    gaps = r.split("## Lacunes")[1]
    assert gaps.count("- aucune") == 2, "les deux sous-rubriques restent visibles, même vides"
    assert "## Contradictions" not in r and "## Non vérifié" not in r


def test_the_report_is_deterministic():
    assert pf.build_report("Q", scenario()) == pf.build_report("Q", scenario())
