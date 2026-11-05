# Architecture de factu-api

- `src/api/` : points d'entrée HTTP (validation des entrées, aucune logique métier).
- `src/billing/` : règles métier (remises, taxes). Fonctions pures, sans accès base de données.
- `tests/` : un fichier de test par module de `src/`.
- Les accès base de données passent par des requêtes paramétrées, jamais par concaténation de texte.
