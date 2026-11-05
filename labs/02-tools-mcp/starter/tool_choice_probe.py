"""Exercice 6 : sonde de `tool_choice`.

La documentation de l'API indique que sur les modèles récents (dont Sonnet 5.5) les valeurs `any` et « outil précis »
sont refusées (erreur 400), seul `auto` passe. Ne le croyez pas sur parole : écrivez la sonde et lancez-la avec une clé.
  python labs/02-tools-mcp/run_tool_choice.py --target starter
Consignez le résultat avec le nom du modèle et la date. Le guide d'examen, lui, décrit les trois valeurs.
"""
from __future__ import annotations

from typing import Any


def build_tool_choice(choice: str, tools: list[dict[str, Any]]) -> dict[str, Any]:
    """TODO : `auto` -> {"type": "auto"}, `any` -> {"type": "any"}, `tool` -> {"type": "tool", "name": <premier outil>}."""
    raise NotImplementedError


def probe_tool_choice(client: Any, model: str, tools: list[dict[str, Any]], choices: tuple[str, ...] = ("auto", "any", "tool")) -> dict[str, dict[str, Any]]:
    """TODO : pour chaque valeur, un appel `client.messages.create`.

    Renvoyer {valeur: {"accepted": True, "tools_called": [...]}} si l'appel passe,
    ou {valeur: {"accepted": False, "status": code HTTP, "error": message}} si l'API le refuse.
    """
    raise NotImplementedError
