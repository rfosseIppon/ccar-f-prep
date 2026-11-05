# factu-api

API de facturation fictive (Python 3.10+).

## Commandes
- Tests : `python -m pytest` (un module : `python -m pytest tests/test_discounts.py`)
- Pas de linter configuré : ne pas en ajouter sans demande.

## Architecture
@docs/architecture.md

## Contraintes
- `src/billing/` reste en fonctions pures : aucun accès base de données ni réseau.
- Toute requête SQL est paramétrée. Aucune concaténation ni f-string dans une requête.
- Toute nouvelle règle métier s'accompagne d'un test dans `tests/`.
- Ne jamais écrire de secret dans le dépôt.
