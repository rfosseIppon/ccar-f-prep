"""Chargement du module testé (LAB_TARGET=starter par défaut, ou solution) et outils de test communs."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

LAB = Path(__file__).resolve().parent.parent
TARGET = os.environ.get("LAB_TARGET", "starter")
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(LAB / TARGET))

import extract  # noqa: E402
import batch  # noqa: E402
import quality  # noqa: E402
import review  # noqa: E402
import scoring  # noqa: E402


def tool_use(name: str, **input_: Any) -> NS:
    return NS(type="tool_use", id="toolu_x", name=name, input=input_)


def reply(*blocks: NS) -> NS:
    return NS(stop_reason="tool_use", content=list(blocks))


class FakeClient:
    """Rejoue des réponses scriptées et garde une photo des requêtes."""

    def __init__(self, responses: list[NS]):
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []
        self.messages = NS(create=self._create)

    def _create(self, **kwargs: Any) -> NS:
        self.calls.append(kwargs)
        if not self._responses:
            raise AssertionError("Plus de réponse scriptée.")
        return self._responses.pop(0)


def valid_extraction(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "supplier_name": "Atelier Dupont SARL",
        "invoice_number": "F-1",
        "invoice_date": "2026-03-12",
        "currency": "EUR",
        "vat_number": "FR12345678901",
        "payment_terms": "net_30",
        "line_items": [{"description": "x", "quantity": 2, "unit_price": 50.0, "amount": 100.0}],
        "stated_total": 100.0,
    }
    data.update(overrides)
    return data
