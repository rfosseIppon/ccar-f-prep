# Lab 02 : conception d'outils et MCP (domaine 2, 18 %)

Durée : 4 heures. Scénarios concernés : outils de productivité développeur, support client, multi-agents.

Statut : socle, code de départ (`starter/`), corrigé (`solution/`) et tests hors ligne fournis. `run_selection.py` et `run_tool_choice.py` appellent un vrai modèle et demandent une clé API : ils n'ont pas été exécutés à la préparation du dépôt.

## Use case

**Outils d'accès aux commandes pour l'agent d'un client e-commerce** (cas fictif). Trois équipes du client ont chacune exposé une fonction de recherche de commandes (`search_orders`, `find_orders`, `lookup_order`) avec des descriptions floues. L'agent choisit mal, répond à côté et, quand une fonction échoue, reçoit une exception brute. L'équipe de développement veut aussi ces outils dans Claude Code pour explorer le code et les données de test.

Mission : rendre le choix d'outil fiable (descriptions, répartition entre agents), faire remonter des erreurs exploitables, puis packager les outils dans un serveur MCP branché via `.mcp.json`.

Livrable : tableau avant/après de sélection (au moins 18 bonnes sélections sur 20, mesuré avec un vrai modèle), serveur MCP de 3 outils avec un test par cas d'échec, `.mcp.json` qui lance ce serveur, répartition argumentée de 15 outils entre 3 agents, résultat de la sonde `tool_choice` sur votre modèle.

Scénarios d'examen concernés : 4 (productivité développeur), 1 (support client) et 3 (multi-agents).

## Cours Anthropic Academy associé

