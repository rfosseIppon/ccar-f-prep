"""CORRIGÉ exercice 2 : règles d'escalade appliquées en code et résumé de transfert autonome."""
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
    """Demande explicite d'un humain. Heuristique de repli : le modèle reste juge des formulations ambiguës."""
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
    """Ordre des règles : demande explicite, ambiguïté, plafond, hors politique, blocage, insistance.

    Ni le ton du client ni une « confiance » auto-déclarée ne déclenchent seuls une escalade.
    """
    if asks_for_human(turn.text):
        return Decision("escalate", "customer_request")  # immédiat, sans enquête préalable
    if turn.matched_customers is not None and turn.matched_customers > 1:
        return Decision("ask_clarification", "multiple_matches")  # on demande un identifiant, on ne devine pas
    if turn.refund_amount_eur is not None and turn.refund_amount_eur > REFUND_LIMIT_EUR:
        return Decision("escalate", "refund_over_limit")
    if turn.request_kind not in COVERED_REQUESTS:
        return Decision("escalate", "policy_exception")
    if state.consecutive_failures >= MAX_FAILED_ATTEMPTS:
        return Decision("escalate", "unable_to_resolve")
    if turn.frustrated and state.resolution_offered:
        return Decision("escalate", "customer_request")  # il insiste après qu'on a proposé de résoudre
    return Decision("continue", "")


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
    """Résumé lisible sans la conversation. Un fait manquant est signalé, jamais inventé."""
    missing = [k for k in REQUIRED_FACTS if not data.facts.get(k)]
    lines = [
        f"Motif : {REASON_LABELS.get(data.reason, data.reason)}",
        f"Client : {data.facts.get('customer_id') or 'non identifié'}",
        f"Commande : {data.facts.get('order_id') or 'non précisée'} (statut : {data.facts.get('order_status') or 'inconnu'})",
        f"Montant discuté : {data.facts.get('amount_discussed_eur') or 'aucun'}",
        f"Engagement pris envers le client : {data.facts.get('commitment') or 'aucun'}",
        "Déjà tenté : " + ("; ".join(data.tried) if data.tried else "rien"),
        f"Action recommandée : {data.recommended_action or 'à définir par le conseiller'}",
    ]
    if missing:
        lines.append("Informations manquantes : " + ", ".join(missing))
    text = "\n".join(lines)
    return text if len(text) <= MAX_SUMMARY_CHARS else text[: MAX_SUMMARY_CHARS - 1] + "…"
