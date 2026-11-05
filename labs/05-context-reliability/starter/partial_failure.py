"""Exercice 3 : panne partielle, provenance des affirmations, contradictions.

Tests : pytest labs/05-context-reliability/tests/test_partial_failure.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

TRANSIENT = (TimeoutError, ConnectionError)


@dataclass(frozen=True)
class Claim:
    text: str
    source_name: str = ""
    source_url: str = ""
    date: str = ""  # ISO 8601
    metric: str = ""
    value: float | None = None

    @property
    def sourced(self) -> bool:
        return bool(self.source_name and self.source_url)


@dataclass
class SubResult:
    source: str
    status: str  # "ok" | "empty" | "timeout" | "unreachable"
    claims: list[Claim] = field(default_factory=list)
    error: str = ""
    attempts: int = 1


def run_with_recovery(source: str, fetch: Callable[[], list[Claim]], max_attempts: int = 3) -> SubResult:
    """TODO (a) : exécute fetch() avec reprise locale.

    - erreur transitoire (TRANSIENT) : réessayer jusqu'à max_attempts, puis renvoyer status "timeout" avec
      l'erreur et le nombre de tentatives ;
    - toute autre exception (accès refusé, introuvable...) : status "unreachable" sans réessayer ;
    - liste vide : status "empty" (la source a été consultée et ne contient rien : ce n'est pas une panne) ;
    - sinon status "ok" avec les affirmations.
    Cette fonction ne lève jamais d'exception : l'échec est une donnée pour le coordinateur.
    """
    raise NotImplementedError("TODO (a)")


@dataclass
class Conflict:
    metric: str
    claims: list[Claim]
    same_period: bool


def find_conflicts(claims: list[Claim]) -> list[Conflict]:
    """TODO (b) : pour une même `metric`, des valeurs différentes venant de sources différentes (et sourcées)
    forment un Conflict. `same_period` vaut True si toutes les affirmations ont la même date. On ne tranche pas."""
    raise NotImplementedError("TODO (b)")


def build_report(question: str, results: list[SubResult]) -> str:
    """TODO (c) : rapport en Markdown avec, dans cet ordre :
    - une ligne de couverture (sources consultées sur total, constats sourcés, contradictions) ;
    - « ## Confirmé » : affirmations sourcées hors contradiction, avec nom de la source, URL et date ; les sources
      consultées sans résultat y sont citées à part, comme absence de résultat ;
    - « ## Contradictions » (si besoin) : les deux valeurs, chacune avec sa source et sa date, sans choisir ;
    - « ## Non vérifié » (si besoin) : affirmations sans source exploitable ;
    - « ## Lacunes » avec « ### Non couvert » (sources inaccessibles) et « ### À retenter » (échecs transitoires,
      avec le nombre de tentatives). Une source en échec n'a aucune affirmation dans le rapport.
    """
    raise NotImplementedError("TODO (c)")
