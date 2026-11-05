"""Outils de mesure fournis tels quels : les exercices portent sur l'extraction, pas sur ce module.

- chargement du corpus et de la vérité terrain ;
- exactitude champ par champ (comparaison tolérante à la casse, aux accents et à la ponctuation) ;
- détection des valeurs inventées (champ absent du document mais rempli par le modèle) ;
- précision et rappel d'une revue de code, rapprochés par (fichier, catégorie).
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

CORPUS = Path(__file__).resolve().parent / "corpus"
SCORED_FIELDS = ["supplier_name", "invoice_number", "invoice_date", "currency", "vat_number", "payment_terms", "stated_total"]


def load_corpus() -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    docs = {p.stem: p.read_text(encoding="utf-8") for p in sorted(CORPUS.glob("doc_*.txt"))}
    truth = json.loads((CORPUS / "truth.json").read_text(encoding="utf-8"))
    return docs, truth


def load_review_case() -> dict[str, Any]:
    return json.loads((CORPUS / "review_pr.json").read_text(encoding="utf-8"))


def _norm(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return round(float(value), 2)
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9/]", "", text.casefold())


def score_extraction(pred: dict[str, Any] | None, truth: dict[str, Any]) -> dict[str, bool]:
    """Champ par champ : la prédiction est-elle égale à la vérité terrain ?"""
    pred = pred or {}
    return {field: _norm(pred.get(field)) == _norm(truth.get(field)) for field in SCORED_FIELDS}


def invented_values(pred: dict[str, Any] | None, truth: dict[str, Any]) -> list[str]:
    """Champs absents du document (null dans la vérité terrain) que la prédiction a remplis."""
    pred = pred or {}
    return [f for f in SCORED_FIELDS if truth.get(f) is None and pred.get(f) is not None]


def accuracy_by_field(scores: dict[str, dict[str, bool]]) -> dict[str, float]:
    """scores : {doc_id: {champ: bool}} -> {champ: exactitude}."""
    out: dict[str, float] = {}
    for field in SCORED_FIELDS:
        values = [s[field] for s in scores.values() if field in s]
        out[field] = sum(values) / len(values) if values else 0.0
    return out


def score_findings(findings: list[dict[str, Any]], expected: list[dict[str, Any]]) -> dict[str, Any]:
    """Revue de code : rapproche les constats attendus et rendus par (fichier, catégorie)."""
    got = {(f.get("file"), f.get("category")) for f in findings}
    want = {(e["file"], e["category"]) for e in expected}
    true_positives = got & want
    return {
        "precision": len(true_positives) / len(got) if got else 1.0,
        "recall": len(true_positives) / len(want) if want else 1.0,
        "false_positives": sorted(got - want, key=str),
        "missed": sorted(want - got),
    }
