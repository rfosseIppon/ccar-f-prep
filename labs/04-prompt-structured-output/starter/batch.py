"""STARTER exercice 5 : traitement par lots avec l'API Message Batches.

Tests : pytest labs/04-prompt-structured-output/tests/test_batch.py
Un résultat d'entrée de lot a : custom_id, result.type ("succeeded", "errored", "canceled", "expired")
et, si succeeded, result.message (comme une réponse de l'API Messages).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from extract import TOOL_NAME, build_request  # noqa: F401  (à utiliser)

CUSTOM_ID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def build_batch_requests(docs: dict[str, str], **kwargs: Any) -> list[dict[str, Any]]:
    """TODO : une requête {"custom_id": ..., "params": build_request(...)} par document.

    Refuser (ValueError) un identifiant qui ne respecte pas CUSTOM_ID.
    """
    raise NotImplementedError


def submit_batch(client: Any, docs: dict[str, str], **kwargs: Any) -> str:
    """TODO : client.messages.batches.create(requests=...) et renvoyer l'identifiant du lot."""
    raise NotImplementedError


@dataclass
class BatchOutcome:
    succeeded: dict[str, dict[str, Any]] = field(default_factory=dict)  # custom_id -> entrée de l'outil
    errored: list[str] = field(default_factory=list)
    expired: list[str] = field(default_factory=list)
    canceled: list[str] = field(default_factory=list)
    malformed: list[str] = field(default_factory=list)  # réussi, mais sans appel d'outil exploitable
    missing: list[str] = field(default_factory=list)  # aucun résultat pour ce document
    unknown: list[str] = field(default_factory=list)  # custom_id qui ne correspond à aucun document


def reconcile(results: Iterable[Any], docs: dict[str, str]) -> BatchOutcome:
    """TODO : rapprocher les résultats des documents par custom_id, sans supposer d'ordre.

    Trier chaque résultat dans la bonne liste de BatchOutcome ; un document sans aucun résultat va dans missing.
    """
    raise NotImplementedError


def split_long_document(text: str, max_chars: int) -> list[str]:
    """TODO : découper par lignes en morceaux de max_chars au plus (une ligne plus longue reste entière)."""
    raise NotImplementedError


def retry_documents(outcome: BatchOutcome, docs: dict[str, str], *, max_chars: int | None = None) -> dict[str, str]:
    """TODO : documents à resoumettre. Seulement les échecs (errored, expired, malformed, missing), jamais le lot entier.

    Les annulés ne sont pas relancés automatiquement. Avec max_chars, un document plus long est découpé et ses
    morceaux reçoivent le custom_id « <id>__part<N> » (N à partir de 1).
    """
    raise NotImplementedError


def submission_window_hours(sla_hours: float, batch_max_hours: float = 24) -> float:
    """TODO : intervalle maximal entre deux soumissions pour tenir un délai (SLA) avec un lot qui peut durer 24 h.

    Si le délai ne laisse aucune marge, lever ValueError : un lot ne convient pas, il faut des appels immédiats.
    """
    raise NotImplementedError
