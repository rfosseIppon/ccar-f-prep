"""CORRIGÉ exercice 1 : faits critiques d'un dossier, troncature de l'historique, sorties d'outils réduites."""
from __future__ import annotations

import json
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

NOTE_FACT_TOOL: dict[str, Any] = {
    "name": "note_fact",
    "description": (
        "Consigne dans le dossier un fait à ne jamais perdre : montant discuté avec le client, engagement "
        "pris, délai promis ou préférence exprimée. À appeler dès que le fait apparaît dans la conversation. "
        "Ne sert pas à consigner un identifiant déjà renvoyé par un outil (ils sont consignés automatiquement)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "key": {"type": "string", "enum": list(NOTE_KEYS)},
            "value": {"type": "string", "description": "Le fait, en une phrase précise, avec chiffres et dates exacts"},
        },
        "required": ["key", "value"],
    },
}


def _clip(value: Any) -> str:
    text = str(value)
    return text if len(text) <= MAX_VALUE_CHARS else text[: MAX_VALUE_CHARS - 1] + "…"


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
        new = _clip(value)
        old = self._facts.get(key)
        if old is not None and old.value == new:
            return
        self._facts[key] = Fact(key, new, source, turn, replaces=old.value if old else None)

    def get(self, key: str) -> str | None:
        fact = self._facts.get(key)
        return fact.value if fact else None

    def keys(self) -> list[str]:
        return list(self._facts)

    def capture_tool_result(self, name: str, tool_input: dict[str, Any], output: dict[str, Any], turn: int) -> None:
        """Consigne automatiquement les identifiants et résultats renvoyés par les outils."""
        if output.get("isError"):
            return
        src = f"outil {name}"
        if name == "get_customer" and "customer_id" in output:
            self.record("customer_id", output["customer_id"], src, turn)
        elif name == "lookup_order" and "order_id" in output:
            self.record("order_id", output["order_id"], src, turn)
            if "status" in output:
                self.record("order_status", output["status"], src, turn)
        elif name == "process_refund":
            if "refund_id" in output:
                self.record("refund_id", output["refund_id"], src, turn)
        elif name == "escalate_to_human":
            self.record("escalation", tool_input.get("reason", "escalade"), src, turn)

    def handle_note_fact(self, tool_input: dict[str, Any], turn: int) -> dict[str, Any]:
        """Gestionnaire de l'outil note_fact : refuse une clé inconnue avec un message exploitable."""
        key = tool_input.get("key")
        value = tool_input.get("value")
        if key not in NOTE_KEYS:
            return {"isError": True, "category": "validation", "retryable": False,
                    "message": f"Clé inconnue {key!r}. Clés autorisées : {', '.join(NOTE_KEYS)}."}
        if not value or not str(value).strip():
            return {"isError": True, "category": "validation", "retryable": False, "message": "Valeur vide."}
        self.record(key, value, "agent", turn)
        return {"ok": True, "key": key}

    def render(self) -> str:
        """Bloc de faits à placer en tête du contexte, jamais enfoui dans l'historique."""
        lines = ["<case_facts>", "Faits du dossier (source de vérité, prioritaires sur l'historique) :"]
        order = [k for k in CRITICAL_KEYS if k in self._facts] + sorted(k for k in self._facts if k not in CRITICAL_KEYS)
        for key in order:
            f = self._facts[key]
            extra = f" ; remplace : {f.replaces}" if f.replaces else ""
            lines.append(f"- {key} : {f.value} (source : {f.source}, tour {f.turn}{extra})")
        lines.append("</case_facts>")
        return "\n".join(lines)


def trim_tool_output(output: dict[str, Any], keep: tuple[str, ...], max_items: int = 5) -> dict[str, Any]:
    """Ne garde que les champs utiles d'un résultat d'outil verbeux ; coupe les listes longues en le disant."""
    trimmed: dict[str, Any] = {}
    for key in keep:
        if key not in output:
            continue
        value = output[key]
        if isinstance(value, list) and len(value) > max_items:
            trimmed[key] = value[:max_items]
            trimmed[f"{key}_truncated"] = f"{len(value) - max_items} éléments omis sur {len(value)}"
        else:
            trimmed[key] = value
    return trimmed


def _blocks(message: dict[str, Any]) -> list[Any]:
    content = message["content"]
    return content if isinstance(content, list) else []


def _btype(block: Any) -> str | None:
    return block.get("type") if isinstance(block, dict) else getattr(block, "type", None)


def _is_turn_start(message: dict[str, Any]) -> bool:
    """Un tour commence par un message utilisateur qui n'est pas un simple retour d'outils."""
    if message["role"] != "user":
        return False
    blocks = _blocks(message)
    return not blocks or any(_btype(b) != "tool_result" for b in blocks)


def truncate_history(messages: list[dict[str, Any]], keep_last_turns: int) -> list[dict[str, Any]]:
    """Garde les N derniers tours COMPLETS : un tool_result ne doit jamais perdre son tool_use."""
    if keep_last_turns <= 0:
        return []
    starts = [i for i, m in enumerate(messages) if _is_turn_start(m)]
    if len(starts) <= keep_last_turns:
        return list(messages)
    return list(messages[starts[-keep_last_turns]:])


def build_request(base_system: str, ledger: FactsLedger, history: list[dict[str, Any]], keep_last_turns: int) -> dict[str, Any]:
    """Requête à envoyer : consignes, puis faits en tête, puis seulement la fin de l'historique."""
    return {
        "system": f"{base_system}\n\n{ledger.render()}",
        "messages": truncate_history(history, keep_last_turns),
    }


def to_json(messages: list[dict[str, Any]]) -> str:
    return json.dumps(messages, ensure_ascii=False, default=str)
