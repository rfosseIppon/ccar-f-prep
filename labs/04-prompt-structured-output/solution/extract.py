"""CORRIGÉ exercices 1 à 3 : extraction par schéma, valeurs absentes, validation et reprise.

Tout est testable hors ligne avec un faux client (tests/test_extract.py). Avec une vraie clé API, lancez
`python labs/04-prompt-structured-output/run_corpus.py --target solution` pour mesurer l'exactitude.

Note sur tool_choice : d'après la page « Define tools » de la documentation (consultée le 29 octobre 2026),
Claude Sonnet 5.5 et Opus 5.5 renvoient une erreur 400 pour tool_choice « any » ou « tool ». Le mode par
défaut est donc « auto » (+ consigne dans le prompt, + strict en option). Le mode « forced » reste disponible
pour les modèles qui l'acceptent : vérifiez le comportement de votre modèle dans votre console.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from jsonschema import Draft202012Validator

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
TOOL_NAME = "extract_invoice"
MAX_RETRIES = 2
RETRYABLE_KINDS = {"format", "arithmetic"}

SYSTEM_PROMPT = """Tu extrais les informations de factures fournisseurs pour la comptabilité.
Règles :
- Recopie ce qui est écrit dans le document. Ne devine jamais, ne déduis jamais une valeur absente : mets null.
- Les montants sont hors taxes. stated_total est le total hors taxes écrit dans le document, même s'il
  ne correspond pas à la somme des lignes : ne le recalcule pas.
- Dates au format AAAA-MM-JJ. Quand le jour et le mois sont ambigus (04/05/2026), utilise l'usage du pays du
  fournisseur.
- Si une valeur ne rentre dans aucune option d'une liste, choisis other et renseigne le champ de détail ;
  si le document ne permet pas de trancher, choisis unclear.
