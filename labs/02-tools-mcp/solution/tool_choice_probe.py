"""Exercice 6 (corrigé) : sonde de `tool_choice` sur un modèle donné."""
from __future__ import annotations

from typing import Any


def build_tool_choice(choice: str, tools: list[dict[str, Any]]) -> dict[str, Any]:
    """`auto` : le modèle décide. `any` : un outil au moins est appelé. `tool` : cet outil précis, imposé."""
    if choice in ("auto", "any"):
        return {"type": choice}
    if choice == "tool":
        return {"type": "tool", "name": tools[0]["name"]}
    raise ValueError(f"tool_choice inconnu : {choice!r}")


def probe_tool_choice(client: Any, model: str, tools: list[dict[str, Any]], choices: tuple[str, ...] = ("auto", "any", "tool")) -> dict[str, dict[str, Any]]:
    """Essaie chaque valeur et note si le modèle l'accepte, avec le message d'erreur sinon."""
    results: dict[str, dict[str, Any]] = {}
    for choice in choices:
        try:
            response = client.messages.create(
                model=model,
                max_tokens=200,
                tools=tools,
                tool_choice=build_tool_choice(choice, tools),
                messages=[{"role": "user", "content": "Où en est la commande CMD-10002 de marie@example.com ?"}],
            )
        except Exception as exc:  # noqa: BLE001 - on veut classer toute erreur de l'API
            results[choice] = {"accepted": False, "status": getattr(exc, "status_code", None), "error": str(exc)[:300]}
            continue
        called = [b.name for b in response.content if getattr(b, "type", None) == "tool_use"]
        results[choice] = {"accepted": True, "tools_called": called}
    return results
