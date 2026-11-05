"""Exercice 4 : répartissez les 15 outils de `tools15.py` entre 3 agents.

Règles vérifiées par les tests :
  - chaque outil est confié à un seul agent ;
  - 4 ou 5 outils par agent ;
  - 2 domaines au plus par agent (colonne « domaine » de `tools15.py`) ;
  - 2 outils qui écrivent dans un système au plus par agent.

Écrivez aussi une phrase par frontière dans RATIONALE : pourquoi ces outils ensemble ?
"""
from __future__ import annotations

DISTRIBUTION: dict[str, list[str]] = {}  # TODO : {"nom_agent": ["outil", ...], ...}
RATIONALE: dict[str, str] = {}
