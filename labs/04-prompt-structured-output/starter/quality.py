"""STARTER exercice 7 : contrôle qualité et relecture humaine.

Tests : pytest labs/04-prompt-structured-output/tests/test_quality.py
"""
from __future__ import annotations

from typing import Any


def accuracy_by_segment(records: list[dict[str, Any]], segment_key: str = "segment") -> dict[str, float]:
    """TODO : records [{"segment": ..., "correct": bool}, ...] -> exactitude par segment."""
    raise NotImplementedError


def weak_segments(by_segment: dict[str, float], floor: float = 0.9) -> list[str]:
    """TODO : segments sous le seuil, du plus faible au plus fort."""
    raise NotImplementedError


def stratified_sample(records: list[dict[str, Any]], key: str, per_stratum: int, seed: int = 0) -> list[dict[str, Any]]:
    """TODO : tirage aléatoire de per_stratum éléments par strate (tous si la strate est plus petite), reproductible."""
    raise NotImplementedError


def calibrate_thresholds(
    labeled: list[tuple[str, float, bool]], target_precision: float = 0.95, min_count: int = 3
) -> dict[str, float]:
    """TODO : labeled = (champ, confiance déclarée, correct ?). Pour chaque champ, la plus petite confiance t telle
    que les valeurs avec confiance >= t atteignent target_precision sur au moins min_count valeurs.
    Si aucune ne convient, renvoyer 1.01 : tout ce champ passe en relecture humaine."""
    raise NotImplementedError


def route_for_review(
    field_confidence: dict[str, float],
    thresholds: dict[str, float],
    *,
    default_threshold: float = 0.8,
    flagged_fields: set[str] | None = None,
) -> list[str]:
    """TODO : champs à relire (triés) : confiance sous le seuil du champ, confiance absente (None), ou champ signalé."""
    raise NotImplementedError


def prioritize_for_capacity(items: list[dict[str, Any]], capacity: int) -> list[dict[str, Any]]:
    """TODO : capacité de relecture limitée : garder les cas les plus incertains (confiance la plus basse d'abord)."""
    raise NotImplementedError
