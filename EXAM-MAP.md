# Correspondance avec le guide d'examen officiel

Source : guide d'examen Claude Certified Architect, Foundations, version 1.0 (« Effective July 2026 », sujet à modification sans préavis), lié depuis la page officielle de la certification (anthropic-partners.skilljar.com). Les 30 task statements ci-dessous sont reformulés en français à partir d'un résumé automatique du PDF, relevé le 29 octobre 2026. Lire le PDF reste nécessaire : la fiche peut contenir des erreurs de reformulation, et le guide change.

Colonnes : « Labs » indique où l'exercice se trouve ; « Quiz » compte les questions de la banque qui portent sur ce task statement ; « État » dit si le dépôt couvre le point : Couvert (un exercice le traite, testé automatiquement quand c'est possible, sinon discuté), Partiel ou Manquant.


## Domaine 1 : Architecture agentique et orchestration (27 %)

| TS | Thème | Labs | Quiz | État | À ajouter |
|---|---|---|---|---|---|
| 1.1 | Boucles agentiques pilotées par stop_reason | 01 ex. 1 | 4 | Couvert | - |
| 1.2 | Coordinateur et sous-agents (hub-and-spoke) | 01 ex. 3 | 2 | Couvert | - |
| 1.3 | Lancer les sous-agents : outil Task, allowedTools, AgentDefinition, contexte explicite, appels parallèles | 01 ex. 3 | 3 | Couvert | - |
| 1.4 | Workflows à garanties : prérequis en code, demandes multi-sujets, transfert à un humain | 01 ex. 2, 05 ex. 2 | 3 | Couvert | - |
| 1.5 | Hooks de l'Agent SDK : PostToolUse et interception | 01 ex. 4 | 2 | Couvert | - |
| 1.6 | Décomposition de tâches : chaînage fixe ou adaptatif, revue par passes | 04 ex. 6, 05 ex. 4 | 2 | Couvert | Adaptatif testé par next_subtasks ; choix fixe contre adaptatif discuté |
| 1.7 | Sessions : reprise nommée, fork, résultats périmés | 01 ex. 5 | 2 | Couvert | Cas des résultats périmés traité en discussion seulement |

## Domaine 2 : Conception d'outils et intégration MCP (18 %)

| TS | Thème | Labs | Quiz | État | À ajouter |
|---|---|---|---|---|---|
| 2.1 | Descriptions d'outils et frontières entre outils | 02 ex. 1 | 3 | Couvert | Sélection mesurée avec un vrai modèle : à faire par l'équipe (clé API) |
| 2.2 | Erreurs structurées MCP : isError, catégorie, isRetryable | 02 ex. 2, 05 ex. 3 | 3 | Couvert | - |
| 2.3 | Répartition des outils entre agents et tool_choice | 02 ex. 4 et 6, 04 ex. 1 | 2 | Couvert | tool_choice : comportement des modèles récents à vérifier avec la sonde |
| 2.4 | Serveurs MCP dans Claude Code : .mcp.json, ~/.claude.json, ${VAR}, resources | 02 ex. 2 et 3 | 3 | Couvert | Référence aux ressources côté Claude Code non couverte (à lire dans la doc) |
| 2.5 | Outils intégrés : Read, Write, Edit, Bash, Grep, Glob | 02 ex. 5 | 2 | Couvert | Outils intégrés : chaque outil a sa règle d'usage, relue en quiz |

## Domaine 3 : Configuration et workflows Claude Code (20 %)

| TS | Thème | Labs | Quiz | État | À ajouter |
|---|---|---|---|---|---|
| 3.1 | Hiérarchie des CLAUDE.md, @import, /memory | 03 ex. 1 | 3 | Couvert | Simulation du chargement ; constat réel avec /memory à faire par l'équipe |
| 3.2 | Commandes slash et skills | 03 ex. 2 | 3 | Couvert | allowed-tools : pré-approbation, pas restriction (doc 29 oct. 2026) |
| 3.3 | Règles par chemin (.claude/rules, paths) | 03 ex. 1 | 2 | Couvert | Règle avec paths testée par simulation |
| 3.4 | Mode plan ou exécution directe | 03 ex. 3 | 2 | Couvert | Règle de décision issue du guide lu via résumé automatique |
| 3.5 | Affinage itératif : exemples, tests d'abord, mode interview | 03 ex. 4 | 2 | Couvert | Technique par situation testée ; pratique manuelle non testée |
| 3.6 | Claude Code en CI/CD : -p, --output-format json, --json-schema | 03 ex. 5 | 3 | Couvert | Workflow GitHub non exécuté ; empreintes non persistées entre runs |

