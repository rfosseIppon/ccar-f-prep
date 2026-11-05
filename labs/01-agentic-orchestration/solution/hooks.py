"""CORRIGÉ exercice 4 : hooks de l'Agent SDK.

Deux usages déterministes, hors du modèle :
- PreToolUse : bloquer un appel qui enfreint une règle (remboursement au-dessus du plafond) ;
- PostToolUse : normaliser le résultat d'un outil avant que le modèle le lise
  (timestamps Unix en ISO 8601, codes de statut numériques en libellés).

Les fonctions sont pures et testables hors ligne. `build_hooks()` les branche dans
`ClaudeAgentOptions(hooks=...)`. Non exécuté de bout en bout (il faut une clé API) :
vérifiez la forme exacte de `tool_response` pour vos outils MCP avec votre version du SDK.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

REFUND_LIMIT_EUR = 100.0
SERVER = "support"  # nom du serveur MCP des outils du scénario : mcp__support__<outil>
STATUS_LABELS = {1: "pending", 2: "delivered", 3: "cancelled"}  # codes d'un système legacy fictif


def _is_tool(tool_name: str, short_name: str) -> bool:
    return tool_name == short_name or tool_name.endswith("__" + short_name)


async def block_large_refund(input_data: dict[str, Any], tool_use_id: str | None, context: Any) -> dict[str, Any]:
    """PreToolUse : refuse process_refund au-dessus du plafond, avec la consigne d'escalade."""
    if input_data.get("hook_event_name") != "PreToolUse":
        return {}
    if not _is_tool(input_data.get("tool_name", ""), "process_refund"):
        return {}
    amount = (input_data.get("tool_input") or {}).get("amount_eur")
    if isinstance(amount, (int, float)) and not isinstance(amount, bool) and amount > REFUND_LIMIT_EUR:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Remboursement de {amount:g} EUR refusé : le plafond automatique est de "
                    f"{REFUND_LIMIT_EUR:g} EUR. Appelle escalate_to_human avec un résumé du dossier."
                ),
            }
        }
    return {}


def _iso(value: float) -> str:
    seconds = value / 1000 if value > 10**11 else value  # millisecondes ou secondes
    return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize(node: Any) -> tuple[Any, bool]:
    """Renvoie (valeur normalisée, modifiée ou non), récursivement."""
    if isinstance(node, dict):
        out: dict[str, Any] = {}
        changed = False
        for key, value in node.items():
            if key == "status_code" and isinstance(value, int) and not isinstance(value, bool) and value in STATUS_LABELS:
                out["status"] = STATUS_LABELS[value]
                changed = True
            elif (
                key.endswith(("_at", "_date", "timestamp"))
                and isinstance(value, (int, float))
                and not isinstance(value, bool)
                and value > 10**9
            ):
                out[key] = _iso(value)
                changed = True
            else:
                new, sub_changed = _normalize(value)
                out[key] = new
                changed = changed or sub_changed
        return out, changed
    if isinstance(node, list):
        items = [_normalize(item) for item in node]
        return [i for i, _ in items], any(c for _, c in items)
    return node, False


async def normalize_tool_result(input_data: dict[str, Any], tool_use_id: str | None, context: Any) -> dict[str, Any]:
    """PostToolUse : remplace le résultat par une version aux formats homogènes."""
    if input_data.get("hook_event_name") != "PostToolUse":
        return {}
    response = input_data.get("tool_response")
    was_json_string = isinstance(response, str)
    if was_json_string:
        try:
            response = json.loads(response)
        except ValueError:
            return {}
    normalized, changed = _normalize(response)
    if not changed:
        return {}
    updated: Any = json.dumps(normalized, ensure_ascii=False) if was_json_string else normalized
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedToolOutput": updated}}


def build_hooks() -> dict[str, list[Any]]:
    """À passer à ClaudeAgentOptions(hooks=build_hooks())."""
    from claude_agent_sdk import HookMatcher

    return {
        "PreToolUse": [HookMatcher(matcher=f"mcp__{SERVER}__process_refund", hooks=[block_large_refund])],
        "PostToolUse": [HookMatcher(matcher=f"mcp__{SERVER}__.*", hooks=[normalize_tool_result])],
    }
