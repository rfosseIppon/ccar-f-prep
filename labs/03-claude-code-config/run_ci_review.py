"""Lance la revue CI sur le diff d'exemple avec le VRAI CLI (identifiants requis, appel facturé).

    python labs/03-claude-code-config/run_ci_review.py [--target starter|solution]

Prépare un dépôt temporaire (dépôt d'exemple + votre configuration + le diff appliqué), puis exécute `ci_review.run_review`
depuis ce dépôt. Avec ANTHROPIC_API_KEY, le mode `--bare` recommandé pour la CI est utilisé ; sans clé (session
connectée par abonnement), il est désactivé car `--bare` ignore les identifiants de connexion.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LAB = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="starter", choices=["starter", "solution"])
    args = parser.parse_args()
    if shutil.which("claude") is None:
        sys.exit("Commande claude introuvable (voir lab 00).")
    sys.path.insert(0, str(LAB / args.target))
    import ci_review  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        shutil.copytree(LAB / "sample_repo", repo, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        shutil.copytree(LAB / args.target / "config", repo, dirs_exist_ok=True)
        diff = (LAB / "sample_repo" / "pr.diff").read_text(encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "apply", "pr.diff"], cwd=repo, check=True)

        def runner(argv: list[str], stdin: str) -> tuple[int, str, str]:
            proc = subprocess.run(argv, input=stdin, capture_output=True, encoding="utf-8", errors="replace", timeout=600, cwd=repo)
            return proc.returncode, proc.stdout, proc.stderr

        bare = bool(os.environ.get("ANTHROPIC_API_KEY"))
        try:
            outcome = ci_review.run_review(runner, diff, bare=bare)
        except ci_review.ReviewError as exc:
            print(f"Revue inexploitable : {exc}", file=sys.stderr)
            return 2
    print(json.dumps(outcome.findings, ensure_ascii=False, indent=2))
    print(f"Constats : {len(outcome.findings)} ; bloquant : {outcome.blocking}")
    return outcome.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
