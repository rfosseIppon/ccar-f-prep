"""Tâches de l'exercice sur les outils intégrés de Claude Code (fourni).

Outils : Read, Write, Edit, Bash, Grep, Glob. Une réponse « Read+Write » désigne le repli en deux temps.
"""
from __future__ import annotations

TASKS = {
    "t1": "Lister tous les fichiers dont le nom se termine par .test.ts dans le dépôt.",
    "t2": "Trouver tous les appels à la fonction apply_discount dans le code.",
    "t3": "Lire le contenu de pyproject.toml.",
    "t4": "Remplacer une chaîne qui n'apparaît qu'une fois dans un fichier de configuration.",
    "t5": "Créer un nouveau fichier CHANGELOG.md.",
    "t6": "Lancer la suite de tests avec pytest.",
    "t7": "Mettre à jour un texte qui apparaît à l'identique à plusieurs endroits d'un même fichier (Edit exige un texte unique).",
    "t8": "Savoir dans quels fichiers est déclarée la classe OrderService.",
    "t9": "Trouver où se trouve le fichier tsconfig.json dans un monorepo.",
}
ALLOWED = {"Read", "Write", "Edit", "Bash", "Grep", "Glob", "Read+Write"}
# Plusieurs réponses acceptées quand la discussion le justifie.
ACCEPTED = {
    "t1": {"Glob"},
    "t2": {"Grep"},
    "t3": {"Read"},
    "t4": {"Edit"},
    "t5": {"Write"},
    "t6": {"Bash"},
    "t7": {"Edit", "Read+Write"},
    "t8": {"Grep"},
    "t9": {"Glob"},
}