- Donne dans field_confidence une confiance entre 0 et 1 pour chaque champ renseigné."""

INVOICE_TOOL: dict[str, Any] = {
    "name": TOOL_NAME,
    "description": (
        "Enregistre les informations d'une facture fournisseur lues dans le document fourni. "
        "Un champ absent du document vaut null : ne jamais deviner. Les montants sont hors taxes."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "supplier_name": {"type": "string", "description": "Raison sociale du fournisseur, telle qu'écrite."},
            "invoice_number": {"type": ["string", "null"], "description": "Numéro de facture. null si le document n'en porte pas."},
            "invoice_date": {"type": ["string", "null"], "description": "Date d'émission, AAAA-MM-JJ. null si absente ou illisible."},
            "currency": {"type": "string", "enum": ["EUR", "USD", "GBP", "other", "unclear"]},
            "currency_detail": {"type": ["string", "null"], "description": "Code ou libellé de la devise quand currency vaut other ou unclear."},
            "vat_number": {"type": ["string", "null"], "description": "Numéro de TVA du fournisseur. null s'il n'y en a pas."},
            "payment_terms": {"type": "string", "enum": ["on_receipt", "net_30", "net_60", "other", "unclear"]},
            "payment_terms_detail": {"type": ["string", "null"], "description": "Conditions telles qu'écrites quand payment_terms vaut other ou unclear."},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "amount": {"type": "number", "description": "Montant hors taxes de la ligne."},
                    },
                    "required": ["description", "amount"],
                    "additionalProperties": False,
                },
            },
            "stated_total": {"type": ["number", "null"], "description": "Total hors taxes écrit dans le document. null s'il n'y en a pas."},
            "field_confidence": {
                "type": "object",
                "description": "Confiance de 0 à 1 par champ renseigné (auto-évaluation, à calibrer).",
                "additionalProperties": {"type": "number"},
            },
        },
        "required": ["supplier_name", "currency", "payment_terms", "line_items"],
        "additionalProperties": False,
    },
}

_VALIDATOR = Draft202012Validator(INVOICE_TOOL["input_schema"])


class ExtractionError(RuntimeError):
    pass


# --- exercice 1 : requête et appel -------------------------------------------------------------

def build_request(
    document: str,
    *,
    mode: str = "auto",
    strict: bool = False,
    previous: dict[str, Any] | None = None,
    issues: list["Issue"] | None = None,
) -> dict[str, Any]:
    """Paramètres de client.messages.create pour une extraction (ou une reprise si previous est fourni)."""
    tool = dict(INVOICE_TOOL)
    if strict:
        tool["strict"] = True  # vérifiez les limites de schéma de la page Structured outputs
    if mode == "forced":
        tool_choice: dict[str, Any] = {"type": "tool", "name": TOOL_NAME}
    elif mode == "auto":
        tool_choice = {"type": "auto"}
    else:
        raise ValueError(f"mode inconnu : {mode}")
    content = f"<document>\n{document}\n</document>\n\nExtrais les informations de cette facture avec l'outil {TOOL_NAME}."
    if previous is not None:
        errors = "\n".join(f"- {i.message}" for i in (issues or []))
        content += (
            "\n\nUne extraction précédente a échoué à la validation.\n"
            f"<previous_extraction>\n{json.dumps(previous, ensure_ascii=False, indent=2)}\n</previous_extraction>\n"
            f"<validation_errors>\n{errors}\n</validation_errors>\n"
            "Corrige ce qui est faux d'après le document. Si l'information n'existe pas dans le document, laisse null."
        )
    return {
        "model": MODEL,
        "max_tokens": 2048,
        "system": SYSTEM_PROMPT,
        "tools": [tool],
        "tool_choice": tool_choice,
        "messages": [{"role": "user", "content": content}],
    }


def call_extraction(client: Any, document: str, **kwargs: Any) -> dict[str, Any]:
    response = client.messages.create(**build_request(document, **kwargs))
    for block in response.content:
        if getattr(block, "type", None) == "tool_use" and block.name == TOOL_NAME:
            return dict(block.input)
    raise ExtractionError("La réponse ne contient pas d'appel à l'outil d'extraction.")


# --- exercice 3 : validation -------------------------------------------------------------------

@dataclass
class Issue:
    kind: str  # "format" | "arithmetic" | "absent"
    pattern: str  # étiquette stable pour analyser les rejets (detected_pattern)
    field: str
    message: str


def _sum_lines(data: dict[str, Any]) -> float:
    return round(sum(float(i.get("amount", 0)) for i in data.get("line_items", []) if isinstance(i, dict)), 2)


def validate_extraction(data: dict[str, Any], today: date | None = None) -> list[Issue]:
    """Schéma JSON, puis règles métier : date plausible, lignes, total, champs obligatoires pour la compta."""
    today = today or date.today()
    issues: list[Issue] = []
    for err in _VALIDATOR.iter_errors(data):
        path = ".".join(str(p) for p in err.path) or "(racine)"
        issues.append(Issue("format", "schema", path, f"{path} : {err.message}"))
    if issues:
        return issues  # sans schéma valide, les règles suivantes n'ont pas de sens

    value = data.get("invoice_date")
    if value is not None:
        try:
            parsed = date.fromisoformat(value)
            plausible = date(2000, 1, 1) <= parsed <= today + timedelta(days=30)
        except ValueError:
            plausible = False
        if not plausible:
            issues.append(Issue("format", "bad_date", "invoice_date", f"invoice_date « {value} » n'est pas une date AAAA-MM-JJ plausible."))

    for index, item in enumerate(data["line_items"]):
        if "quantity" in item and "unit_price" in item and abs(item["quantity"] * item["unit_price"] - item["amount"]) > 0.01:
            issues.append(Issue("arithmetic", "line_mismatch", f"line_items.{index}", f"La ligne {index} : quantité x prix unitaire ne donne pas le montant."))

    stated = data.get("stated_total")
    calculated = _sum_lines(data)
    if stated is not None and abs(stated - calculated) > 0.01:
        issues.append(Issue("arithmetic", "total_mismatch", "stated_total", f"stated_total ({stated}) diffère de la somme des lignes ({calculated})."))

    for name in ("invoice_number", "invoice_date"):
        if data.get(name) is None:
            issues.append(Issue("absent", f"missing_{name}", name, f"{name} est absent du document."))
    return issues


def enrich(data: dict[str, Any]) -> dict[str, Any]:
    """Ajoute calculated_total et conflict_detected, calculés en code (jamais par le modèle)."""
    out = dict(data)
    calculated = _sum_lines(data)
    stated = data.get("stated_total")
    out["calculated_total"] = calculated
    out["conflict_detected"] = stated is not None and abs(stated - calculated) > 0.01
    return out


@dataclass
class ExtractionResult:
    data: dict[str, Any]
    issues: list[Issue]
    attempts: int
    needs_review: bool
    detected_patterns: list[str] = field(default_factory=list)


def extract_with_retry(client: Any, document: str, *, max_retries: int = MAX_RETRIES, today: date | None = None, **kwargs: Any) -> ExtractionResult:
    """Extrait, valide, relance avec le message d'erreur. S'arrête si la reprise est inutile.

    - on ne relance que pour les erreurs de format ou de calcul ;
    - une information absente du document ne se corrige pas par une relance : revue humaine ;
    - si la reprise renvoie les mêmes données, on s'arrête (le défaut est dans le document).
    """
    data = call_extraction(client, document, **kwargs)
    attempts = 1
    issues = validate_extraction(data, today)
    patterns = [i.pattern for i in issues]
    while attempts <= max_retries and any(i.kind in RETRYABLE_KINDS for i in issues):
        retryable = [i for i in issues if i.kind in RETRYABLE_KINDS]
        new_data = call_extraction(client, document, previous=data, issues=retryable, **kwargs)
        attempts += 1
        unchanged = new_data == data
        data = new_data
        issues = validate_extraction(data, today)
        patterns += [i.pattern for i in issues]
        if unchanged:
            break
    return ExtractionResult(
        data=enrich(data),
        issues=issues,
        attempts=attempts,
        needs_review=bool(issues),
        detected_patterns=patterns,
    )
