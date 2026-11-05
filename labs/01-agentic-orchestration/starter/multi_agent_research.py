"""STARTER exercice 3 : système de recherche multi-agents avec le Claude Agent SDK.

La configuration est vérifiée hors ligne : pytest labs/01-agentic-orchestration/tests/test_multi_agent.py.
L'exécution réelle demande une clé API. Les noms exacts (outil d'invocation des sous-agents, champs
d'AgentDefinition) dépendent de la version du SDK : vérifiez la documentation de votre version.
Le guide d'examen parle de l'outil « Task » ; les versions récentes de Claude Code l'appellent « Agent ».

Lancer : python starter/multi_agent_research.py "votre question de recherche"
"""
from __future__ import annotations

import asyncio
import sys

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, query

COORDINATOR_PROMPT = """TODO : rédiger le prompt du coordinateur.

Il doit couvrir : la décomposition de la question en sous-questions, la délégation, le contexte
transmis à chaque sous-agent (ils ne partagent pas l'historique du coordinateur), et la conduite à
tenir quand un sous-agent échoue ou ne trouve rien. Pensez aussi à : lancer les sous-questions indépendantes
dans le même tour, faire renvoyer les affirmations avec leurs sources, relancer une recherche si la couverture
est insuffisante, distinguer « source inaccessible » de « rien trouvé »."""


def build_options() -> ClaudeAgentOptions:
    """TODO : définir les sous-agents.

    Proposition de rôles : searcher (recherche web), analyst (lecture et recoupement),
    writer (rédaction du rapport). Pour chacun : description (quand l'utiliser), prompt
    (rôle et format de sortie attendu), tools (liste minimale d'outils).

    Le coordinateur ne doit disposer que de l'outil d'invocation des sous-agents
    ("Agent" dans les versions récentes du SDK, "Task" dans les plus anciennes).
    """
    return ClaudeAgentOptions(
        system_prompt=COORDINATOR_PROMPT,
        allowed_tools=[],  # TODO
        agents={},  # TODO
    )


async def main(question: str) -> None:
    async for message in query(prompt=question, options=build_options()):
        if hasattr(message, "result"):
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "Quels sont les usages courants du protocole MCP en entreprise ?"))
