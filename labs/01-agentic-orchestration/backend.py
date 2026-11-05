"""Backend factice du scénario « agent de support client ».

Fourni tel quel : les exercices portent sur l'agent, pas sur ce module.
Chaque erreur est renvoyée sous forme structurée (voir `error`), jamais comme exception.
"""
from __future__ import annotations

from typing import Any

CUSTOMERS: dict[str, dict[str, str]] = {
    "alice@example.com": {"customer_id": "C-100", "name": "Alice Martin", "tier": "standard"},
    "bob@example.com": {"customer_id": "C-200", "name": "Bob Durand", "tier": "premium"},
}

ORDERS: dict[str, dict[str, Any]] = {
    "O-1001": {"customer_id": "C-100", "total_eur": 42.0, "status": "delivered"},
    "O-1002": {"customer_id": "C-100", "total_eur": 250.0, "status": "delivered"},
    "O-2001": {"customer_id": "C-200", "total_eur": 80.0, "status": "shipped"},
}


def error(category: str, message: str, retryable: bool = False) -> dict[str, Any]:
    """Réponse d'erreur structurée, lisible par le modèle.

    Catégories utilisées : not_found, validation, transient, prerequisite_not_met,
    policy_limit, forbidden.
    """
    return {
        "isError": True,
        "errorCategory": category,
        "isRetryable": retryable,
        "message": message,
    }


def get_customer(email: str) -> dict[str, Any]:
    customer = CUSTOMERS.get(email.strip().lower())
    if customer is None:
        return error("not_found", f"Aucun client avec l'adresse {email}.")
    return dict(customer)


def lookup_order(order_id: str) -> dict[str, Any]:
    order = ORDERS.get(order_id)
    if order is None:
        return error("not_found", f"Commande {order_id} introuvable.")
    return {"order_id": order_id, **order}


def process_refund(order_id: str, amount_eur: float) -> dict[str, Any]:
    order = ORDERS.get(order_id)
    if order is None:
        return error("not_found", f"Commande {order_id} introuvable.")
    if amount_eur <= 0 or amount_eur > order["total_eur"]:
        return error(
            "validation",
            f"Montant invalide : il doit être entre 0 et {order['total_eur']} EUR.",
        )
    return {"refund_id": f"R-{order_id}", "order_id": order_id, "amount_eur": amount_eur}


def escalate_to_human(summary: str, reason: str) -> dict[str, Any]:
    return {"ticket_id": "T-0001", "reason": reason, "summary": summary, "status": "queued"}
