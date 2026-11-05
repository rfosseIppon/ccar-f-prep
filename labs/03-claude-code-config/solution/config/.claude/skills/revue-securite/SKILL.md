---
name: revue-securite
description: Revue de sécurité d'un fichier ou d'un dossier Python du dépôt (injection SQL, secret en dur, contrôle d'accès absent). À utiliser quand on demande de vérifier la sécurité d'un code ; ne corrige rien.
argument-hint: [chemin]
context: fork
agent: Explore
allowed-tools: Read Grep Glob
disallowed-tools: Edit Write Bash
---

Fais une revue de sécurité de `$ARGUMENTS` (fichier ou dossier du dépôt). Tu n'as pas accès à la conversation : tout ce qu'il te faut est ici.

Cherche uniquement ces trois critères :
1. Injection SQL : requête construite par concaténation ou f-string avec une valeur venant de l'extérieur.
2. Secret en dur : mot de passe, clé d'API ou jeton écrit dans le code.
3. Contrôle d'accès absent : fonction qui lit ou modifie les données d'un client sans vérifier qu'il en est propriétaire.

À ignorer : le style, les noms, le formatage, les suggestions de refactorisation.

Pour chaque problème trouvé, donne : le fichier, la ligne, le critère (1, 2 ou 3), la gravité (high, medium ou low) et une correction proposée en une phrase. Si rien ne correspond aux trois critères, réponds « Aucun problème trouvé » et liste les fichiers examinés.
