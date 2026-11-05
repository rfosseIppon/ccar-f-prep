"""Mesure l'extraction sur le corpus avec un VRAI modèle (clé API requise).

    python labs/04-prompt-structured-output/run_corpus.py [--target starter|solution] [--mode auto|forced] [--strict]

Affiche l'exactitude par champ, les valeurs inventées et les documents à relire. `evaluate` est aussi testé hors ligne
avec un faux client (tests/test_pipeline.py).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))

from scoring import accuracy_by_field, invented_values, load_corpus, score_extraction  # noqa: E402


def evaluate(client: Any, extract_with_retry: Any, **kwargs: Any) -> dict[str, Any]:
    docs, truth = load_corpus()
    scores, invented, review = {}, {}, []
    for doc_id, text in docs.items():
        result = extract_with_retry(client, text, **kwargs)
        scores[doc_id] = score_extraction(result.data, truth[doc_id])
        found = invented_values(result.data, truth[doc_id])
        if found:
            invented[doc_id] = found
        if result.needs_review:
            review.append(doc_id)
    return {"by_field": accuracy_by_field(scores), "scores": scores, "invented": invented, "needs_review": review}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="starter", choices=["starter", "solution"])
    parser.add_argument("--mode", default="auto", choices=["auto", "forced"])
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(LAB / args.target))
    import os  # noqa: PLC0415

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY absente : ce script appelle le vrai modèle (voir lab 00). Les tests, eux, n'en ont pas besoin.")
    import anthropic  # noqa: PLC0415
    from extract import extract_with_retry  # noqa: PLC0415

    report = evaluate(anthropic.Anthropic(), extract_with_retry, mode=args.mode, strict=args.strict)
    print("Exactitude par champ :")
    for name, value in report["by_field"].items():
        print(f"  {name:16s} {value:.0%}")
    print("Valeurs inventées :", report["invented"] or "aucune")
    print("À relire :", report["needs_review"] or "aucun")


if __name__ == "__main__":
    main()
