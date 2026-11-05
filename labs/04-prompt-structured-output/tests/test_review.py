"""Tests hors ligne des exercices 4 et 6 (revue de code). LAB_TARGET=starter (défaut) ou solution.

Les contrôles sur le texte de la consigne sont des garde-fous grossiers, pas une mesure de sa qualité :
la qualité se mesure avec un vrai modèle (run_review.py).
"""
from __future__ import annotations

import json

from helpers import FakeClient, reply, review, scoring, tool_use

CASE = scoring.load_review_case()


def findings_reply(*findings):
    return reply(tool_use("report_findings", findings=list(findings)))


def finding(file, category, severity="high", confidence=0.9, line=1):
    return {"file": file, "line": line, "category": category, "severity": severity, "confidence": confidence, "explanation": "x"}


# --- exercice 4 : consigne ---------------------------------------------------------------------

def prompt():
    text = review.REVIEW_PROMPT
    assert not text.startswith("TODO"), "la consigne de revue est encore le texte de départ"
    return text.lower()


def test_prompt_names_what_to_report_and_what_to_ignore():
    text = prompt()
    assert "bug" in text and "security" in text
    assert "ignorer" in text and "style" in text


def test_prompt_defines_three_severity_levels():
    text = prompt()
    assert all(level in text for level in ("high", "medium", "low"))


def test_prompt_has_two_to_four_few_shot_examples_with_their_reason():
    text = review.REVIEW_PROMPT
    n = text.count("<example>")
    assert 2 <= n <= 4
    assert text.count("<why>") == n


def test_prompt_allows_an_empty_answer():
    assert "liste vide" in prompt() or "aucun constat" in prompt()


# --- exercice 6 : passes -----------------------------------------------------------------------

def test_review_file_uses_a_fresh_conversation_with_only_its_own_diff():
    client = FakeClient([findings_reply(finding("a.py", "bug"))])
    out = review.review_file(client, "a.py", "DIFF-A")
    assert out[0]["file"] == "a.py"
    call = client.calls[0]
    assert len(call["messages"]) == 1 and call["messages"][0]["role"] == "user"
    assert "DIFF-A" in str(call["messages"])
    assert call["tools"][0]["name"] == "report_findings"


def make_pr_client():
    return FakeClient(
        [
            findings_reply(),  # billing.py : rien en local
            findings_reply(finding("invoice_api.py", "security", "high", 0.95, 12)),
            findings_reply(),  # utils.py : style ignoré
            findings_reply(finding("invoice_api.py", "cross_file", "high", 0.6, 10)),  # intégration, confiance faible
        ]
    )


def test_review_in_passes_runs_one_pass_per_file_then_an_integration_pass():
    client = make_pr_client()
    report = review.review_in_passes(client, CASE["files"])
    assert len(client.calls) == len(CASE["files"]) + 1
    local_calls, integration_call = client.calls[:-1], client.calls[-1]
    names = list(CASE["files"])
    for name, call in zip(names, local_calls):
        text = str(call["messages"])
        assert name in text
        for other in names:
            if other != name:
                assert CASE["files"][other] not in text, "une passe locale ne voit que son fichier"
    integration_text = str(integration_call["messages"])
    assert all(name in integration_text for name in names)
    assert "SELECT * FROM clients" in integration_text
    assert "security" in integration_text, "les constats locaux sont transmis à la passe d'intégration"
    assert all(len(c["messages"]) == 1 for c in client.calls), "chaque passe démarre d'une conversation neuve"


def test_review_in_passes_sorts_and_routes_low_confidence_to_a_human():
    report = review.review_in_passes(make_pr_client(), CASE["files"], confidence_threshold=0.7)
    assert [f["category"] for f in report.findings] == ["security", "cross_file"]  # high d'abord, confiance décroissante
    assert [f["category"] for f in report.needs_human] == ["cross_file"]


def test_review_in_passes_sorts_by_severity_then_confidence_whatever_the_arrival_order():
    client = FakeClient(
        [
            findings_reply(finding("billing.py", "bug", "low", 0.99, 3)),
            findings_reply(finding("invoice_api.py", "bug", "medium", 0.8, 5), finding("invoice_api.py", "security", "high", 0.75, 12)),
            findings_reply(finding("utils.py", "bug", "medium", 0.95, 2)),
            findings_reply(finding("invoice_api.py", "cross_file", "high", 0.9, 10)),
        ]
    )
    report = review.review_in_passes(client, CASE["files"])
    assert [(f["severity"], f["confidence"]) for f in report.findings] == [
        ("high", 0.9), ("high", 0.75), ("medium", 0.95), ("medium", 0.8), ("low", 0.99),
    ]


def test_review_in_passes_removes_duplicates():
    dup = finding("invoice_api.py", "security", "high", 0.9, 12)
    client = FakeClient([findings_reply(dup), findings_reply(dup), findings_reply(), findings_reply(dup)])
    report = review.review_in_passes(client, CASE["files"])
    assert len(report.findings) == 1


def test_scoring_of_findings_against_the_expected_ones():
    perfect = [finding("invoice_api.py", "security"), finding("invoice_api.py", "cross_file")]
    assert scoring.score_findings(perfect, CASE["expected"]) == {"precision": 1.0, "recall": 1.0, "false_positives": [], "missed": []}
    noisy = perfect + [finding("utils.py", "bug", "low", 0.5)]
    scored = scoring.score_findings(noisy, CASE["expected"])
    assert scored["recall"] == 1.0 and scored["precision"] < 1.0 and scored["false_positives"] == [("utils.py", "bug")]
    local_only = [finding("invoice_api.py", "security")]
    assert scoring.score_findings(local_only, CASE["expected"])["missed"] == [("invoice_api.py", "cross_file")]
