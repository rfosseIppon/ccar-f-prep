"""Données des exercices 3 et 4 (fournies)."""
from __future__ import annotations

# Exercice 3 : mode plan ou exécution directe ?
TASKS_PLAN = {
    "p1": "Renommer une variable locale dans un seul fichier.",
    "p2": "Migrer l'appel d'une bibliothèque vers une autre, dans une quarantaine de fichiers.",
    "p3": "Corriger un test qui échoue, avec une trace d'erreur qui désigne la ligne fautive.",
    "p4": "Ajouter un module de notifications dont l'architecture n'est pas décidée (plusieurs approches possibles).",
    "p5": "Retrouver la cause d'une régression apparue entre deux versions, sans piste.",
}
PLAN_ACCEPTED = {
    "p1": {"direct"},
    "p2": {"plan"},
    "p3": {"direct"},
    "p4": {"plan"},
    "p5": {"plan"},
}

# Exercice 4 : techniques d'affinage. Pour s4 et s5, le raisonnement : des problèmes qui interagissent se traitent
# ensemble (une correction change l'autre), des problèmes indépendants se traitent l'un après l'autre.
# À recouper avec le guide d'examen (lu via un résumé automatique, pas directement).
TECHNIQUES = {
    "examples": "Donner 2 à 4 exemples concrets d'entrée et de sortie attendue.",
    "tests_first": "Écrire d'abord les tests, puis demander une implémentation qui les fait passer.",
    "interview": "Demander à Claude de poser ses questions avant d'écrire quoi que ce soit.",
    "sequential": "Traiter les problèmes un par un, dans des messages séparés.",
    "single_message": "Donner tous les problèmes dans un seul message.",
}
SITUATIONS = {
    "s1": "Vos consignes en prose sont comprises de façon différente à chaque essai (format de dates, cas limites).",
    "s2": "Vous voulez un résultat vérifiable automatiquement et des corrections qui s'appuient sur des échecs précis.",
    "s3": "Vous démarrez une fonctionnalité dans un domaine que vous maîtrisez mal : vous ne savez pas quelles questions se poser.",
    "s4": "Trois défauts indépendants, dans trois fichiers, sans lien entre eux.",
    "s5": "Deux défauts dont la correction de l'un change la façon de corriger l'autre.",
}
TECHNIQUES_ACCEPTED = {
    "s1": {"examples"},
    "s2": {"tests_first"},
    "s3": {"interview"},
    "s4": {"sequential"},
    "s5": {"single_message"},
}
