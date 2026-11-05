"""CORRIGÉ exercice 7 : contrôle qualité et relecture humaine.

Une exactitude globale élevée peut cacher un segment mauvais. On mesure par segment, on échantillonne les
sorties à forte confiance, on calibre les seuils par champ sur des données étiquetées, et on dirige vers la
relecture humaine ce qui est faible ou contradictoire, dans la limite de la capacité des relecteurs.
"""
from __future__ import annotations

import random
from collections import defaultdict
from typing import Any


def accuracy_by_segment(records: list[dict[str, Any]], segment_key: str = "segment") -> dict[str, float]:
    """records : [{"segment": ..., "correct": bool}, ...] -> exactitude par segment."""
    totals: dict[str, list[bool]] = defaultdict(list)
    for r in records:
        totals[r[segment_key]].append(bool(r["correct"]))
    return {seg: sum(v) / len(v) for seg, v in totals.items()}


def weak_segments(by_segment: dict[str, float], floor: float = 0.9) -> list[str]:
    """Segments sous le seuil, du plus faible au plus fort. L'exactitude globale ne sert pas à les trouver."""
    return [s for s, acc in sorted(by_segment.items(), key=lambda kv: kv[1]) if acc < floor]


def stratified_sample(records: list[dict[str, Any]], key: str, per_stratum: int, seed: int = 0) -> list[dict[str, Any]]:
    """Tirage aléatoire de per_stratum éléments par strate (ou tous, si la strate est plus petite). Reproductible."""
    rng = random.Random(seed)
    strata: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        strata[r[key]].append(r)
    out: list[dict[str, Any]] = []
    for name in sorted(strata, key=str):
        items = strata[name]
        out.extend(rng.sample(items, min(per_stratum, len(items))))
    return out


def calibrate_thresholds(
    labeled: list[tuple[str, float, bool]], target_precision: float = 0.95, min_count: int = 3
) -> dict[str, float]:
    """labeled : (champ, confiance déclarée, correct ?). Pour chaque champ : la plus petite confiance t telle que
    les valeurs avec confiance >= t atteignent target_precision (sur au moins min_count valeurs).
    Si aucune ne convient, le seuil vaut 1.01 : tout ce champ passe en revue humaine."""
    by_field: dict[str, list[tuple[float, bool]]] = defaultdict(list)
    for name, confidence, correct in labeled:
        by_field[name].append((confidence, correct))
    thresholds: dict[str, float] = {}
    for name, items in by_field.items():
        thresholds[name] = 1.01
        for t in sorted({c for c, _ in items}):
            kept = [ok for c, ok in items if c >= t]
            if len(kept) >= min_count and sum(kept) / len(kept) >= target_precision:
                thresholds[name] = t
                break
    return thresholds


def route_for_review(
    field_confidence: dict[str, float],
    thresholds: dict[str, float],
    *,
    default_threshold: float = 0.8,
    flagged_fields: set[str] | None = None,
) -> list[str]:
    """Champs à envoyer en relecture : confiance sous le seuil du champ, confiance absente, ou champ signalé
    par la validation (contradiction, incohérence)."""
    flagged = flagged_fields or set()
    return sorted(
        name
        for name, confidence in field_confidence.items()
        if name in flagged or confidence is None or confidence < thresholds.get(name, default_threshold)
    )


def prioritize_for_capacity(items: list[dict[str, Any]], capacity: int) -> list[dict[str, Any]]:
    """Capacité de relecture limitée : on garde les cas les plus incertains (confiance la plus basse d'abord)."""
    return sorted(items, key=lambda i: i["confidence"])[:capacity]
