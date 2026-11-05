"""Exercice 2 : règles d'escalade appliquées en code et résumé de transfert autonome.

Tests : pytest labs/05-context-reliability/tests/test_escalation.py
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

REFUND_LIMIT_EUR = 100.0
MAX_FAILED_ATTEMPTS = 3
COVERED_REQUESTS = {"refund", "return", "order_status", "address_change"}

_HUMAN = re.compile(
    r"(parler|discuter|passer|transf[ée]rer|joindre)[^.!?]{0,40}\b(humain|conseiller|conseill[eè]re|responsable|quelqu'un|personne)\b"
    r"|\b(agent|conseiller|conseill[eè]re|service)\s+(humain|client)\b"
    r"|\b(un|une)\s+(humain|vrai(e)?\s+personne|personne\s+r[ée]elle)\b"
    r"|\b(speak|talk)\s+(to|with)\s+(a|an|someone|somebody)\b|\b(a|an)\s+human\b|\bhuman\s+agent\b|\breal\s+person\b",
    re.IGNORECASE,
)
_NEGATION = re.compile(r"\b(pas besoin|ne veux pas|inutile|no need|don'?t (need|want))\b", re.IGNORECASE)


def asks_for_human(text: str) -> bool:
    """Demande explicite d'un humain (fourni). Heuristique de repli : le modèle reste juge des formulations ambiguës."""
    return bool(_HUMAN.search(text)) and not _NEGATION.search(text)


@dataclass(frozen=True)
class Turn:
    text: str
    request_kind: str = "order_status"
    refund_amount_eur: float | None = None
    matched_customers: int | None = None  # nombre de clients trouvés par la recherche ; None si pas de recherche
    frustrated: bool = False


@dataclass(frozen=True)
class CaseState:
    consecutive_failures: int = 0
    resolution_offered: bool = False


@dataclass(frozen=True)
class Decision:
    action: str  # "continue" | "escalate" | "ask_clarification"
    reason: str  # "" | customer_request | refund_over_limit | policy_exception | unable_to_resolve | multiple_matches


def decide(turn: Turn, state: CaseState) -> Decision:
    """TODO (a) : appliquer les règles d'escalade du scénario support, dans le bon ordre.

    - demande explicite d'un humain : escalade immédiate (customer_request), avant toute enquête ;
    - plusieurs clients correspondent : demander un identifiant (ask_clarification, multiple_matches), ne pas deviner ;
    - remboursement au-delà du plafond : escalade refund_over_limit ;
    - demande hors COVERED_REQUESTS : escalade policy_exception ;
    - MAX_FAILED_ATTEMPTS échecs consécutifs : escalade unable_to_resolve ;
    - client frustré alors qu'une résolution lui a déjà été proposée : escalade customer_request ;
    - sinon continuer. Le ton seul du client ne déclenche pas d'escalade s'il n'a pas encore reçu de proposition.
    """
    raise NotImplementedError("TODO (a)")


REASON_LABELS = {
    "customer_request": "Le client demande un conseiller",
    "refund_over_limit": f"Remboursement au-delà du plafond de {REFUND_LIMIT_EUR:.0f} EUR",
    "policy_exception": "Demande hors du périmètre de la politique",
    "unable_to_resolve": "Blocage après plusieurs tentatives",
}
REQUIRED_FACTS = ("customer_id", "order_id")
MAX_SUMMARY_CHARS = 1200


@dataclass
class HandoffInput:
    reason: str
    facts: dict[str, str]
    tried: list[str] = field(default_factory=list)
    recommended_action: str = ""


def handoff_summary(data: HandoffInput) -> str:
    """TODO (b) : résumé compréhensible SANS lire la conversation (le conseiller n'y a pas accès).

    Lignes attendues, dans cet ordre : « Motif : », « Client : », « Commande : » (avec le statut), « Montant
    discuté : », « Engagement pris envers le client : », « Déjà tenté : », « Action recommandée : ». Un fait absent
    est écrit comme tel (« non identifié », « aucun », « inconnu »), jamais inventé ; si customer_id ou order_id
    manque, ajouter une ligne « Informations manquantes : ». Longueur maximale : MAX_SUMMARY_CHARS.
    Aucun renvoi à la conversation (« voir plus haut »).
    """
    raise NotImplementedError("TODO (b)")
