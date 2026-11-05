"""Faux back-office de la boutique (fourni). Aucune donnée réelle : cas fictif du lab.

Le serveur MCP que vous écrivez appelle ce module. Il sait tomber en panne à la demande, pour tester les erreurs :
    backend.fail_next("timeout")  -> la prochaine requête lève BackendTimeout
    backend.down = True           -> toutes les requêtes lèvent BackendUnavailable
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


class BackendTimeout(Exception):
    """Délai dépassé : panne passagère, une nouvelle tentative a des chances de réussir."""


class BackendUnavailable(Exception):
    """Service indisponible : panne passagère."""


ORDERS: dict[str, dict[str, Any]] = {
    "CMD-10001": {"customer": "marie@example.com", "status": "delivered", "date": "2026-09-12", "total": 89.90, "items": ["Câble USB-C 2 m", "Chargeur 30 W"]},
    "CMD-10002": {"customer": "marie@example.com", "status": "shipped", "date": "2026-10-20", "total": 129.00, "items": ["Casque Bluetooth"]},
    "CMD-10003": {"customer": "paul@example.com", "status": "processing", "date": "2026-10-25", "total": 45.00, "items": ["Housse d'ordinateur 14 pouces"]},
    "CMD-10004": {"customer": "paul@example.com", "status": "delivered", "date": "2026-10-03", "total": 119.00, "items": ["Casque Bluetooth"]},
    "CMD-10005": {"customer": "lea@example.com", "status": "archived", "date": "2023-04-02", "total": 59.00, "items": ["Clavier mécanique"]},
    "CMD-10006": {"customer": "marie@example.com", "status": "cancelled", "date": "2026-10-27", "total": 35.00, "items": ["Souris sans fil"]},
}


class ShopBackend:
    def __init__(self) -> None:
        self.orders = deepcopy(ORDERS)
        self.down = False
        self._fail_next: str | None = None
        self.calls = 0

    def fail_next(self, kind: str) -> None:
        self._fail_next = kind

    def _enter(self) -> None:
        self.calls += 1
        if self.down:
            raise BackendUnavailable("service commandes indisponible")
        if self._fail_next:
            kind, self._fail_next = self._fail_next, None
            if kind == "timeout":
                raise BackendTimeout("délai dépassé")
            raise BackendUnavailable(kind)

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        self._enter()
        order = self.orders.get(order_id)
        return {"order_id": order_id, **deepcopy(order)} if order else None

    def orders_of(self, customer_email: str, status: str | None = None) -> list[dict[str, Any]]:
        self._enter()
        found = [
            {"order_id": oid, **deepcopy(o)}
            for oid, o in self.orders.items()
            if o["customer"] == customer_email and o["status"] != "archived" and (status is None or o["status"] == status)
        ]
        return sorted(found, key=lambda o: o["order_id"])

    def search_items(self, text: str, date_from: str | None = None, date_to: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        self._enter()
        needle = text.lower()
        hits = []
        for oid, o in sorted(self.orders.items()):
            if o["status"] == "archived":
                continue
            if date_from and o["date"] < date_from or date_to and o["date"] > date_to:
                continue
            for item in o["items"]:
                if needle in item.lower():
                    hits.append({"order_id": oid, "item": item, "date": o["date"], "status": o["status"]})
        return hits[:limit]


STATUS_GLOSSARY = {
    "processing": "Commande reçue, préparation en cours.",
    "shipped": "Colis remis au transporteur.",
    "delivered": "Colis livré.",
    "cancelled": "Commande annulée, aucun débit.",
    "archived": "Commande de plus de 2 ans, retirée du service en ligne ; consulter le support.",
}
