"""Chargement des modules testés (LAB_TARGET=starter par défaut, ou solution) et outils communs du lab 05."""
from __future__ import annotations

import os
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
TARGET = os.environ.get("LAB_TARGET", "starter")
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(LAB / TARGET))

import case_facts  # noqa: E402
import escalation  # noqa: E402
import exploration  # noqa: E402
import fixtures05  # noqa: E402
import partial_failure  # noqa: E402


def reachable(start: str) -> set[str]:
    seen, todo = set(), [start]
    while todo:
        m = todo.pop()
        if m in seen:
            continue
        seen.add(m)
        todo += fixtures05.DEPS[m]
    return seen


def run_exploration(repo: Path, start: str, tmp: Path, budget: int = 3, max_rounds: int = 20):
    """Boucle d'exploration adaptative avec la doublure de sous-agent. Renvoie (explorés, volume lu, volume remonté)."""
    pad = exploration.Scratchpad(tmp / "notes.jsonl")
    findings: list = []
    explored: set[str] = set()
    raw_chars = returned_chars = 0
    queue = [start]
    for round_no in range(max_rounds):
        if not queue:
            break
        for module in queue:
            deps, raw = fixtures05.explore_module(repo, module)
            raw_chars += raw
            synthesis = exploration.bound_synthesis(f"{module} dépend de {', '.join(deps) or 'rien'}. " + "détail " * 200)
            returned_chars += len(synthesis)
            pad.add(f"phase{round_no}", synthesis)
            findings.append(exploration.Finding(module, deps, synthesis))
            explored.add(module)
        queue = exploration.next_subtasks(findings, explored, budget)
    return explored, raw_chars, returned_chars
