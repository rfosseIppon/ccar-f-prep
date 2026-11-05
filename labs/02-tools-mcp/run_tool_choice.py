"""Sonde de `tool_choice` avec un VRAI modèle (clé API requise).

    python labs/02-tools-mcp/run_tool_choice.py [--target starter|solution] [--model claude-sonnet-5-5]
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
    parser.add_argument("--model", default=os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"))
    args = parser.parse_args()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY absente : ce script appelle le vrai modèle (voir lab 00). Les tests, eux, n'en ont pas besoin.")
    sys.path.insert(0, str(LAB / args.target))
    import anthropic  # noqa: PLC0415
    from baseline import BASELINE_TOOLS  # noqa: PLC0415
    from tool_choice_probe import probe_tool_choice  # noqa: PLC0415

    for choice, result in probe_tool_choice(anthropic.Anthropic(), args.model, BASELINE_TOOLS).items():
        print(f"{choice:5s} -> {result}")


if __name__ == "__main__":
    main()
