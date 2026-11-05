"""STARTER exercices 1 à 3 : extraction par schéma, valeurs absentes, validation et reprise.

Tests : pytest labs/04-prompt-structured-output/tests/test_extract.py  (avec LAB_TARGET=starter, défaut)
Mesure avec un vrai modèle (clé API) : python labs/04-prompt-structured-output/run_corpus.py

À savoir sur tool_choice : d'après la documentation, Claude Sonnet 5.5 et Opus 5.5 renvoient une erreur 400 pour
tool_choice « any » ou « tool ». Votre fonction build_request prend donc un paramètre mode : « auto » (défaut,
avec une consigne dans le prompt et strict en option) ou « forced ». Vérifiez le comportement de votre modèle.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date
from typing import Any

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
TOOL_NAME = "extract_invoice"
MAX_RETRIES = 2
RETRYABLE_KINDS = {"format", "arithmetic"}

SYSTEM_PROMPT = "TODO : consignes d'extraction (ne jamais deviner, null si absent, dates AAAA-MM-JJ, other/unclear + détail)."

# TODO exercices 1 et 2 : le schéma de l'outil d'extraction.
# Champs attendus : supplier_name, invoice_number, invoice_date, currency (+ currency_detail),
# vat_number, payment_terms (+ payment_terms_detail), line_items (description, quantity, unit_price, amount),
# stated_total, field_confidence.
# Réfléchissez à ce qui est obligatoire, à ce qui peut valoir null, et aux listes de valeurs avec « other » et « unclear ».
INVOICE_TOOL: dict[str, Any] = {
    "name": TOOL_NAME,
    "description": "TODO",
    "input_schema": {"type": "object", "properties": {}},
}


class ExtractionError(RuntimeError):
    pass


def build_request(
    document: str,
    *,
    mode: str = "auto",
    strict: bool = False,
    previous: dict[str, Any] | None = None,
    issues: list["Issue"] | None = None,
) -> dict[str, Any]:
    """TODO exercice 1 : paramètres de client.messages.create.

    - tools=[outil], avec "strict": True sur l'outil si strict ;
    - tool_choice : {"type": "auto"} en mode auto, {"type": "tool", "name": TOOL_NAME} en mode forced ;
    - le document dans un message utilisateur, entre balises ;
    - si previous est fourni (reprise) : joindre le document, l'extraction échouée et les erreurs de validation.
    """
    raise NotImplementedError


def call_extraction(client: Any, document: str, **kwargs: Any) -> dict[str, Any]:
    """TODO exercice 1 : appeler client.messages.create(**build_request(...)) et renvoyer l'entrée du bloc tool_use."""
    raise NotImplementedError


@dataclass
class Issue:
    kind: str  # "format" | "arithmetic" | "absent"
    pattern: str  # étiquette stable pour analyser les rejets (detected_pattern)
    field: str
    message: str


def validate_extraction(data: dict[str, Any], today: date | None = None) -> list[Issue]:
    """TODO exercice 3 : schéma JSON (jsonschema), puis règles métier.

    - date plausible (AAAA-MM-JJ, entre 2000 et aujourd'hui + 30 jours) : kind "format", pattern "bad_date" ;
    - quantité x prix unitaire = montant de la ligne : kind "arithmetic", pattern "line_mismatch" ;
    - stated_total égal à la somme des lignes (0,01 près) : kind "arithmetic", pattern "total_mismatch" ;
    - invoice_number et invoice_date manquants : kind "absent", pattern "missing_<champ>" ;
    - erreurs de schéma : kind "format", pattern "schema".
    """
    raise NotImplementedError


def enrich(data: dict[str, Any]) -> dict[str, Any]:
    """TODO exercice 3 : ajouter calculated_total (somme des lignes) et conflict_detected, calculés en code."""
    raise NotImplementedError


@dataclass
class ExtractionResult:
    data: dict[str, Any]
    issues: list[Issue]
    attempts: int
    needs_review: bool
    detected_patterns: list[str] = field(default_factory=list)


def extract_with_retry(client: Any, document: str, *, max_retries: int = MAX_RETRIES, today: date | None = None, **kwargs: Any) -> ExtractionResult:
    """TODO exercice 3 : extraire, valider, relancer avec le message d'erreur.

    - relancer seulement pour les erreurs de format ou de calcul (RETRYABLE_KINDS) ;
    - une information absente du document ne se corrige pas par une relance : needs_review ;
    - si la relance renvoie exactement les mêmes données, s'arrêter (le défaut est dans le document) ;
    - au plus max_retries relances ; garder tous les patterns détectés dans detected_patterns.
    """
    raise NotImplementedError
