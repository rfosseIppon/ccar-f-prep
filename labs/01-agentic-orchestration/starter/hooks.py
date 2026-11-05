"""STARTER exercice 4 : hooks de l'Agent SDK.

À écrire : deux hooks asynchrones et leur branchement. Tests : pytest labs/01-agentic-orchestration/tests/test_hooks.py

Forme d'un hook : async def hook(input_data, tool_use_id, context) -> dict
- PreToolUse : input_data contient hook_event_name, tool_name, tool_input. Pour bloquer, renvoyer
  {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                          "permissionDecisionReason": "..."}}. Pour laisser passer, renvoyer {}.
- PostToolUse : input_data contient en plus tool_response. Pour remplacer le résultat avant que le modèle le
  lise, renvoyer {"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedToolOutput": <nouveau résultat>}}.
  Sans modification, renvoyer {}.

Vérifiez les noms de champs avec votre version du SDK (types.py du paquet claude_agent_sdk).
"""
from __future__ import annotations

from typing import Any

REFUND_LIMIT_EUR = 100.0
SERVER = "support"  # nom du serveur MCP : les outils s'appellent mcp__support__<outil>
STATUS_LABELS = {1: "pending", 2: "delivered", 3: "cancelled"}  # codes d'un système legacy fictif


async def block_large_refund(input_data: dict[str, Any], tool_use_id: str | None, context: Any) -> dict[str, Any]:
    """TODO PreToolUse : refuser process_refund au-dessus de REFUND_LIMIT_EUR.

    - ne toucher qu'à l'outil process_refund (le nom peut être préfixé par mcp__support__) ;
    - la raison du refus doit dire quoi faire ensuite (escalate_to_human).
    """
    raise NotImplementedError


async def normalize_tool_result(input_data: dict[str, Any], tool_use_id: str | None, context: Any) -> dict[str, Any]:
    """TODO PostToolUse : homogénéiser les formats du résultat d'un outil.

    - les champs de date numériques (noms finissant par _at, _date ou timestamp, valeur Unix en secondes
      ou en millisecondes) deviennent des chaînes ISO 8601 en UTC ;
    - un champ status_code (1, 2, 3) devient un champ status avec son libellé (STATUS_LABELS) ;
    - le résultat peut être un dict, une liste ou une chaîne JSON ; une chaîne non JSON est laissée telle quelle ;
    - si rien ne change, renvoyer {}.
    """
    raise NotImplementedError


def build_hooks() -> dict[str, list[Any]]:
    """TODO : renvoyer le dictionnaire à passer à ClaudeAgentOptions(hooks=...).

    Utiliser claude_agent_sdk.HookMatcher : un matcher sur mcp__support__process_refund pour
    PreToolUse, un matcher sur les outils du serveur support pour PostToolUse.
    """
    raise NotImplementedError
