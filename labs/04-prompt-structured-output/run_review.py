"""Revue de code sur le cas fictif corpus/review_pr.json avec un VRAI modèle (clé API requise).

    python labs/04-prompt-structured-output/run_review.py [--target starter|solution]

Compare les constats rendus aux constats attendus (précision, rappel, faux positifs).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))

from scoring import load_review_case, score_findings  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="starter", choices=["starter", "solution"])
    args = parser.parse_args()
    sys.path.insert(0, str(LAB / args.target))
    import os  # noqa: PLC0415

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY absente : ce script appelle le vrai modèle (voir lab 00). Les tests, eux, n'en ont pas besoin.")
    import anthropic  # noqa: PLC0415
    from review import review_in_passes  # noqa: PLC0415

    case = load_review_case()
    report = review_in_passes(anthropic.Anthropic(), case["files"])
    print(score_findings(report.findings, case["expected"]))


if __name__ == "__main__":
    main()
