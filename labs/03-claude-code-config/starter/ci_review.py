"""Exercice 5 : revue de pull request par Claude Code en CI, lisible par un programme.

À écrire (voir les docstrings) :
  - REVIEW_SCHEMA : schéma JSON de la sortie (`findings` : file, line, category, severity, title, explanation, snippet, suggestion) ;
  - REVIEW_PROMPT : 3 critères explicites, ce qu'il faut ignorer, liste vide autorisée ;
  - build_command : la ligne de commande `claude -p ...` ;
  - parse_result : lit la réponse JSON du CLI et en tire les constats ;
  - fingerprint / only_new : ne signaler que les constats nouveaux ;
  - run_review : orchestre l'ensemble avec un exécuteur injecté (testable sans CLI ni clé).
Vérifiez chaque option avec `claude --help` dans votre version.
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Callable

REVIEW_SCHEMA: dict[str, Any] = {}  # TODO

REVIEW_PROMPT = "TODO"


class ReviewError(Exception):
    """La revue n'a pas produit de résultat exploitable."""


def build_command(*, bare: bool = True, max_budget_usd: float = 0.5, model: str | None = None) -> list[str]:
    """TODO : liste d'arguments pour subprocess.

    Attendu : -p avec la consigne ; --output-format json ; --json-schema (le schéma en JSON) ; outils en lecture seule
    (--allowedTools) ; plafond de budget ; session neuve et non conservée ; --bare si `bare`. Le diff n'apparaît pas ici :
    il passe par l'entrée standard.
    """
    raise NotImplementedError


def parse_result(stdout: str) -> list[dict[str, Any]]:
    """TODO : lit la réponse JSON du CLI.

    - sortie illisible -> ReviewError ;
    - `is_error` vrai -> ReviewError avec le texte de `result` ;
    - pas de champ `structured_output` -> ReviewError (le champ est absent si le modèle n'a pas produit de sortie valide) ;
    - sortie hors de REVIEW_SCHEMA -> ReviewError ;
    - sinon la liste `findings`.
    """
    raise NotImplementedError


def fingerprint(finding: dict[str, Any]) -> str:
    """TODO : identité stable d'un constat, indépendante du numéro de ligne (qui bouge d'un commit à l'autre)."""
    raise NotImplementedError


def only_new(findings: list[dict[str, Any]], known: set[str] | frozenset[str]) -> list[dict[str, Any]]:
    """TODO : les constats dont l'empreinte n'est pas dans `known`."""
    raise NotImplementedError


@dataclass
class ReviewOutcome:
    findings: list[dict[str, Any]]
    new_findings: list[dict[str, Any]]
    fingerprints: list[str] = field(default_factory=list)

    @property
    def blocking(self) -> bool:
        """TODO : vrai s'il existe un constat NOUVEAU de gravité high."""
        raise NotImplementedError

    @property
    def exit_code(self) -> int:
        """TODO : 1 si bloquant, sinon 0."""
        raise NotImplementedError


Runner = Callable[[list[str], str], "tuple[int, str, str]"]


def run_review(run: Runner, diff: str, *, known: set[str] | frozenset[str] = frozenset(), **command_options: Any) -> ReviewOutcome:
    """TODO : `run(argv, stdin)` renvoie (code de sortie, stdout, stderr).

    Sortie vide ou code de sortie non nul -> ReviewError. Une erreur signalée dans le JSON (`is_error`) prime sur le code.
    """
    raise NotImplementedError


def subprocess_runner(argv: list[str], stdin: str) -> "tuple[int, str, str]":
    proc = subprocess.run(argv, input=stdin, capture_output=True, encoding="utf-8", errors="replace", timeout=600)
    return proc.returncode, proc.stdout, proc.stderr


def main(argv: list[str] | None = None) -> int:
    """python ci_review.py < pr.diff   (code 0 : rien de bloquant, 1 : constat high nouveau, 2 : revue inexploitable)"""
    import json

    try:
        outcome = run_review(subprocess_runner, sys.stdin.read())
    except ReviewError as exc:
        print(f"Revue inexploitable : {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"new_findings": outcome.new_findings, "fingerprints": outcome.fingerprints}, ensure_ascii=False, indent=2))
    return outcome.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
