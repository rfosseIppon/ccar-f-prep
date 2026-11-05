"""CORRIGÉ exercices 4 et 6 : revue de code, critères explicites, exemples, passes multiples.

Testé hors ligne avec un faux client (tests/test_review.py). Pour comparer deux consignes sur le cas de
corpus/review_pr.json avec un vrai modèle, utilisez run_review.py (clé API requise).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

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

REVIEW_PROMPT = """Tu relis le diff d'une pull request. Rends tes constats avec l'outil report_findings.

À signaler (catégories) :
- bug : comportement incorrect probable (condition inversée, décalage d'indice, valeur nulle non gérée) ;
- security : faille exploitable (injection, secret en clair, entrée non contrôlée) ;
- cross_file : incohérence entre fichiers (signature changée sans mise à jour des appels, contrat rompu).

À ignorer, sans en parler :
- le style, le nommage, le formatage, les docstrings manquantes ;
- les motifs locaux acceptables (compréhension de liste plutôt que boucle, nettoyage de fichier temporaire qui ignore une erreur).

Sévérité, avec un exemple de code pour chaque niveau :
- high : donnée ou argent en jeu, exploitable. Exemple : query = f"SELECT * FROM t WHERE id = {user_id}"
- medium : comportement faux dans un cas réaliste. Exemple : for i in range(1, len(items)) qui saute le premier élément
- low : fragilité sans effet immédiat. Exemple : un except trop large autour d'un appel qui ne peut échouer que d'une façon

Pas de remarque si tu n'es pas sûr : une liste vide est une réponse valide.

<example>
<diff>
+    query = f"SELECT * FROM users WHERE name = '{name}'"
+    rows = db.execute(query).fetchall()
</diff>
<findings>[{"file": "users.py", "line": 12, "category": "security", "severity": "high", "confidence": 0.95, "explanation": "Injection SQL : name est inséré dans la requête par f-string."}]</findings>
<why>Valeur contrôlée par l'utilisateur concaténée dans une requête : à signaler.</why>
</example>

<example>
<diff>
-    result = []
-    for x in values:
-        result.append(x * 2)
+    result = [x * 2 for x in values]
</diff>
<findings>[]</findings>
<why>Réécriture de style équivalente : motif local acceptable, rien à signaler.</why>
</example>

<example>
<diff>
+    try:
+        os.remove(tmp_path)
+    except OSError:
+        pass
</diff>
<findings>[]</findings>
<why>Nettoyage d'un fichier temporaire : ignorer l'échec est acceptable ici. Le même except/pass autour d'un paiement serait un bug : le contexte décide.</why>
</example>"""

INTEGRATION_PROMPT = """Tu fais la passe d'intégration d'une pull request. Les problèmes locaux de chaque fichier ont déjà été
traités séparément (voir <local_findings>) : ne les répète pas.
Cherche uniquement ce qui n'apparaît qu'en croisant plusieurs fichiers : signature modifiée dont un appelant n'est pas mis à jour,
contrat de données rompu, flux de données incohérent entre fichiers. Catégorie : cross_file. Rends tes constats avec report_findings.
Liste vide si rien ne se voit en croisant les fichiers. Pas de remarque de style."""


def _findings(response: Any) -> list[dict[str, Any]]:
    for block in response.content:
        if getattr(block, "type", None) == "tool_use" and block.name == REVIEW_TOOL["name"]:
            return list(block.input.get("findings", []))
    return []


def _ask(client: Any, system: str, user_text: str) -> list[dict[str, Any]]:
    """Un appel dans une conversation neuve : aucun historique, donc aucun raisonnement de génération."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system,
        tools=[REVIEW_TOOL],
        tool_choice={"type": "auto"},
        messages=[{"role": "user", "content": user_text}],
    )
    return _findings(response)


def review_file(client: Any, filename: str, diff: str) -> list[dict[str, Any]]:
    """Passe locale : un fichier à la fois, pour que l'attention ne se dilue pas."""
    return _ask(client, REVIEW_PROMPT, f"Fichier : {filename}\n<diff>\n{diff}\n</diff>")


def review_integration(client: Any, files: dict[str, str], local: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Passe d'intégration : tous les fichiers ensemble, plus les constats locaux déjà faits."""
    parts = [f"Fichier : {name}\n<diff>\n{diff}\n</diff>" for name, diff in files.items()]
    user = "\n\n".join(parts) + f"\n\n<local_findings>\n{json.dumps(local, ensure_ascii=False)}\n</local_findings>"
    return _ask(client, INTEGRATION_PROMPT, user)


@dataclass
class ReviewReport:
    findings: list[dict[str, Any]]
    needs_human: list[dict[str, Any]] = field(default_factory=list)


def review_in_passes(client: Any, files: dict[str, str], *, confidence_threshold: float = 0.7) -> ReviewReport:
    """Passes locales par fichier, puis une passe d'intégration ; constats triés, faible confiance routée vers un humain."""
    local = {name: review_file(client, name, diff) for name, diff in files.items()}
    merged = [f for findings in local.values() for f in findings]
    merged += review_integration(client, files, local)
    seen: set[tuple[Any, Any, Any]] = set()
    unique = []
    for f in merged:
        key = (f.get("file"), f.get("category"), f.get("line"))
        if key not in seen:
            seen.add(key)
            unique.append(f)
    unique.sort(key=lambda f: (SEVERITY_ORDER.get(f.get("severity"), 3), -f.get("confidence", 0)))
    return ReviewReport(unique, [f for f in unique if f.get("confidence", 0) < confidence_threshold])
