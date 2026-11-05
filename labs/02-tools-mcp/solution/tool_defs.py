"""Exercice 1 (corrigé) : des descriptions qui séparent les trois outils.

Chaque description dit ce que fait l'outil, quand le préférer, ce qu'il ne fait pas et vers quel outil se tourner.
"""
from __future__ import annotations

DESCRIPTIONS = {
    "lookup_order": (
        "Renvoie le détail d'UNE commande (statut, date, total, articles) à partir de son numéro exact (format CMD-12345) "
        "et de l'adresse e-mail du client qui la demande ; refuse si la commande n'appartient pas à ce client. "
        "À utiliser dès que la demande cite un numéro de commande. "
        "Ne cherche ni par client ni par article : pour lister les commandes d'un client, préférer find_orders ; "
        "pour chercher un article, préférer search_orders."
    ),
    "find_orders": (
        "Liste les commandes d'UN client identifié par son adresse e-mail (par exemple marie@example.com), "
        "avec un filtre facultatif sur le statut (processing, shipped, delivered, cancelled) ; "
        "renvoie une liste vide, sans erreur, si le client n'a aucune commande. "
        "À utiliser quand la demande porte sur un client et non sur un numéro précis. "
        "Ne renvoie pas les commandes archivées et ne cherche pas dans les articles : "
        "pour un numéro de commande, préférer lookup_order ; pour un article, préférer search_orders."
    ),
    "search_orders": (
        "Cherche un texte libre dans les articles de toutes les commandes (par exemple casque Bluetooth), "
        "avec une date minimale et une date maximale facultatives au format AAAA-MM-JJ ; "
        "renvoie les numéros de commande, l'article, la date et le statut, sans coordonnées de client. "
        "À utiliser quand on connaît un produit ou une période mais ni le client ni le numéro de commande. "
        "Ne sert pas à consulter une commande précise (lookup_order) ni à lister les commandes d'un client (find_orders)."
    ),
}
