"""CORRIGÉ exercice 3 : coordinateur et sous-agents avec le Claude Agent SDK.

La configuration (outils du coordinateur, listes d'outils minimales, consignes) est vérifiée hors ligne par
tests/test_multi_agent.py. L'exécution de bout en bout n'a pas pu être testée à la préparation du repo (pas
de clé API) : lancez-la une fois et ajustez selon votre version du SDK.

Nom de l'outil de délégation : le guide d'examen parle de l'outil « Task » ; les versions récentes de Claude
Code l'appellent « Agent ». Vérifiez le nom dans votre version et corrigez DELEGATION_TOOL si besoin.
"""
from __future__ import annotations

import asyncio
import sys

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, query

DELEGATION_TOOL = "Agent"

COORDINATOR_PROMPT = """Tu coordonnes une recherche documentaire. Tu ne cherches pas toi-même.

Objectif : un rapport complet et sourcé. Critère de qualité : chaque affirmation garde sa source.

Méthode :
1. Décompose la question en 3 à 5 sous-questions qui couvrent tout le sujet, sans doublon.
2. Délègue chaque sous-question au sous-agent « searcher ». Les sous-questions indépendantes se lancent
   dans le même tour, en parallèle. Un sous-agent ne voit pas cette conversation et n'hérite de rien :
   donne-lui dans la consigne la sous-question, le périmètre attendu et le format de réponse.
3. Transmets l'ensemble des résultats complets à « analyst » pour recoupement : il garde les sources
   attachées à chaque affirmation, sépare ce qui est établi de ce qui est contesté, et note les dates
   de publication quand deux chiffres divergent.
4. Si l'analyse montre une couverture insuffisante, relance une recherche ciblée sur ce qui manque.
5. Transmets l'analyse à « writer » pour le rapport final.

Pannes partielles : si une recherche échoue ou ne renvoie rien, continue avec les autres. Distingue
« source inaccessible » (à retenter ou à signaler) de « source consultée, rien trouvé ».
Ne comble jamais un manque avec des suppositions. Le rapport final contient une section « Lacunes »
qui liste les sous-questions non couvertes et la raison."""

SEARCHER_PROMPT = (
    "Tu réponds à une seule sous-question. Renvoie une liste de constats, chacun avec : l'affirmation, "
    "source_url, source_name, la date de publication si elle est connue, et un niveau de confiance "
    "(élevé, moyen, faible). Garde l'affirmation et ses métadonnées séparées. Si une source est "
    "inaccessible, renvoie un constat d'échec avec la requête tentée et la cause. Si tu ne trouves "
    "rien de fiable, dis-le explicitement au lieu de deviner."
)


def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=COORDINATOR_PROMPT,
        # Le coordinateur délègue uniquement.
        allowed_tools=[DELEGATION_TOOL],
        agents={
            "searcher": AgentDefinition(
                description="Recherche sur le web les faits qui répondent à UNE sous-question précise.",
                prompt=SEARCHER_PROMPT,
                tools=["WebSearch", "WebFetch"],
            ),
            "analyst": AgentDefinition(
                description="Recoupe des résultats de recherche, repère contradictions et trous.",
                prompt=(
                    "Tu reçois des résultats bruts. Liste les points confirmés par au moins deux sources, "
                    "les contradictions et les sous-questions sans réponse fiable."
                ),
                tools=["Read"],
            ),
            "writer": AgentDefinition(
                description="Rédige le rapport final à partir de l'analyse fournie.",
                prompt=(
                    "Rédige un rapport structuré à partir de l'analyse. Cite les sources. "
                    "Termine par une section « Lacunes »."
                ),
                tools=["Write"],
            ),
        },
    )


async def main(question: str) -> None:
    async for message in query(prompt=question, options=build_options()):
        if hasattr(message, "result"):
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "Quels sont les usages courants du protocole MCP en entreprise ?"))
