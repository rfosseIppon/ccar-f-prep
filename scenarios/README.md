# Les 6 scénarios

D'après le guide d'examen officiel (version 1.0, juillet 2026), l'examen présente 4 scénarios tirés au hasard parmi ces 6. Les descriptions sont reformulées à partir d'un résumé automatique du PDF : comparez avec le guide. Domaines principaux de chaque scénario : voir `EXAM-MAP.md`. Les questions ci-dessous sont des questions de discussion originales, pas des questions d'examen.

## 1. Agent de support client

Un agent, construit avec l'Agent SDK, traite retours, litiges de facturation et problèmes de compte au travers d'outils MCP (consultation client, recherche de commande, remboursement, escalade). Objectif du guide : plus de 80 % de résolution au premier contact, sans perdre la capacité d'escalader.

- Quelles décisions relèvent du modèle, lesquelles du code ?
- Comment mesurer qu'il escalade au bon moment ?
- Que doit contenir le résumé transmis à un humain ?

## 2. Génération de code avec Claude Code

Une équipe utilise Claude Code au quotidien pour générer, refactorer, déboguer et documenter, avec des commandes slash personnalisées et des fichiers CLAUDE.md.

- Que mettre dans le CLAUDE.md racine, dans les règles par chemin, dans un skill ?
- Quand le mode plan évite-t-il des erreurs coûteuses ?
- Comment partager une configuration entre quatre personnes sans conflits ?

## 3. Système de recherche multi-agents

Un coordinateur délègue à des sous-agents de recherche, d'analyse, de synthèse et de rédaction.

- Quel contexte faut-il transmettre explicitement à chaque sous-agent ?
- Que fait le coordinateur quand un sous-agent échoue ?
- À partir de quand ajouter un agent coûte plus qu'il ne rapporte ?

## 4. Outils de productivité développeur

Un agent construit avec l'Agent SDK aide à explorer un code inconnu ou legacy, à générer du code répétitif et à automatiser des tâches, avec les outils intégrés (Read, Write, Bash, Grep, Glob) et des serveurs MCP.

- Quels outils intégrés suffisent, quand créer un outil MCP ?
- Comment éviter les confusions entre outils proches ?
- Que renvoie un outil quand il échoue ?

## 5. Claude Code en CI/CD

Revues de code automatiques, génération de tests, retours sur les PR.

- Comment obtenir une sortie exploitable par un script ?
- Pourquoi séparer génération et revue ?
- Comment réduire les faux positifs sans perdre les vrais problèmes ?

## 6. Extraction de données structurées

Extraire des informations de documents hétérogènes, valider par schéma, traiter par lots.

- Comment empêcher le modèle d'inventer une valeur absente ?
- Quelle boucle de validation, avec quelle limite de tentatives ?
- Quand préférer un traitement par lots à des appels immédiats ?
