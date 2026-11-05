"""Exercice 2 : serveur MCP de trois outils, avec des erreurs structurées.

Lancement : `python shop_server.py` (transport stdio).

À faire, pour chacun des trois outils :
  - renvoyer un résultat d'erreur structuré (`failure(...)`) pour chaque échec prévisible :
      validation  : entrée invalide (numéro de commande hors format CMD-12345, e-mail invalide, statut inconnu, date mal formée)
      permission  : la commande n'appartient pas au client qui la demande (ne rien révéler de la commande)
      business    : commande inexistante, commande archivée
      transient   : BackendTimeout / BackendUnavailable (réessayable)
  - chaque erreur contient `errorCategory`, `isRetryable`, `message` et `nextStep` (ce que le modèle doit faire ensuite) ;
  - `find_orders` pour un client sans commande renvoie un résultat VALIDE et vide (`count: 0`), pas une erreur ;
  - `search_orders` ne renvoie aucune adresse e-mail de client ;
  - une ressource `shop://status-glossary` expose le glossaire des statuts (`STATUS_GLOSSARY`).

Une exception qui remonte au modèle donne un message opaque et aucune consigne : c'est ce que le lab vous fait éviter.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from mcp_compat import CallToolResult, error_result, make_server, ok_result  # noqa: E402,F401
from shop_backend import STATUS_GLOSSARY, BackendTimeout, BackendUnavailable, ShopBackend  # noqa: E402,F401
from tool_defs import DESCRIPTIONS  # noqa: E402

BACKEND = ShopBackend()
server = make_server("shop")


def failure(category: str, retryable: bool, message: str, next_step: str) -> CallToolResult:
    """TODO : résultat d'erreur avec errorCategory, isRetryable, message, nextStep (voir `error_result`)."""
    raise NotImplementedError


@server.tool(name="lookup_order", description=DESCRIPTIONS["lookup_order"])
def lookup_order(order_id: str, customer_email: str) -> CallToolResult:
    raise NotImplementedError  # TODO


@server.tool(name="find_orders", description=DESCRIPTIONS["find_orders"])
def find_orders(customer_email: str, status: str | None = None) -> CallToolResult:
    raise NotImplementedError  # TODO


@server.tool(name="search_orders", description=DESCRIPTIONS["search_orders"])
def search_orders(text: str, date_from: str | None = None, date_to: str | None = None) -> CallToolResult:
    raise NotImplementedError  # TODO


# TODO : ressource `shop://status-glossary` (voir le décorateur `server.resource` de votre version du SDK).


if __name__ == "__main__":
    server.run()