## Domaine 4 : Prompt engineering et sortie structurée (20 %)

| TS | Thème | Labs | Quiz | État | À ajouter |
|---|---|---|---|---|---|
| 4.1 | Critères explicites contre les faux positifs | 04 ex. 4 | 2 | Couvert | Mesure des faux positifs avec un vrai modèle : à faire par l'équipe (clé API) |
| 4.2 | Few-shot sur les cas ambigus | 04 ex. 4 | 2 | Couvert | Exemples avec champ <why> contrôlés par les tests |
| 4.3 | Sortie structurée par tool use et JSON Schema | 04 ex. 1, 2 | 3 | Couvert | tool_choice : voir le point d'attention du README du lab |
| 4.4 | Validation, reprise, boucles de retour | 04 ex. 3 | 2 | Couvert | - |
| 4.5 | Traitement par lots (Message Batches) | 04 ex. 5 | 3 | Couvert | Aucun appel réel à l'API Batches : tests avec faux client |
| 4.6 | Revue multi-instances et multi-passes | 04 ex. 6 | 2 | Couvert | - |

## Domaine 5 : Gestion du contexte et fiabilité (15 %)

| TS | Thème | Labs | Quiz | État | À ajouter |
|---|---|---|---|---|---|
| 5.1 | Préserver le contexte : faits critiques, troncature des sorties, effet « lost in the middle » | 05 ex. 1 | 5 | Couvert | Mécanisme testé hors ligne ; fiabilité d'un vrai modèle à constater (ex. 5) |
| 5.2 | Escalade et ambiguïté | 05 ex. 2 | 2 | Couvert | Règles issues du guide lu via résumé automatique ; heuristique de texte limitée |
| 5.3 | Propagation d'erreurs entre agents | 05 ex. 3 | 1 | Couvert | Reprise locale, absence de résultat distincte d'une panne |
| 5.4 | Exploration d'un gros dépôt | 05 ex. 4 et 5 | 1 | Couvert | Simulation avec doublure de sous-agent ; pratique réelle non testée |
| 5.5 | Relecture humaine et calibration de la confiance | 04 ex. 7 | 1 | Couvert | Seuils calibrés sur données étiquetées fournies par le test |
| 5.6 | Provenance des sources et incertitude | 05 ex. 3 | 2 | Couvert | Provenance, dates et contradictions sans arbitrage |

## Bilan

- Task statements : 30. Couverts : 30. Partiels : 0. Manquants : 0.
- Questions du quiz rattachées à un task statement : 72. Questions hors guide : 0.
- Task statements sans aucune question de quiz : aucun.

## Scénarios (guide officiel) et domaines principaux

| Scénario | Domaines principaux |
|---|---|
| 1. Agent de résolution du support client (objectif de résolution au premier contact supérieur à 80 %) | 1, 2, 5 |
| 2. Génération de code avec Claude Code | 3, 5 |
| 3. Système de recherche multi-agents | 1, 2, 5 |
| 4. Outils de productivité développeur avec l'Agent SDK | 2, 3, 1 |
| 5. Claude Code en intégration continue | 3, 4 |
| 6. Extraction de données structurées | 4, 5 |

L'examen tire 4 scénarios parmi ces 6.

## Hors périmètre selon le guide

Fine-tuning, authentification et facturation de l'API, hébergement des serveurs MCP, fournisseurs cloud spécifiques, computer use, vision, streaming, limites de débit et tarification, OAuth, tokenisation, sécurité de l'entraînement (Constitutional AI, RLHF). Ne pas y passer de temps.

## Les quatre exercices de préparation du guide

1. Agent multi-outils avec logique d'escalade (domaines 1, 2, 5) : labs 01, 02 et 05.
2. Claude Code pour un workflow d'équipe (domaines 3, 2) : lab 03 et partie MCP du lab 02.
3. Pipeline d'extraction de données structurées (domaines 4, 5) : lab 04.
4. Pipeline de recherche multi-agents (domaines 1, 2, 5) : labs 01 et 05.
