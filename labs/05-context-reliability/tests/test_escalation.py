"""Exercice 2 : règles d'escalade et résumé de transfert."""
from __future__ import annotations

import pytest

from helpers05 import case_facts as cf
from helpers05 import escalation as es
from helpers05 import fixtures05 as fx

T, S = es.Turn, es.CaseState

CASES = [
    # (id, tour, état, (action, motif))
    ("demande explicite", T("Je veux parler à un conseiller"), S(), ("escalate", "customer_request")),
    ("demande explicite en anglais", T("Can I speak to a human?"), S(), ("escalate", "customer_request")),
    ("demande explicite avant l'enquête", T("Passez-moi un humain", matched_customers=3, refund_amount_eur=500), S(), ("escalate", "customer_request")),
    ("plusieurs clients", T("Mon nom est Martin", matched_customers=2), S(), ("ask_clarification", "multiple_matches")),
    ("un seul client", T("Mon nom est Martin", matched_customers=1), S(), ("continue", "")),
    ("pas de recherche", T("Où est mon colis ?"), S(), ("continue", "")),
    ("plafond dépassé", T("Remboursez 150 EUR", request_kind="refund", refund_amount_eur=150), S(), ("escalate", "refund_over_limit")),
    ("plafond exact", T("Remboursez 100 EUR", request_kind="refund", refund_amount_eur=100), S(), ("continue", "")),
    ("plafond dépassé avec plusieurs clients", T("Remboursez 150 EUR", request_kind="refund", refund_amount_eur=150, matched_customers=2), S(), ("ask_clarification", "multiple_matches")),
    ("hors politique", T("Alignez-vous sur le prix du concurrent", request_kind="price_match"), S(), ("escalate", "policy_exception")),
    ("trois échecs", T("Toujours rien ?"), S(consecutive_failures=3), ("escalate", "unable_to_resolve")),
    ("deux échecs", T("Toujours rien ?"), S(consecutive_failures=2), ("continue", "")),
    ("frustré sans proposition", T("C'est inadmissible !", frustrated=True), S(), ("continue", "")),
    ("frustré après proposition", T("C'est toujours inadmissible !", frustrated=True), S(resolution_offered=True), ("escalate", "customer_request")),
    ("proposition faite, client calme", T("D'accord, merci"), S(resolution_offered=True), ("continue", "")),
    ("refus d'un conseiller", T("Je n'ai pas besoin d'un conseiller, juste le suivi"), S(), ("continue", "")),
]


@pytest.mark.parametrize("turn,state,expected", [c[1:] for c in CASES], ids=[c[0] for c in CASES])
def test_escalation_rules(turn, state, expected):
    d = es.decide(turn, state)
    assert (d.action, d.reason) == expected


def test_every_covered_request_without_other_trigger_continues():
    for kind in sorted(es.COVERED_REQUESTS):
        assert es.decide(T("Bonjour", request_kind=kind), S()).action == "continue", kind


# --- résumé de transfert -----------------------------------------------------------------------------------------

FACTS = {
    "customer_id": "C-77",
    "order_id": "O-1001",
    "order_status": "delivered",
    "amount_discussed_eur": "60 EUR (un article abîmé)",
    "commitment": "Remboursement de 60 EUR sous 5 jours ouvrés, confirmation par e-mail",
}
LABELS = ["Motif :", "Client :", "Commande :", "Montant discuté :", "Engagement pris envers le client :", "Déjà tenté :", "Action recommandée :"]


def test_the_handoff_summary_carries_every_critical_fact_and_the_reason():
    out = es.handoff_summary(es.HandoffInput("refund_over_limit", FACTS, ["vérifié la propriété de la commande"], "Valider un remboursement de 150 EUR"))
    for exact in ("C-77", "O-1001", "delivered", "60 EUR (un article abîmé)", "5 jours ouvrés", "plafond de 100 EUR",
                  "vérifié la propriété de la commande", "Valider un remboursement de 150 EUR"):
        assert exact in out, exact
    assert "Informations manquantes" not in out


def test_the_summary_lines_come_in_the_documented_order():
    out = es.handoff_summary(es.HandoffInput("customer_request", FACTS))
    positions = [out.index(label) for label in LABELS]
    assert positions == sorted(positions)


def test_a_missing_fact_is_flagged_never_invented():
    out = es.handoff_summary(es.HandoffInput("unable_to_resolve", {}))
    assert "Client : non identifié" in out and "Commande : non précisée" in out and "statut : inconnu" in out
    assert "Montant discuté : aucun" in out and "Engagement pris envers le client : aucun" in out
    assert "Déjà tenté : rien" in out
    assert "Informations manquantes : customer_id, order_id" in out


def test_only_the_missing_required_fact_is_listed():
    out = es.handoff_summary(es.HandoffInput("customer_request", {"customer_id": "C-1"}))
    assert "Informations manquantes : order_id" in out and "customer_id," not in out.split("Informations manquantes")[1]


def test_the_summary_does_not_refer_to_the_conversation_and_is_bounded():
    out = es.handoff_summary(es.HandoffInput("customer_request", FACTS, ["a" * 3000]))
    low = out.lower()
    assert not any(p in low for p in ("ci-dessus", "plus haut", "voir la conversation", "comme dit", "précédemment"))
    assert len(out) <= es.MAX_SUMMARY_CHARS


def test_the_summary_can_be_built_from_the_ledger_alone_after_15_turns():
    led = cf.FactsLedger()
    fx.replay(fx.case_events(), led)
    facts = {k: led.get(k) for k in led.keys()}
    out = es.handoff_summary(es.HandoffInput("customer_request", facts))
    assert "O-1001" in out and "60 EUR (un article abîmé)" in out and "5 jours ouvrés" in out and "80 EUR" not in out
