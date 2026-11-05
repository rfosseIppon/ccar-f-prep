"""Exercices 3 et 4 (corrigé)."""
from __future__ import annotations

PLAN_OR_DIRECT = {"p1": "direct", "p2": "plan", "p3": "direct", "p4": "plan", "p5": "plan"}
JUSTIFICATION = {
    "p1": "Un fichier, périmètre clair : aucun intérêt à planifier.",
    "p2": "Quarante fichiers et des choix de migration : on explore et on valide un plan avant de modifier quoi que ce soit.",
    "p3": "La trace d'erreur désigne la ligne : une correction directe suffit.",
    "p4": "Plusieurs architectures possibles : on les compare en mode plan avant d'écrire du code.",
    "p5": "Cause inconnue : explorer en lecture seule d'abord, puis proposer une correction.",
}
TECHNIQUE = {"s1": "examples", "s2": "tests_first", "s3": "interview", "s4": "sequential", "s5": "single_message"}
