"""Mesure le choix d'outil avec un VRAI modèle (clé API requise).

    python labs/02-tools-mcp/run_selection.py [--target starter|solution] [--baseline]

`--baseline` mesure les descriptions floues d'origine : c'est la colonne « avant » du tableau avant/après.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="starter", choices=["starter", "solution"])
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY absente : ce script appelle le vrai modèle (voir lab 00). Les tests, eux, n'en ont pas besoin.")
    sys.path.insert(0, str(LAB / args.target))
    import anthropic  # noqa: PLC0415
    from baseline import BASELINE_TOOLS, build_tools  # noqa: PLC0415
    from selection import MODEL, evaluate_selection  # noqa: PLC0415
    from tool_defs import DESCRIPTIONS  # noqa: PLC0415

    tools = BASELINE_TOOLS if args.baseline else build_tools(DESCRIPTIONS)
    report = evaluate_selection(anthropic.Anthropic(), tools)
    print(f"Modèle : {MODEL} ; descriptions : {'floues (avant)' if args.baseline else args.target}")
    print(f"Bonnes sélections : {report['correct']} sur {report['total']}")
    for w in report["wrong"]:
        print(f"  {w['id']} : attendu {w['expected']}, obtenu {w['got']}")


if __name__ == "__main__":
    main()
