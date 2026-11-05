# Grille d'auto-évaluation

À remplir seul, sur papier ou dans une copie de ce fichier, à trois moments : fin de la semaine du domaine, début de S4, la veille de l'examen. Les 30 task statements viennent du guide d'examen officiel (voir `EXAM-MAP.md`).

## Comment remplir

Pour chaque task statement, trois cases à cocher honnêtement :

- **Expliquer** : je l'explique à voix haute en deux minutes, en anglais avec le vocabulaire de l'examen, sans notes, en donnant une situation où l'autre option est la mauvaise.
- **Appliquer** : l'exercice du lab indiqué passe sur mon `starter/` (ou, pour une discussion, j'ai noté mon choix et l'alternative écartée).
- **Trancher** : je réponds juste, du premier coup, aux questions du quiz de ce task statement (colonne « Quiz »), y compris celles à deux bonnes réponses, sans avoir lu la correction avant.

Le total d'un task statement va de 0 à 3. Cocher « Expliquer » sans les deux autres ne compte pas comme maîtrisé : l'examen demande de choisir entre des options plausibles, pas de réciter.

## Que faire du résultat

1. Un task statement à 0 ou 1 sur 3 passe en révision prioritaire, en commençant par les domaines les plus lourds (D1 27 %, D3 et D4 20 %).
2. À 2 sur 3, refaire la case manquante cette semaine.
3. Un domaine est prêt quand tous ses task statements sont à 3, ou à 2 avec la case manquante datée.
4. Mettez les cases « Trancher » et les scores du quiz en regard : un score au quiz élevé avec « Expliquer » vide signale une reconnaissance sans compréhension.

Cette grille reste une auto-évaluation : elle ne prédit pas la note, qui est échelonnée de 100 à 1 000 (seuil de 720) avec une conversion non publiée. Faites-la relire par un pair en atelier : on se surestime sur ce qu'on a lu et on se sous-estime sur ce qu'on a codé.


## Domaine 1 : Architecture agentique et orchestration (27 %)

| TS | Thème | Lab | Quiz | Expliquer | Appliquer | Trancher | Total |
|---|---|---|---|---|---|---|---|
| 1.1 | Boucles agentiques pilotées par stop_reason | 01 ex. 1 | 4 | [ ] | [ ] | [ ] | /3 |
| 1.2 | Coordinateur et sous-agents (hub-and-spoke) | 01 ex. 3 | 2 | [ ] | [ ] | [ ] | /3 |
| 1.3 | Lancer les sous-agents : outil Task, allowedTools, AgentDefinition, contexte explicite, appels parallèles | 01 ex. 3 | 3 | [ ] | [ ] | [ ] | /3 |
| 1.4 | Workflows à garanties : prérequis en code, demandes multi-sujets, transfert à un humain | 01 ex. 2, 05 ex. 2 | 3 | [ ] | [ ] | [ ] | /3 |
| 1.5 | Hooks de l'Agent SDK : PostToolUse et interception | 01 ex. 4 | 2 | [ ] | [ ] | [ ] | /3 |
| 1.6 | Décomposition de tâches : chaînage fixe ou adaptatif, revue par passes | 04 ex. 6, 05 ex. 4 | 2 | [ ] | [ ] | [ ] | /3 |
| 1.7 | Sessions : reprise nommée, fork, résultats périmés | 01 ex. 5 | 2 | [ ] | [ ] | [ ] | /3 |

Total du domaine 1 : ___ / 21

## Domaine 2 : Conception d'outils et intégration MCP (18 %)

| TS | Thème | Lab | Quiz | Expliquer | Appliquer | Trancher | Total |
|---|---|---|---|---|---|---|---|
| 2.1 | Descriptions d'outils et frontières entre outils | 02 ex. 1 | 3 | [ ] | [ ] | [ ] | /3 |
| 2.2 | Erreurs structurées MCP : isError, catégorie, isRetryable | 02 ex. 2, 05 ex. 3 | 3 | [ ] | [ ] | [ ] | /3 |
| 2.3 | Répartition des outils entre agents et tool_choice | 02 ex. 4 et 6, 04 ex. 1 | 2 | [ ] | [ ] | [ ] | /3 |
| 2.4 | Serveurs MCP dans Claude Code : .mcp.json, ~/.claude.json, ${VAR}, resources | 02 ex. 2 et 3 | 3 | [ ] | [ ] | [ ] | /3 |
| 2.5 | Outils intégrés : Read, Write, Edit, Bash, Grep, Glob | 02 ex. 5 | 2 | [ ] | [ ] | [ ] | /3 |

