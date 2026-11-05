"""Exercice 5 (corrigé) : revue de pull request par Claude Code en CI, lisible par un programme.

Principes :
  - une session neuve (`-p`, `--no-session-persistence`, ni `--resume` ni `--continue`) : le relecteur ne voit pas le
    raisonnement qui a produit le code ;
  - la sortie est du JSON validé par un schéma (`--output-format json --json-schema ...`), lu dans `structured_output` ;
  - 3 critères explicites et une liste de ce qu'il faut ignorer, au lieu de « sois prudent » ;
  - outils en lecture seule, budget plafonné, `--bare` pour un résultat identique sur toutes les machines ;
  - le diff passe par l'entrée standard (pas dans la ligne de commande) ;
  - on ne remonte que les constats nouveaux, pour ne pas répéter ceux d'une revue précédente.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Callable

from jsonschema import Draft202012Validator

REVIEW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "category": {"type": "string", "enum": ["security", "bug", "cross_file"]},
                    "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                    "title": {"type": "string"},
                    "explanation": {"type": "string"},
                    "snippet": {"type": "string"},
                    "suggestion": {"type": ["string", "null"]},
                },
                "required": ["file", "category", "severity", "title", "explanation", "snippet"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["findings"],
    "additionalProperties": False,
}

REVIEW_PROMPT = """Tu relis le diff d'une pull request (fourni sur l'entrée standard). Signale uniquement :
1. security : injection SQL ou de commande, secret écrit en dur, contrôle d'accès absent. Gravité high.
2. bug : comportement incorrect à l'exécution (mauvaise condition, valeur d'erreur ignorée). Gravité high ou medium.
3. cross_file : un fichier modifié casse un appelant ou un contrat d'un autre fichier (signature changée, appelants non mis à jour). Gravité high.
Ignore : le style, les noms, le formatage, les préférences de structure, les suggestions de refactorisation.
Pour chaque constat, `snippet` recopie la ligne de code concernée. Si tu ne trouves rien de ces trois types, renvoie une liste `findings` vide.
Tu peux lire les autres fichiers du dépôt (Read, Grep, Glob) pour vérifier les appelants."""


class ReviewError(Exception):
    """La revue n'a pas produit de résultat exploitable (échec du CLI, pas de sortie structurée, sortie invalide)."""


def build_command(*, bare: bool = True, max_budget_usd: float = 0.5, model: str | None = None) -> list[str]:
    cmd = ["claude"]
    if bare:
        cmd.append("--bare")
    cmd += [
        "-p", REVIEW_PROMPT,
        "--output-format", "json",
        "--json-schema", json.dumps(REVIEW_SCHEMA, ensure_ascii=False),
        "--allowedTools", "Read,Grep,Glob",
        "--max-budget-usd", str(max_budget_usd),
        "--no-session-persistence",
    ]
    if model:
        cmd += ["--model", model]
    return cmd


def parse_result(stdout: str) -> list[dict[str, Any]]:
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ReviewError(f"sortie du CLI illisible : {exc}") from exc
    if result.get("is_error"):
        raise ReviewError(f"le CLI a signalé une erreur : {result.get('result')}")
    if "structured_output" not in result:
        raise ReviewError("pas de `structured_output` dans la réponse (le modèle a peut-être refusé ou n'a pas respecté le schéma)")
    errors = sorted(Draft202012Validator(REVIEW_SCHEMA).iter_errors(result["structured_output"]), key=lambda e: list(e.path))
    if errors:
        raise ReviewError(f"sortie hors schéma : {errors[0].message}")
    return result["structured_output"]["findings"]


def fingerprint(finding: dict[str, Any]) -> str:
    """Identité stable d'un constat : le numéro de ligne bouge d'un commit à l'autre, pas le code concerné."""
    snippet = re.sub(r"\s+", " ", finding["snippet"]).strip().lower()
    return hashlib.sha1(f"{finding['file']}|{finding['category']}|{snippet}".encode()).hexdigest()[:12]


def only_new(findings: list[dict[str, Any]], known: set[str] | frozenset[str]) -> list[dict[str, Any]]:
    return [f for f in findings if fingerprint(f) not in known]


@dataclass
class ReviewOutcome:
    findings: list[dict[str, Any]]
    new_findings: list[dict[str, Any]]
    fingerprints: list[str] = field(default_factory=list)

    @property
    def blocking(self) -> bool:
        return any(f["severity"] == "high" for f in self.new_findings)

    @property
    def exit_code(self) -> int:
        return 1 if self.blocking else 0


Runner = Callable[[list[str], str], "tuple[int, str, str]"]


def run_review(run: Runner, diff: str, *, known: set[str] | frozenset[str] = frozenset(), **command_options: Any) -> ReviewOutcome:
    """`run(argv, stdin)` renvoie (code de sortie, stdout, stderr). Lève ReviewError si rien d'exploitable."""
    code, stdout, stderr = run(build_command(**command_options), diff)
    if not stdout.strip():
        raise ReviewError(f"le CLI n'a rien renvoyé (code {code}) : {stderr.strip()[:200]}")
    findings = parse_result(stdout)  # une erreur signalée dans le JSON prime sur le code de sortie
    if code != 0:
        raise ReviewError(f"le CLI a terminé avec le code {code} : {stderr.strip()[:200]}")
    return ReviewOutcome(findings, only_new(findings, known), [fingerprint(f) for f in findings])


def subprocess_runner(argv: list[str], stdin: str) -> "tuple[int, str, str]":
    proc = subprocess.run(argv, input=stdin, capture_output=True, encoding="utf-8", errors="replace", timeout=600)
    return proc.returncode, proc.stdout, proc.stderr


def main(argv: list[str] | None = None) -> int:
    """python ci_review.py < pr.diff   (code 0 : rien de bloquant, 1 : constat high nouveau, 2 : revue inexploitable)"""
    try:
        outcome = run_review(subprocess_runner, sys.stdin.read())
    except ReviewError as exc:
        print(f"Revue inexploitable : {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"new_findings": outcome.new_findings, "fingerprints": outcome.fingerprints}, ensure_ascii=False, indent=2))
    return outcome.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
