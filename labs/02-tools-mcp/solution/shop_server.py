"""Exercice 2 (corrigé) : serveur MCP de trois outils, avec des erreurs structurées.

Lancement : `python shop_server.py` (transport stdio). Variable : SHOP_LOG_LEVEL (facultative).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from mcp_compat import CallToolResult, error_result, make_server, ok_result  # noqa: E402
from shop_backend import STATUS_GLOSSARY, BackendTimeout, BackendUnavailable, ShopBackend  # noqa: E402
from tool_defs import DESCRIPTIONS  # noqa: E402

BACKEND = ShopBackend()
ORDER_ID = re.compile(r"^CMD-\d{5}$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUSES = {"processing", "shipped", "delivered", "cancelled"}

server = make_server("shop")


def failure(category: str, retryable: bool, message: str, next_step: str) -> CallToolResult:
    """Catégories : transient, validation, permission, business."""
    return error_result({"errorCategory": category, "isRetryable": retryable, "message": message, "nextStep": next_step})


def transient() -> CallToolResult:
    return failure(
        "transient", True,
        "Le service commandes n'a pas répondu à temps.",
        "Réessayer une fois la même demande ; si l'échec persiste, prévenir le client et escalader.",
    )


def bad_email() -> CallToolResult:
    return failure("validation", False, "Adresse e-mail invalide.", "Redemander l'adresse e-mail au client (forme nom@domaine.fr).")


@server.tool(name="lookup_order", description=DESCRIPTIONS["lookup_order"])
def lookup_order(order_id: str, customer_email: str) -> CallToolResult:
    if not ORDER_ID.match(order_id):
        return failure("validation", False, f"Numéro de commande invalide : {order_id!r}.", "Demander au client son numéro au format CMD-12345.")
    if not EMAIL.match(customer_email):
        return bad_email()
    try:
        order = BACKEND.get_order(order_id)
    except (BackendTimeout, BackendUnavailable):
        return transient()
    if order is None:
        return failure("business", False, f"Aucune commande {order_id}.", "Vérifier le numéro avec le client ; ne pas en inventer un.")
    if order["customer"] != customer_email:
        return failure(
            "permission", False,
            "Cette commande n'appartient pas au client identifié.",
            "Ne communiquer aucune information sur cette commande ; vérifier l'identité du client ou escalader.",
        )
    if order["status"] == "archived":
        return failure("business", False, f"La commande {order_id} est archivée.", "Orienter le client vers le support : les commandes de plus de 2 ans ne sont plus en ligne.")
    return ok_result({"order_id": order_id, "status": order["status"], "date": order["date"], "total": order["total"], "items": order["items"]})


@server.tool(name="find_orders", description=DESCRIPTIONS["find_orders"])
def find_orders(customer_email: str, status: str | None = None) -> CallToolResult:
    if not EMAIL.match(customer_email):
        return bad_email()
    if status is not None and status not in STATUSES:
        return failure("validation", False, f"Statut inconnu : {status!r}.", f"Utiliser l'une de ces valeurs : {', '.join(sorted(STATUSES))}.")
    try:
        orders = BACKEND.orders_of(customer_email, status)
    except (BackendTimeout, BackendUnavailable):
        return transient()
    # Aucune commande : réponse valide, pas une erreur.
    return ok_result({"count": len(orders), "orders": [{k: o[k] for k in ("order_id", "status", "date", "total")} for o in orders]})


@server.tool(name="search_orders", description=DESCRIPTIONS["search_orders"])
def search_orders(text: str, date_from: str | None = None, date_to: str | None = None) -> CallToolResult:
    if len(text.strip()) < 2:
        return failure("validation", False, "Texte de recherche trop court.", "Demander au moins un mot de 2 lettres ou plus.")
    for label, value in (("date_from", date_from), ("date_to", date_to)):
        if value is not None and not DATE.match(value):
            return failure("validation", False, f"{label} doit être au format AAAA-MM-JJ.", "Reformuler la date, par exemple 2026-10-01.")
    try:
        matches = BACKEND.search_items(text.strip(), date_from, date_to)
    except (BackendTimeout, BackendUnavailable):
        return transient()
    return ok_result({"count": len(matches), "matches": matches})


@server.resource("shop://status-glossary", description="Glossaire des statuts de commande (lecture seule).", mime_type="application/json")
def status_glossary() -> str:
    import json

    return json.dumps(STATUS_GLOSSARY, ensure_ascii=False)


if __name__ == "__main__":
    server.run()