Total du domaine 2 : ___ / 15

## Domaine 3 : Configuration et workflows Claude Code (20 %)

| TS | Thème | Lab | Quiz | Expliquer | Appliquer | Trancher | Total |
|---|---|---|---|---|---|---|---|
| 3.1 | Hiérarchie des CLAUDE.md, @import, /memory | 03 ex. 1 | 3 | [ ] | [ ] | [ ] | /3 |
| 3.2 | Commandes slash et skills | 03 ex. 2 | 3 | [ ] | [ ] | [ ] | /3 |
| 3.3 | Règles par chemin (.claude/rules, paths) | 03 ex. 1 | 2 | [ ] | [ ] | [ ] | /3 |
| 3.4 | Mode plan ou exécution directe | 03 ex. 3 | 2 | [ ] | [ ] | [ ] | /3 |
| 3.5 | Affinage itératif : exemples, tests d'abord, mode interview | 03 ex. 4 | 2 | [ ] | [ ] | [ ] | /3 |
| 3.6 | Claude Code en CI/CD : -p, --output-format json, --json-schema | 03 ex. 5 | 3 | [ ] | [ ] | [ ] | /3 |

Total du domaine 3 : ___ / 18

## Domaine 4 : Prompt engineering et sortie structurée (20 %)

| TS | Thème | Lab | Quiz | Expliquer | Appliquer | Trancher | Total |
|---|---|---|---|---|---|---|---|
| 4.1 | Critères explicites contre les faux positifs | 04 ex. 4 | 2 | [ ] | [ ] | [ ] | /3 |
| 4.2 | Few-shot sur les cas ambigus | 04 ex. 4 | 2 | [ ] | [ ] | [ ] | /3 |
| 4.3 | Sortie structurée par tool use et JSON Schema | 04 ex. 1, 2 | 3 | [ ] | [ ] | [ ] | /3 |
| 4.4 | Validation, reprise, boucles de retour | 04 ex. 3 | 2 | [ ] | [ ] | [ ] | /3 |
| 4.5 | Traitement par lots (Message Batches) | 04 ex. 5 | 3 | [ ] | [ ] | [ ] | /3 |
| 4.6 | Revue multi-instances et multi-passes | 04 ex. 6 | 2 | [ ] | [ ] | [ ] | /3 |

Total du domaine 4 : ___ / 18

## Domaine 5 : Gestion du contexte et fiabilité (15 %)

| TS | Thème | Lab | Quiz | Expliquer | Appliquer | Trancher | Total |
|---|---|---|---|---|---|---|---|
| 5.1 | Préserver le contexte : faits critiques, troncature des sorties, effet « lost in the middle » | 05 ex. 1 | 5 | [ ] | [ ] | [ ] | /3 |
| 5.2 | Escalade et ambiguïté | 05 ex. 2 | 2 | [ ] | [ ] | [ ] | /3 |
| 5.3 | Propagation d'erreurs entre agents | 05 ex. 3 | 1 | [ ] | [ ] | [ ] | /3 |
| 5.4 | Exploration d'un gros dépôt | 05 ex. 4 et 5 | 1 | [ ] | [ ] | [ ] | /3 |
| 5.5 | Relecture humaine et calibration de la confiance | 04 ex. 7 | 1 | [ ] | [ ] | [ ] | /3 |
| 5.6 | Provenance des sources et incertitude | 05 ex. 3 | 2 | [ ] | [ ] | [ ] | /3 |

Total du domaine 5 : ___ / 18

## Journal des écarts

| Date | TS | Ce qui m'a manqué | Action | Fait |
|---|---|---|---|---|
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |
