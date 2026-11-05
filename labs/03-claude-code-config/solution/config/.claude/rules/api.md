---
paths:
  - "src/api/**/*.py"
---

# Conventions des points d'entrée

- Valider les entrées avant tout appel à `src/billing/`.
- Aucune règle métier ici : déléguer à `src/billing/`.
- Les erreurs renvoyées ne contiennent aucun détail interne (pas de trace, pas de requête SQL).
