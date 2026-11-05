"""Mesure du choix d'outil (fourni). Hors ligne avec un faux client, en vrai avec run_selection.py."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

QUERIES = Path(__file__).resolve().parent / "corpus" / "queries.json"
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
SYSTEM = (
    "Tu es l'assistant d'un service client e-commerce. Pour répondre, utilise l'outil le plus adapté. "
    "N'appelle qu'un seul outil par demande."
)


def load_queries() -> list[dict[str, str]]:
    return json.loads(QUERIES.read_text(encoding="utf-8"))


def chosen_tool(client: Any, tools: list[dict[str, Any]], query: str, model: str = MODEL) -> str | None:
    """Nom du premier outil appelé par le modèle pour cette demande, ou None s'il répond sans outil."""
    response = client.messages.create(
        model=model,
        max_tokens=300,
        system=SYSTEM,
        tools=tools,
        tool_choice={"type": "auto"},
        messages=[{"role": "user", "content": query}],
    )
    for block in response.content:
        if getattr(block, "type", None) == "tool_use":
            return block.name
    return None


def evaluate_selection(client: Any, tools: list[dict[str, Any]], queries: list[dict[str, str]] | None = None, model: str = MODEL) -> dict[str, Any]:
    queries = queries if queries is not None else load_queries()
    wrong = []
    correct = 0
    for q in queries:
        got = chosen_tool(client, tools, q["query"], model)
        if got == q["expected"]:
            correct += 1
        else:
            wrong.append({"id": q["id"], "expected": q["expected"], "got": got})
    return {"correct": correct, "total": len(queries), "wrong": wrong}
