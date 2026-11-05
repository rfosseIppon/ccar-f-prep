---
description: Lance les tests d'un module de src/ et résume les échecs
argument-hint: [module]
allowed-tools: Bash(python -m pytest *)
---

Lance `python -m pytest tests/test_$ARGUMENTS.py`. S'il y a des échecs, résume pour chacun le test, la cause probable et le fichier à corriger, sans rien modifier.
