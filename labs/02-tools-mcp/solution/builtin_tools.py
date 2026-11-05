"""Exercice 5 (corrigé) : l'outil intégré adapté à chaque tâche de `builtin_tasks.py`."""
from __future__ import annotations

CHOICES = {
    "t1": "Glob",       # motif de nom de fichier
    "t2": "Grep",       # contenu des fichiers
    "t3": "Read",
    "t4": "Edit",       # remplacement ciblé, texte unique
    "t5": "Write",
    "t6": "Bash",
    "t7": "Edit",       # avec un contexte plus long pour rendre l'ancre unique, ou remplacer toutes les occurrences ; sinon Read+Write
    "t8": "Grep",
    "t9": "Glob",
}
