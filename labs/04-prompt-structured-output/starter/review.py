"""STARTER exercices 4 et 6 : revue de code, critères explicites, exemples, passes multiples.

Tests : pytest labs/04-prompt-structured-output/tests/test_review.py
Avec un vrai modèle (clé API) : python labs/04-prompt-structured-output/run_review.py
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")

# Fourni : l'outil de sortie structurée des constats.
REVIEW_TOOL: dict[str, Any] = {
    "name": "report_findings",
    "description": "Rend la liste des problèmes trouvés. Liste vide si rien ne mérite d'être signalé.",
    "input_schema": {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "line": {"type": ["integer", "null"]},
                        "category": {"type": "string", "enum": ["bug", "security", "cross_file"]},
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                        "confidence": {"type": "number", "description": "De 0 à 1, auto-évaluation à calibrer."},
                        "explanation": {"type": "string"},
                    },
                    "required": ["file", "category", "severity", "confidence", "explanation"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["findings"],
        "additionalProperties": False,
    },
}

REVIEW_PROMPT = "TODO exercice 4 : consigne de revue."
# À écrire : (1) les catégories à signaler (bug, security, cross_file) et celles à IGNORER (style, nommage, motifs locaux
# acceptables), (2) trois niveaux de sévérité chacun illustré par un exemple de code, (3) 2 à 4 exemples dans des blocs
# <example> pour les cas ambigus, avec la raison du choix, (4) l'autorisation de rendre une liste vide.

INTEGRATION_PROMPT = "TODO exercice 6 : consigne de la passe d'intégration (ce qui ne se voit qu'en croisant les fichiers)."


def review_file(client: Any, filename: str, diff: str) -> list[dict[str, Any]]:
    """TODO exercice 6 : passe locale. Un appel par fichier, dans une conversation neuve (un seul message utilisateur),
    avec REVIEW_PROMPT en consigne système, REVIEW_TOOL, et le diff de ce fichier seulement."""
    raise NotImplementedError


def review_integration(client: Any, files: dict[str, str], local: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """TODO exercice 6 : passe d'intégration. Tous les diffs ensemble, plus les constats locaux déjà faits (à ne pas répéter)."""
    raise NotImplementedError


@dataclass
class ReviewReport:
    findings: list[dict[str, Any]]
    needs_human: list[dict[str, Any]] = field(default_factory=list)


def review_in_passes(client: Any, files: dict[str, str], *, confidence_threshold: float = 0.7) -> ReviewReport:
    """TODO exercice 6 : une passe locale par fichier, puis une passe d'intégration.

    - dédoublonner par (fichier, catégorie, ligne) ;
    - trier par sévérité (high d'abord), puis par confiance décroissante ;
    - needs_human : les constats dont la confiance est sous confidence_threshold.
    """
    raise NotImplementedError
