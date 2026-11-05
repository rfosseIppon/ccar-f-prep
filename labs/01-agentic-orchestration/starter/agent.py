"""STARTER : agent de support client. Complétez les deux TODO (run_agent et execute_tool).

Lancer les tests : pytest labs/01-agentic-orchestration/tests
(par défaut les tests visent ce fichier ; LAB_TARGET=solution vise le corrigé)
"""
from __future__ import annotations

import json  # noqa: F401  (utile pour sérialiser les résultats d'outils)
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import backend  # noqa: E402

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
MAX_ITERATIONS = 10
REFUND_LIMIT_EUR = 100.0

SYSTEM_PROMPT = """Tu es l'agent de support d'une boutique en ligne.
Traite les retours, litiges de facturation et problèmes de compte.
Identifie toujours le client avec get_customer avant toute action sur une commande.
Quand une demande sort de ton périmètre, ou que le client demande un humain, appelle escalate_to_human.
Réponds de façon brève et factuelle."""

TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_customer",
        "description": (
            "Identifie un client à partir de son adresse e-mail et renvoie son customer_id, "
            "son nom et son niveau. À appeler en premier, avant lookup_order ou process_refund. "
            "Ne renvoie aucune information sur les commandes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string", "description": "Adresse e-mail du client"}},
            "required": ["email"],
        },
    },
    {
        "name": "lookup_order",
        "description": (
            "Renvoie le détail d'une commande (propriétaire, montant total, statut) à partir de son "
            "identifiant de la forme O-1234. Ne modifie rien."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "process_refund",
        "description": (
            "Rembourse tout ou partie d'une commande livrée. Exige un client déjà identifié avec "
            "get_customer. Refusé au-delà de 100 EUR : dans ce cas, utiliser escalate_to_human."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount_eur": {"type": "number", "description": "Montant en euros, strictement positif"},
            },
            "required": ["order_id", "amount_eur"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Transmet le dossier à un agent humain avec un résumé autonome (le conseiller n'a pas "
            "accès à la conversation). À utiliser pour un remboursement hors plafond, une demande "
            "explicite du client, une exception de politique ou un blocage."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Résumé du dossier et de ce qui a été tenté"},
                "reason": {
                    "type": "string",
                    "enum": ["refund_over_limit", "customer_request", "policy_exception", "unable_to_resolve"],
                },
            },
            "required": ["summary", "reason"],
        },
    },
]


@dataclass
class SessionState:
    verified_customer_id: str | None = None
    escalated: bool = False
    escalation: dict[str, Any] | None = None


@dataclass
class AgentResult:
    final_text: str
    stop_reason: str
    escalated: bool
    iterations: int
    tool_calls: list[tuple[str, dict[str, Any]]] = field(default_factory=list)


def execute_tool(name: str, args: dict[str, Any], state: SessionState) -> dict[str, Any]:
    """TODO exercice 2 : exécuter l'outil `name` et appliquer les règles métier EN CODE.

    Règles à garantir, quoi que le modèle décide :
    - process_refund est refusé tant qu'aucun client n'a été identifié via get_customer
      (catégorie d'erreur : prerequisite_not_met, réessayable).
    - process_refund est refusé si la commande n'appartient pas au client identifié (forbidden).
    - process_refund est refusé au-delà de REFUND_LIMIT_EUR (policy_limit, non réessayable),
      avec un message qui indique d'appeler escalate_to_human.
    - escalate_to_human positionne state.escalated et state.escalation.
    - un outil inconnu ou des arguments invalides renvoient une erreur `validation`, sans exception.

    Les fonctions du backend sont dans `backend` (get_customer, lookup_order, process_refund,
    escalate_to_human, error).
    """
    raise NotImplementedError("exercice 2")


def _text(response: Any) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


def run_agent(
    client: Any,
    user_message: str,
    *,
    max_iterations: int = MAX_ITERATIONS,
    model: str = MODEL,
) -> AgentResult:
    """TODO exercice 1 : boucle agentique pilotée par stop_reason.

    Attendu :
    - appeler client.messages.create(model=..., max_tokens=1024, system=SYSTEM_PROMPT,
      tools=TOOLS, messages=...) à chaque itération ;
    - ajouter la réponse de l'assistant à l'historique ;
    - stop_reason == "end_turn" : terminer et renvoyer le texte ;
    - stop_reason == "tool_use" : exécuter CHAQUE bloc tool_use via execute_tool, puis renvoyer
      tous les tool_result d'un même tour dans UN seul message utilisateur
      (champs : type, tool_use_id, content en JSON, is_error) ;
    - tout autre stop_reason (max_tokens, refusal...) : rendre la main sans lever d'exception ;
    - plafond max_iterations atteint : escalader vers un humain (reason=unable_to_resolve)
      et renvoyer stop_reason="max_iterations".
    """
    raise NotImplementedError("exercice 1")


if __name__ == "__main__":
    import anthropic

    demande = " ".join(sys.argv[1:]) or "Bonjour, je suis alice@example.com, je voudrais un remboursement pour O-1001."
    resultat = run_agent(anthropic.Anthropic(), demande)
    print(resultat.final_text)
    print(f"[stop_reason={resultat.stop_reason} escalade={resultat.escalated} outils={[n for n, _ in resultat.tool_calls]}]")
