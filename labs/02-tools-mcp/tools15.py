"""Les 15 outils du système de support (fournis) pour l'exercice de répartition entre agents."""
from __future__ import annotations

# (nom, domaine, écrit dans un système ?)
TOOLS_15 = [
    ("lookup_order", "commandes", False),
    ("find_orders", "commandes", False),
    ("search_orders", "commandes", False),
    ("cancel_order", "commandes", True),
    ("track_parcel", "livraison", False),
    ("get_invoice", "facturation", False),
    ("process_refund", "facturation", True),
    ("check_refund_status", "facturation", False),
    ("apply_coupon", "facturation", True),
    ("search_products", "catalogue", False),
    ("get_stock", "catalogue", False),
    ("get_price", "catalogue", False),
    ("get_customer_profile", "client", False),
    ("update_address", "client", True),
    ("get_loyalty_points", "client", False),
]
DOMAIN = {n: d for n, d, _ in TOOLS_15}
WRITES = {n for n, _, w in TOOLS_15 if w}
