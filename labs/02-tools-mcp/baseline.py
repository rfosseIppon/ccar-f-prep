"""Les trois outils dans l'état « avant » (fourni) : noms proches, descriptions floues.

Les schémas d'entrée restent corrects : le lab porte sur les descriptions. Vous les réécrivez dans
`starter/tool_defs.py`; ce module sert de point de départ et de référence de comparaison.
"""
from __future__ import annotations

from typing import Any

VAGUE_DESCRIPTIONS = {
    "search_orders": "Recherche des commandes.",
    "find_orders": "Trouve des commandes.",
    "lookup_order": "Consulte une commande.",
}

SCHEMAS: dict[str, dict[str, Any]] = {
    "search_orders": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Texte à chercher dans les articles commandés"},
            "date_from": {"type": "string", "description": "Date minimale, AAAA-MM-JJ"},
            "date_to": {"type": "string", "description": "Date maximale, AAAA-MM-JJ"},
        },
        "required": ["text"],
    },
    "find_orders": {
        "type": "object",
        "properties": {
            "customer_email": {"type": "string", "description": "Adresse e-mail du client"},
            "status": {"type": "string", "enum": ["processing", "shipped", "delivered", "cancelled"]},
        },
        "required": ["customer_email"],
    },
    "lookup_order": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "Numéro de commande, par exemple CMD-10001"},
            "customer_email": {"type": "string", "description": "Adresse e-mail du client qui demande"},
        },
        "required": ["order_id", "customer_email"],
    },
}


def build_tools(descriptions: dict[str, str]) -> list[dict[str, Any]]:
    """Liste d'outils au format de l'API Messages."""
    return [{"name": name, "description": descriptions[name], "input_schema": SCHEMAS[name]} for name in SCHEMAS]


BASELINE_TOOLS = build_tools(VAGUE_DESCRIPTIONS)
