"""Exercice 4 : exploration d'un gros dépôt (notes persistées, synthèses bornées, sous-tâches adaptatives).

Tests : pytest labs/05-context-reliability/tests/test_exploration.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

MAX_SYNTHESIS_CHARS = 600


class Scratchpad:
    """Fichier de notes d'exploration. Il survit à la perte du contexte : on le relit avant chaque phase."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def add(self, phase: str, finding: str) -> None:
        """TODO (a) : ajoute une note en fin de fichier (une note par ligne JSON), sans réécrire les précédentes."""
        raise NotImplementedError("TODO (a)")

    def entries(self) -> list[dict[str, str]]:
        """TODO (a) : relit les notes ({"phase", "finding"}) ; fichier absent = liste vide."""
        raise NotImplementedError("TODO (a)")

    def render(self, max_chars: int = 2000) -> str:
        """TODO (a) : notes sous la forme « - [phase] note », dans l'ordre chronologique. Si la place manque,
        ce sont les plus anciennes qui sautent. Aucune note : « (aucune note) »."""
        raise NotImplementedError("TODO (a)")


def bound_synthesis(text: str, max_chars: int = MAX_SYNTHESIS_CHARS) -> str:
    """TODO (b) : ce qu'un sous-agent renvoie au contexte principal. Espaces normalisés ; au plus max_chars
    caractères, coupure de préférence à une fin de phrase, et la marque « [tronqué] » quand on a coupé."""
    raise NotImplementedError("TODO (b)")


def phase_brief(pad: Scratchpad, phase: str, question: str, module: str) -> str:
    """TODO (c) : consigne d'un sous-agent, autonome (il ne voit pas la conversation) : la question d'ensemble,
    la phase, le module, les notes déjà établies (lues dans le fichier de notes) et la limite de longueur."""
    raise NotImplementedError("TODO (c)")


@dataclass
class Finding:
    module: str
    depends_on: list[str] = field(default_factory=list)
    note: str = ""


def next_subtasks(findings: list[Finding], explored: set[str], budget: int) -> list[str]:
    """TODO (d) : décomposition adaptative. Les modules cités comme dépendances et pas encore explorés, les plus
    cités d'abord (égalité : ordre alphabétique), au plus `budget`. Rien de découvert : liste vide."""
    raise NotImplementedError("TODO (d)")
