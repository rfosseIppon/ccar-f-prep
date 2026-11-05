"""CORRIGÉ exercice 5 : traitement par lots avec l'API Message Batches.

Les fonctions sont testées hors ligne avec de faux résultats (tests/test_batch.py). Pour un vrai lot, il faut une clé API :
le traitement peut prendre jusqu'à 24 heures, sans délai garanti.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from extract import TOOL_NAME, build_request

CUSTOM_ID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def build_batch_requests(docs: dict[str, str], **kwargs: Any) -> list[dict[str, Any]]:
    """Une requête par document, rapprochée de son résultat par custom_id (l'ordre de retour n'est pas garanti)."""
    requests = []
    for doc_id, text in docs.items():
        if not CUSTOM_ID.match(doc_id):
            raise ValueError(f"custom_id invalide : {doc_id!r} (lettres, chiffres, _ et -, 64 caractères au plus)")
        requests.append({"custom_id": doc_id, "params": build_request(text, **kwargs)})
    return requests


def submit_batch(client: Any, docs: dict[str, str], **kwargs: Any) -> str:
    batch = client.messages.batches.create(requests=build_batch_requests(docs, **kwargs))
    return batch.id


@dataclass
class BatchOutcome:
    succeeded: dict[str, dict[str, Any]] = field(default_factory=dict)  # custom_id -> entrée de l'outil
    errored: list[str] = field(default_factory=list)
    expired: list[str] = field(default_factory=list)
    canceled: list[str] = field(default_factory=list)
    malformed: list[str] = field(default_factory=list)  # réussi, mais sans appel d'outil exploitable
    missing: list[str] = field(default_factory=list)  # aucun résultat pour ce document
    unknown: list[str] = field(default_factory=list)  # custom_id qui ne correspond à aucun document


def _tool_input(message: Any) -> dict[str, Any] | None:
    for block in getattr(message, "content", []) or []:
        if getattr(block, "type", None) == "tool_use" and block.name == TOOL_NAME:
            return dict(block.input)
    return None


def reconcile(results: Iterable[Any], docs: dict[str, str]) -> BatchOutcome:
    """Rapproche les résultats des documents par custom_id, sans supposer d'ordre."""
    outcome = BatchOutcome()
    seen: set[str] = set()
    for entry in results:
        custom_id = entry.custom_id
        if custom_id not in docs:
            outcome.unknown.append(custom_id)
            continue
        seen.add(custom_id)
        kind = entry.result.type
        if kind == "succeeded":
            data = _tool_input(entry.result.message)
            if data is None:
                outcome.malformed.append(custom_id)
            else:
                outcome.succeeded[custom_id] = data
        elif kind == "errored":
            outcome.errored.append(custom_id)
        elif kind == "expired":
            outcome.expired.append(custom_id)
        elif kind == "canceled":
            outcome.canceled.append(custom_id)
    outcome.missing = sorted(set(docs) - seen)
    return outcome


def split_long_document(text: str, max_chars: int) -> list[str]:
    """Découpe par lignes en morceaux de max_chars au plus (une ligne plus longue reste entière)."""
    chunks: list[str] = []
    current = ""
    for line in text.splitlines(keepends=True):
        if current and len(current) + len(line) > max_chars:
            chunks.append(current)
            current = ""
        current += line
    if current:
        chunks.append(current)
    return chunks or [text]


def retry_documents(outcome: BatchOutcome, docs: dict[str, str], *, max_chars: int | None = None) -> dict[str, str]:
    """Documents à resoumettre : seulement les échecs, jamais le lot entier.

    Les résultats annulés ne sont pas relancés automatiquement : quelqu'un les a annulés, on lui laisse la décision.
    Si max_chars est donné, un document plus long est découpé (custom_id suffixé par __partN).
    """
    ids = [*outcome.errored, *outcome.expired, *outcome.malformed, *outcome.missing]
    out: dict[str, str] = {}
    for doc_id in ids:
        text = docs[doc_id]
        if max_chars and len(text) > max_chars:
            for n, chunk in enumerate(split_long_document(text, max_chars), start=1):
                out[f"{doc_id}__part{n}"] = chunk
        else:
            out[doc_id] = text
    return out


def submission_window_hours(sla_hours: float, batch_max_hours: float = 24) -> float:
    """Intervalle maximal entre deux soumissions pour tenir un délai (SLA) avec un traitement qui peut durer 24 h."""
    window = sla_hours - batch_max_hours
    if window <= 0:
        raise ValueError("Un lot peut durer jusqu'à 24 h sans garantie : il ne peut pas tenir ce délai, utiliser des appels immédiats.")
    return window
