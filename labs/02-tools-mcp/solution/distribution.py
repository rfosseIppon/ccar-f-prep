"""Exercice 4 (corrigé) : 15 outils répartis entre 3 agents spécialisés (5 outils chacun, 2 domaines au plus)."""
from __future__ import annotations

DISTRIBUTION = {
    "agent_commandes_livraison": ["lookup_order", "find_orders", "search_orders", "cancel_order", "track_parcel"],
    "agent_facturation": ["get_invoice", "process_refund", "check_refund_status", "apply_coupon", "get_loyalty_points"],
    "agent_catalogue_client": ["search_products", "get_stock", "get_price", "get_customer_profile", "update_address"],
}

# Frontières, en une phrase chacune (à discuter, pas à tester).
RATIONALE = {
    "agent_commandes_livraison": "Tout ce qui concerne le cycle de vie d'une commande ; track_parcel prolonge le suivi.",
    "agent_facturation": "Les flux d'argent regroupés (remboursement, coupon) ; les points de fidélité sont une forme d'avoir.",
    "agent_catalogue_client": "Lecture du catalogue et du profil ; update_address est le seul outil d'écriture du client.",
}