- **Introduction to Model Context Protocol** (https://anthropic.skilljar.com/introduction-to-model-context-protocol) : serveur Python, définition d'outils par décorateurs, inspecteur, ressources et prompts, client. Appuie l'exercice 2.
- **Model Context Protocol: Advanced Topics** (https://anthropic.skilljar.com/model-context-protocol-advanced-topics) : sampling, notifications, roots, transports STDIO et StreamableHTTP. Utile pour le choix du transport ; la page indiquait que certaines vidéos étaient encore en cours de traitement.
- **Building with the Claude API** (https://anthropic.skilljar.com/claude-with-the-anthropic-api) : bloc 5 « Tool use » (schémas d'outils, plusieurs outils) et bloc 8 « Model Context Protocol », pour l'exercice 1.

Non couvert d'après les programmes lus : rédaction de descriptions qui évitent les chevauchements, erreurs structurées (`errorCategory`, `isRetryable`, drapeau `isError`), répartition des outils entre agents. À travailler avec la documentation MCP et celle de l'API (tool use).

Quand : semaine 2.

Cours en anglais, gratuits, compte Skilljar requis. Les pages consultées le 29 octobre 2026 n'indiquent pas de durée. Le rapprochement avec le lab est une proposition de l'équipe, établie sur les pages de présentation des cours : aucune correspondance officielle avec l'examen n'a été relevée.

## Objectifs

Task statements du guide d'examen : 2.1 à 2.5 (voir `EXAM-MAP.md`).

- Écrire des descriptions d'outils qui permettent au modèle de choisir le bon outil (2.1).
- Renvoyer des erreurs structurées (`errorCategory`, `isRetryable`, message, étape suivante) avec le drapeau MCP `isError`, et distinguer un échec d'accès d'un résultat vide valide (2.2).
- Répartir les outils entre agents et connaître les valeurs de `tool_choice` (2.3).
- Déclarer un serveur MCP pour Claude Code : portées, `.mcp.json`, variables d'environnement, ressources (2.4).
- Choisir l'outil intégré de Claude Code adapté à une tâche (2.5).

## Version du SDK Python `mcp`

Le SDK existe en deux versions majeures : 1.x (`FastMCP`, celle du cours Academy) et 2.x (renommé `MCPServer`, client différent). Le fichier `mcp_compat.py` (fourni) masque la différence : le corrigé et les tests ont été exécutés avec mcp 1.30 et mcp 2.3 et passent dans les deux cas. Le protocole, lui, ne change pas : un résultat d'erreur porte `isError: true`.

## Ce qui est fourni

| Fichier | Rôle |
|---|---|
| `shop_backend.py` | faux back-office : 6 commandes fictives, pannes injectables (`fail_next("timeout")`, `down = True`) |
| `baseline.py` | les 3 outils dans l'état « avant » : descriptions floues, schémas corrects |
| `corpus/queries.json` | 20 demandes avec l'outil attendu (7 `lookup_order`, 7 `find_orders`, 6 `search_orders`) |
| `selection.py`, `run_selection.py` | mesure du taux de bon choix (vrai modèle) |
| `mcp_compat.py` | compatibilité SDK 1.x / 2.x, client en mémoire et client stdio pour les tests |
| `mcp_config.py` | lecture et contrôle d'un `.mcp.json` |
| `tools15.py`, `builtin_tasks.py` | données des exercices 4 et 5 |

Les trois outils : `lookup_order` (une commande, par numéro exact et e-mail du demandeur), `find_orders` (les commandes d'un client), `search_orders` (recherche libre dans les articles, sans coordonnées de client).

## Exercice 1 : descriptions qui se chevauchent (45 min)

Dans `starter/tool_defs.py`, réécrivez les trois descriptions : ce que fait l'outil avec un exemple de valeur, quand le préférer, ce qu'il ne fait pas et l'outil voisin à utiliser à la place. Tests : `pytest labs/02-tools-mcp/tests/test_descriptions.py`. Ils vérifient la forme (longueur, exemple, négation, outils voisins nommés, pas de quasi-doublon) : ce sont des garde-fous, pas une mesure de qualité.

La mesure se fait avec un vrai modèle, avant puis après :

```bash
python labs/02-tools-mcp/run_selection.py --baseline      # descriptions floues d'origine
python labs/02-tools-mcp/run_selection.py --target starter   # vos descriptions
```

Critère : au moins 18 bonnes sélections sur 20 après réécriture, avec le tableau avant/après. Regardez les demandes ratées : une confusion persistante signale une frontière mal tracée entre deux outils.

## Exercice 2 : serveur MCP et erreurs structurées (75 min)

Dans `starter/shop_server.py`, implémentez les trois outils, la fonction `failure` et la ressource `shop://status-glossary`. Chaque échec prévisible renvoie un résultat d'erreur avec les champs `errorCategory` (`transient`, `validation`, `permission` ou `business`), `isRetryable`, `message` et `nextStep` :

| Cas | Catégorie | Réessayable |
|---|---|---|
| numéro de commande, e-mail, statut ou date invalide | validation | non |
| commande d'un autre client (ne rien révéler d'elle) | permission | non |
| commande inexistante, commande archivée | business | non |
| délai dépassé, service indisponible | transient | oui |
| client sans commande, recherche sans résultat | pas une erreur : résultat valide et vide | |

Tests : `pytest labs/02-tools-mcp/tests/test_server.py`. Ils parlent au serveur comme un vrai client MCP et lisent le drapeau `isError`.

Questions à noter :
1. Pourquoi « aucun résultat » n'est-il pas une erreur, alors qu'« échec d'accès » en est une ? Que ferait un agent qui prendrait l'un pour l'autre ?
2. Que reçoit le modèle quand une exception brute remonte du serveur ? Essayez : avec le starter, chaque appel lève `NotImplementedError`. Notez le texte reçu.
3. Pourquoi le message de l'erreur de permission ne contient-il ni le nom du titulaire ni le contenu de la commande ?
4. Pourquoi le champ `nextStep` aide-t-il plus qu'un simple message ?

Pour tester à la main : `npx @modelcontextprotocol/inspector python labs/02-tools-mcp/solution/shop_server.py` (vérifiez la syntaxe de votre version de l'inspecteur).

## Exercice 3 : branchement dans Claude Code (40 min)

Écrivez `starter/.mcp.json` pour lancer le serveur en stdio. Tests : `pytest labs/02-tools-mcp/tests/test_mcp_config.py` (le dernier test démarre le serveur comme le ferait Claude Code et liste ses outils).

Les trois portées d'un serveur MCP dans Claude Code (page « MCP » de la documentation, consultée le 29 octobre 2026) :

| Portée | Chargée dans | Partagée avec l'équipe | Stockée dans |
|---|---|---|---|
| locale (par défaut) | le projet courant | non | `~/.claude.json`, sous le chemin du projet |
| projet | le projet courant | oui, par le contrôle de version | `.mcp.json` à la racine |
| utilisateur | tous vos projets | non | `~/.claude.json` |

En cas de nom identique, la définition locale l'emporte sur celle du projet, puis de l'utilisateur, sans fusion des champs. Les variables `${VAR}` et `${VAR:-défaut}` sont développées dans `command`, `args`, `env`, `url` et `headers` ; une variable sans valeur ni défaut reste telle quelle et déclenche un avertissement. Les secrets s'écrivent donc `${NOM}` dans le fichier versionné, jamais en clair.

À essayer avec Claude Code (version 2.1.312 testée pour ce lab) :

```bash
claude mcp add --scope project shop -e 'SHOP_API_KEY=${SHOP_API_KEY:-demo-key}' -- python3 shop_server.py
claude mcp list
```

La commande écrit un `.mcp.json` (vérifié). Un serveur de portée projet demande une approbation dans une session interactive : `claude mcp list` l'affiche « Pending approval » tant que vous ne l'avez pas donnée, et `claude mcp reset-project-choices` réinitialise ces choix. Dans une session `claude -p`, l'invite ne peut pas s'afficher et le serveur est chargé sans demande : à retenir pour la CI (lab 03).

Sous Windows, la commande est probablement `python` et non `python3` : non vérifié.

Les ressources MCP (exercice 2) servent à exposer des données consultables sans appel d'outil ; la manière de les référencer dans Claude Code se trouve dans la page « MCP » de la documentation : consultez-la, elle n'a pas été relevée pour ce lab.

## Exercice 4 : répartition des outils entre agents (30 min)

Dans `starter/distribution.py`, répartissez les 15 outils de `tools15.py` entre 3 agents spécialisés et justifiez chaque frontière en une phrase. Tests : `pytest labs/02-tools-mcp/tests/test_distribution.py` (chaque outil une fois, 4 ou 5 outils par agent, 2 domaines au plus, 2 outils qui écrivent au plus). Question : pourquoi une liste courte d'outils améliore-t-elle le choix, et que perd-on à trop spécialiser ?

## Exercice 5 : outils intégrés de Claude Code (30 min)

Dans `starter/builtin_tools.py`, associez chacune des 9 tâches de `builtin_tasks.py` à un outil : Read, Write, Edit, Bash, Grep, Glob. Tests : `pytest labs/02-tools-mcp/tests/test_builtin_tools.py`. Vérifiez vos réponses dans Claude Code en donnant chaque tâche. Point à comprendre : Edit exige un texte unique dans le fichier ; quand il ne l'est pas, élargir le contexte autour de la chaîne, remplacer toutes les occurrences ou passer par Read puis Write.

## Exercice 6 : `tool_choice` (20 min)

Le guide d'examen décrit trois valeurs : `auto` (le modèle décide), `any` (un outil au moins est appelé) et un outil précis. La documentation de l'API indique que sur les modèles récents (Sonnet 5.5, Opus 5.5, Fable 5.1, Mythos 5.1) `any` et l'outil précis renvoient une erreur 400, et que seul `auto` est accepté. Cette indication n'est pas recoupée : vérifiez-la.

Dans `starter/tool_choice_probe.py`, écrivez la sonde, puis lancez `python labs/02-tools-mcp/run_tool_choice.py --target starter`. Consignez le résultat avec le modèle et la date. Tests (faux modèle) : `pytest labs/02-tools-mcp/tests/test_tool_choice.py`. À l'examen, les questions suivent le guide : sachez ce que fait chaque valeur.

## Tout vérifier

```bash
LAB_TARGET=solution pytest labs/02-tools-mcp/tests   # corrigé : tout passe, sans clé API
pytest labs/02-tools-mcp/tests                       # votre starter
```

## Critères de réussite

- Tous les tests passent sur votre `starter/`.
- Tableau avant/après de sélection, avec au moins 18 bonnes sélections sur 20 (vrai modèle).
- Chaque cas d'échec du tableau de l'exercice 2 a son test et son `nextStep`.
- Vous expliquez la différence entre erreur d'accès et résultat vide, et entre erreur réessayable et définitive.
- Résultat de la sonde `tool_choice` consigné avec le modèle et la date.

## Pièges fréquents

- Deux outils dont les descriptions se recouvrent, ou une description qui explique l'implémentation au lieu de l'usage.
- Exception brute qui remonte au modèle sans catégorie ni consigne.
- Résultat vide traité comme une erreur (l'agent conclut « panne » au lieu de « aucun résultat »), ou l'inverse.
- Erreur de permission qui révèle le contenu de la ressource refusée.
- Erreur réessayable et erreur définitive traitées pareil.
- Un secret en clair dans un `.mcp.json` versionné.
- Un seul agent avec tous les outils du système.

## Limites connues

- Le choix d'outil par un vrai modèle n'a pas été mesuré à la préparation : seuls les tests hors ligne ont été exécutés. Les contrôles sur le texte des descriptions sont grossiers.
- Les portées, la syntaxe des variables et le comportement d'approbation viennent de la documentation de Claude Code et d'un essai du CLI en version 2.1.312 ; ils peuvent changer.
- La commande de l'inspecteur MCP et la syntaxe sous Windows n'ont pas été vérifiées.

## Références à ouvrir

Documentation Claude Code (page « MCP »), documentation MCP (spécification et SDK Python), documentation de l'API (tool use, `tool_choice`), cours Anthropic Academy sur MCP.
