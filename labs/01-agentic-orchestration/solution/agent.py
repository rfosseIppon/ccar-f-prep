"""CORRIGÉ : agent de support client avec boucle agentique et garde-fous en code."""
from __future__ import annotations

import json
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
    """Exécute un outil. Les règles métier sont appliquées ICI, pas seulement dans le prompt."""
    try:
        if name == "get_customer":
            out = backend.get_customer(**args)
            if not out.get("isError"):
                state.verified_customer_id = out["customer_id"]
            return out

        if name == "lookup_order":
            return backend.lookup_order(**args)

        if name == "process_refund":
            if state.verified_customer_id is None:
                return backend.error(
                    "prerequisite_not_met",
                    "Identifier d'abord le client avec get_customer avant tout remboursement.",
                    retryable=True,
                )
            order = backend.ORDERS.get(args.get("order_id", ""))
            if order is not None and order["customer_id"] != state.verified_customer_id:
                return backend.error("forbidden", "Cette commande n'appartient pas au client identifié.")
            if float(args.get("amount_eur", 0)) > REFUND_LIMIT_EUR:
                return backend.error(
                    "policy_limit",
                    f"Remboursement supérieur à {REFUND_LIMIT_EUR:.0f} EUR : "
                    "appeler escalate_to_human avec reason=refund_over_limit.",
                )
            return backend.process_refund(**args)

        if name == "escalate_to_human":
            out = backend.escalate_to_human(**args)
            state.escalated = True
            state.escalation = out
            return out

        return backend.error("validation", f"Outil inconnu : {name}.")
    except TypeError as exc:
        return backend.error("validation", f"Arguments invalides pour {name} : {exc}")


def _text(response: Any) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


def run_agent(
    client: Any,
    user_message: str,
    *,
    max_iterations: int = MAX_ITERATIONS,
    model: str = MODEL,
) -> AgentResult:
    """Boucle agentique pilotée par stop_reason."""
    state = SessionState()
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
    tool_calls: list[tuple[str, dict[str, Any]]] = []

    for iteration in range(1, max_iterations + 1):
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return AgentResult(_text(response), "end_turn", state.escalated, iteration, tool_calls)

        if response.stop_reason != "tool_use":
            # max_tokens, refusal, pause_turn... : on rend la main sans inventer de suite.
            return AgentResult(_text(response), response.stop_reason, state.escalated, iteration, tool_calls)

        # Tous les tool_result d'un même tour reviennent dans UN seul message utilisateur.
        results: list[dict[str, Any]] = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            tool_calls.append((block.name, dict(block.input)))
            output = execute_tool(block.name, dict(block.input), state)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output, ensure_ascii=False),
                    "is_error": bool(output.get("isError")),
                }
            )
        messages.append({"role": "user", "content": results})

    # Garde-fou : plafond d'itérations atteint, on escalade au lieu de boucler.
    execute_tool(
        "escalate_to_human",
        {"summary": "Plafond d'itérations atteint sans résolution.", "reason": "unable_to_resolve"},
        state,
    )
    return AgentResult("", "max_iterations", state.escalated, max_iterations, tool_calls)


if __name__ == "__main__":
    import anthropic

    demande = " ".join(sys.argv[1:]) or "Bonjour, je suis alice@example.com, je voudrais un remboursement pour O-1001."
    resultat = run_agent(anthropic.Anthropic(), demande)
    print(resultat.final_text)
    print(f"[stop_reason={resultat.stop_reason} escalade={resultat.escalated} outils={[n for n, _ in resultat.tool_calls]}]")
