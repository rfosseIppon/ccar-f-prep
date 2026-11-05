"""Exercice 1 : réécrivez les trois descriptions.

Point de départ : les descriptions floues de `baseline.py`. Une bonne description dit :
  - ce que fait l'outil, avec un exemple de valeur d'entrée ;
  - quand le préférer ;
  - ce qu'il ne fait PAS, en nommant l'outil voisin à utiliser à la place.

Mesure (vrai modèle, clé API) : `python labs/02-tools-mcp/run_selection.py --target starter`.
Visez au moins 18 bonnes sélections sur 20. Les tests hors ligne ne vérifient que la forme des descriptions.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from baseline import VAGUE_DESCRIPTIONS  # noqa: E402

DESCRIPTIONS = dict(VAGUE_DESCRIPTIONS)  # TODO exercice 1
