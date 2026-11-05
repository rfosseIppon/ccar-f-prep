"""Exercice 1 : faits critiques d'un dossier, troncature de l'historique, sorties d'outils réduites.

Tests : pytest labs/05-context-reliability/tests/test_case_facts.py
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Faits qu'un dossier de support ne doit jamais perdre. Ordre = ordre d'affichage (stable d'un tour à l'autre).
CRITICAL_KEYS = (
    "customer_id",
    "order_id",
    "order_status",
    "amount_discussed_eur",
    "commitment",
    "refund_id",
    "escalation",
)
# Faits que le modèle peut consigner lui-même avec l'outil note_fact.
NOTE_KEYS = ("amount_discussed_eur", "commitment", "deadline", "customer_preference")
MAX_VALUE_CHARS = 200

# TODO (a) : améliorer cette description. Elle doit dire QUAND appeler l'outil, CE QU'IL consigne (avec des
# exemples) et CE QUI n'est pas pour lui (les identifiants déjà renvoyés par les outils sont consignés seuls).
NOTE_FACT_TOOL: dict[str, Any] = {
    "name": "note_fact",
    "description": "Note un fait.",
    "input_schema": {
        "type": "object",
        "properties": {
            "key": {"type": "string", "enum": list(NOTE_KEYS)},
            "value": {"type": "string"},
        },
        "required": ["key", "value"],
    },
}


@dataclass
class Fact:
    key: str
    value: str
    source: str
    turn: int
    replaces: str | None = None


class FactsLedger:
    """Registre des faits d'un dossier. Un fait plus récent remplace l'ancien et garde sa trace."""

    def __init__(self) -> None:
        self._facts: dict[str, Fact] = {}

    def record(self, key: str, value: Any, source: str, turn: int) -> None:
        """Consigne un fait. Valeur tronquée à MAX_VALUE_CHARS (avec « … »). Même valeur : rien ne change.
        Valeur différente : elle remplace l'ancienne, qui est gardée dans `replaces`."""
        raise NotImplementedError("TODO (b)")

    def get(self, key: str) -> str | None:
        raise NotImplementedError("TODO (b)")

    def capture_tool_result(self, name: str, tool_input: dict[str, Any], output: dict[str, Any], turn: int) -> None:
        """Consigne seuls les identifiants renvoyés par les outils (source « outil <nom> ») :
        get_customer -> customer_id ; lookup_order -> order_id et order_status (champ `status`) ;
        process_refund -> refund_id ; escalate_to_human -> escalation (valeur : le `reason` de l'appel).
        Une sortie en erreur (`isError`) ne consigne rien."""
        raise NotImplementedError("TODO (c)")

    def handle_note_fact(self, tool_input: dict[str, Any], turn: int) -> dict[str, Any]:
        """Gestionnaire de note_fact (source « agent »). Clé hors NOTE_KEYS ou valeur vide : renvoyer
        {"isError": True, "category": "validation", "retryable": False, "message": ...} avec un message qui
        dit quoi faire (les clés autorisées). Sinon {"ok": True, "key": clé}."""
        raise NotImplementedError("TODO (c)")

    def render(self) -> str:
        """Bloc <case_facts>...</case_facts> : une ligne par fait, dans l'ordre de CRITICAL_KEYS puis les autres
        clés par ordre alphabétique, avec la source, le tour et, le cas échéant, la valeur remplacée."""
        raise NotImplementedError("TODO (d)")


def trim_tool_output(output: dict[str, Any], keep: tuple[str, ...], max_items: int = 5) -> dict[str, Any]:
    """Ne garde que les champs de `keep`. Une liste de plus de max_items éléments est coupée, et un champ
    `<clé>_truncated` dit combien d'éléments ont été omis."""
    raise NotImplementedError("TODO (e)")


def _blocks(message: dict[str, Any]) -> list[Any]:
    content = message["content"]
    return content if isinstance(content, list) else []


def _btype(block: Any) -> str | None:
    return block.get("type") if isinstance(block, dict) else getattr(block, "type", None)


def truncate_history(messages: list[dict[str, Any]], keep_last_turns: int) -> list[dict[str, Any]]:
    """Garde les N derniers tours COMPLETS. Un tour commence par un message utilisateur qui n'est pas un simple
    retour d'outils (tool_result) : couper au milieu d'un tour laisserait un tool_result sans tool_use,
    ce que l'API refuse."""
    raise NotImplementedError("TODO (f)")


def build_request(base_system: str, ledger: FactsLedger, history: list[dict[str, Any]], keep_last_turns: int) -> dict[str, Any]:
    """Renvoie {"system": consignes puis bloc de faits en tête, "messages": fin de l'historique}."""
    raise NotImplementedError("TODO (g)")
