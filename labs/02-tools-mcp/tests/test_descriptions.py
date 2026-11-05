"""Exercice 1 : forme des descriptions. Garde-fous grossiers : la vraie mesure se fait avec un modèle (run_selection.py)."""
from __future__ import annotations

import re

from helpers02 import TOOL_NAMES, baseline, tool_defs

D = tool_defs.DESCRIPTIONS


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-zàâçéèêëîïôûùüÿ0-9_-]{3,}", text.lower()))


def test_the_three_tools_are_described():
    assert set(D) == TOOL_NAMES


def test_descriptions_are_no_longer_the_vague_baseline():
    assert all(D[n].strip() != baseline.VAGUE_DESCRIPTIONS[n] for n in TOOL_NAMES)
    assert all(not D[n].lstrip().lower().startswith("todo") for n in TOOL_NAMES)


def test_each_description_is_substantial_and_gives_an_example_value():
    for name, text in D.items():
        assert len(text.split()) >= 30, f"{name} : trop courte pour dire quand et pourquoi"
        assert re.search(r"par exemple|format ", text.lower()), f"{name} : donner un exemple de valeur (« par exemple ... » ou un format)"


def test_each_description_says_what_the_tool_does_not_do():
    for name, text in D.items():
        low = text.lower()
        assert re.search(r"\b(ne |pas|sans|préférer|à la place)\b", low) and ("préférer" in low or "à la place" in low or "ne sert pas" in low), (
            f"{name} : dire ce que l'outil ne fait pas et vers quel outil se tourner"
        )


def test_each_description_names_the_neighbouring_tools():
    for name, text in D.items():
        others = TOOL_NAMES - {name}
        assert sum(o in text for o in others) == 2, f"{name} : nommer les deux outils voisins"


def test_descriptions_are_not_near_duplicates():
    names = sorted(D)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            wa, wb = words(D[a]), words(D[b])
            assert len(wa & wb) / len(wa | wb) < 0.5, f"{a} et {b} se recouvrent trop"
