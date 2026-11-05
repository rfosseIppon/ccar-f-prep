# Lab 05 : gestion du contexte et fiabilité (domaine 5, 15 %)

Durée : 3 heures 30. Scénarios concernés : support client, multi-agents, exploration de gros codebase.

Statut : code de départ (`starter/`), corrigé (`solution/`) et tests hors ligne fournis. Aucun appel à un modèle : le comportement d'un vrai modèle (consigne-t-il bien ses faits ? respecte-t-il le bloc de faits ?) n'a pas été mesuré. À faire après le lab 01.

## Use case

**Le dossier qui dure** (cas fictif). Trois situations d'un même client e-commerce :
1. Une cliente échange pendant 15 tours avec l'agent de support. Au tour 16, l'agent doit encore connaître le numéro de commande, le montant discuté et l'engagement pris, puis transmettre à un conseiller un dossier qu'il comprend sans relire la conversation.
2. Le rapport d'avant-vente du lab 01 doit sortir même quand une source est indisponible, en distinguant ce qui est confirmé, ce qui n'est pas couvert et ce qui peut être retenté.
3. Une question d'architecture transversale sur un dépôt de plus de 500 fichiers, à traiter sans saturer le contexte.

Livrable : bloc de faits réinjecté à chaque tour (3 faits exacts après 15 tours, historique tronqué), règles d'escalade et résumé de transfert autonome, rapport de panne partielle avec provenance et contradictions, notes d'exploration persistées avec décomposition adaptative, et le constat d'une exploration réelle sur un de vos dépôts.

Scénarios d'examen concernés : 1 (support client), 3 (multi-agents) et 4 (exploration de code).

## Cours Anthropic Academy associé

Aucun cours de la liste n'est dédié à ce domaine. Les plus proches :

- **Claude Code in Action** (https://anthropic.skilljar.com/claude-code-in-action) : module « Steer the Work » (cadrer avec le mode plan, diriger la compaction, revenir en arrière) et module « Verify and Share » (vérifier un run non supervisé). Appuie les exercices 1 et 4.
- **Introduction to subagents** (https://anthropic.skilljar.com/introduction-to-subagents) : leçons 1 et 4 (contexte séparé, synthèses renvoyées, quand déléguer). Appuie les exercices 3 et 4.
- **Building with the Claude API** (https://anthropic.skilljar.com/claude-with-the-anthropic-api) : bloc 7 « Fonctionnalités de Claude » (prompt caching, extended thinking), bloc 10 « Agents et workflows ».

Non couvert d'après les programmes lus : règles d'escalade, transmission d'un dossier autonome, gestion des pannes partielles. Ce lab s'appuie sur la documentation d'Anthropic sur la gestion du contexte et sur les scénarios du dépôt.

Quand : semaine 2, après le lab 01.

Cours en anglais, gratuits, compte Skilljar requis. Les pages consultées le 29 octobre 2026 n'indiquent pas de durée. Le rapprochement avec le lab est une proposition de l'équipe, établie sur les pages de présentation des cours : aucune correspondance officielle avec l'examen n'a été relevée.

## Objectifs

Task statements du guide d'examen : 5.1 à 5.6 et 1.6 (voir `EXAM-MAP.md`). Le détail des règles d'escalade et de provenance vient du guide lu via un résumé automatique : relisez le PDF.

- Garder les faits critiques disponibles dans une longue conversation, malgré la troncature de l'historique (5.1).
- Décider quand escalader, quand demander une précision, et transmettre un dossier autonome (5.2).
- Rendre compte d'une panne partielle sans cacher la lacune ni inventer (5.3).
- Garder la provenance de chaque affirmation et présenter les contradictions sans trancher (5.6).
- Explorer un gros dépôt sans saturer le contexte, avec des sous-tâches décidées au fil des découvertes (5.4, 1.6).

## Ce qui est fourni

| Fichier | Rôle |
|---|---|
| `fixtures05.py` | dossier de 15 tours (`case_events`, `build_history`, `replay`), sortie d'outil verbeuse, faux dépôt de 520 fichiers (`make_repo`), doublure d'un sous-agent d'exploration (`explore_module`) |
| `starter/*.py` | quatre modules à compléter : `case_facts`, `escalation`, `partial_failure`, `exploration` |
| `solution/*.py` | corrigé |
| `tests/` | `test_socle05.py` (intégrité du socle, passe toujours), puis un fichier de tests par module |

```bash
LAB_TARGET=solution pytest labs/05-context-reliability/tests   # corrigé : 97 tests verts
pytest labs/05-context-reliability/tests                       # votre starter : au départ 90 échecs, 7 réussites (socle)
```

## Exercice 1 : faits critiques (45 min)

Module `starter/case_facts.py`. Tests : `pytest labs/05-context-reliability/tests/test_case_facts.py`.

Le scénario : 15 tours, dont les trois faits critiques (commande O-1001, montant discuté, engagement de remboursement) apparaissent dans les 4 premiers. On n'envoie au modèle que les 4 derniers tours, ce qui est le cas d'une conversation tronquée ou compactée. Le test montre d'abord que l'historique tronqué a perdu le montant et l'engagement, puis que le bloc de faits les restitue mot pour mot.

À écrire : le registre `FactsLedger` (un fait plus récent remplace l'ancien et en garde la trace), la capture automatique des identifiants renvoyés par les outils, le gestionnaire de l'outil `note_fact` avec un message d'erreur exploitable, la description de cet outil, le rendu du bloc, `trim_tool_output`, `truncate_history`, `build_request`.

Points à justifier :
- pourquoi les faits sont dans le bloc de tête et non dans l'historique : un résumé progressif de conversation condense volontiers les montants et les dates, et les informations enfouies au milieu d'un long contexte sont moins bien exploitées que celles du début ou de la fin (effet « lost in the middle ») ;
- pourquoi on coupe l'historique par tours complets : un `tool_result` dont le `tool_use` a disparu est refusé par l'API ;
- pourquoi on réduit une sortie d'outil verbeuse à quelques champs avant qu'elle s'accumule dans le contexte (la sortie de test passe de plusieurs milliers de caractères à moins d'un quart) ;
- pourquoi le bloc est identique d'un tour à l'autre quand rien ne change.

Limite : le test vérifie le mécanisme, pas la fiabilité du modèle à appeler `note_fact` au bon moment. Ce point se constate avec un vrai modèle (exercice 5).

## Exercice 2 : escalade et transfert (45 min)

Module `starter/escalation.py`. Tests : `pytest labs/05-context-reliability/tests/test_escalation.py`.

À écrire : `decide`, qui applique les règles dans l'ordre, et `handoff_summary`. Les règles du lab, d'après le guide :
- le client demande un humain : on escalade tout de suite, sans enquête préalable ;
- plusieurs clients correspondent à la recherche : on demande un identifiant supplémentaire, on ne choisit pas selon une heuristique ;
- remboursement au-delà du plafond, demande hors du périmètre de la politique, blocage après plusieurs échecs : escalade ;
- client frustré : si le problème est dans le périmètre, on reconnaît la frustration et on propose de le résoudre ; on n'escalade que s'il insiste ensuite ;
- ni le ton du client ni une « confiance » déclarée par le modèle ne déclenchent seuls une escalade : ces signaux sont peu fiables.

Le résumé doit être lisible par un conseiller qui n'a pas la conversation : faits exacts, ce qui a été tenté, action recommandée. Un fait absent est écrit comme absent, jamais inventé.

Fourni : `asks_for_human`, une heuristique de repli sur le texte du client. Elle ne comprend pas toutes les formulations : dans un vrai agent, le modèle juge les cas ambigus et la règle de code garantit le cas net.

Questions à noter :
1. Quelles règles méritent un garde-fou en code, lesquelles restent au jugement du modèle ?
2. Pourquoi demander un identifiant plutôt que choisir le client « le plus probable » ?
3. Que se passe-t-il pour un client qui insiste alors que vous pouviez résoudre son problème ?

## Exercice 3 : panne partielle et provenance (50 min)

Module `starter/partial_failure.py`. Tests : `pytest labs/05-context-reliability/tests/test_partial_failure.py`.

À écrire : `run_with_recovery` (reprise locale des erreurs transitoires, remontée du reste avec ce qui a été tenté, aucune exception qui s'échappe), `find_conflicts`, `build_report`.

Quatre situations à ne pas confondre :

| Situation | Statut | Où dans le rapport |
|---|---|---|
| La source répond avec des résultats | `ok` | Confirmé, avec source, URL et date |
| La source répond sans rien contenir | `empty` | Citée comme absence de résultat, pas comme panne |
| Délai dépassé après plusieurs tentatives | `timeout` | Lacunes, à retenter |
| Accès refusé ou introuvable | `unreachable` | Lacunes, non couvert |

Deux sources qui donnent deux chiffres différents pour la même mesure forment une contradiction : le rapport montre les deux valeurs avec leur source et leur date, sans en choisir une. Une différence de date est signalée, parce qu'elle explique souvent l'écart. Une affirmation sans source exploitable n'est jamais « confirmée ».

Questions à noter :
1. Pourquoi une erreur générique « échec » rend-elle la récupération impossible pour le coordinateur ?
2. Que gagne-t-on à réessayer dans le sous-agent plutôt que dans le coordinateur ? Que perd-on si le sous-agent réessaie indéfiniment ?
3. Dans quel cas le coordinateur doit-il relancer une recherche plutôt que livrer le rapport avec ses lacunes ?

## Exercice 4 : exploration d'un gros dépôt (40 min)

Module `starter/exploration.py`. Tests : `pytest labs/05-context-reliability/tests/test_exploration.py`.

À écrire : le fichier de notes `Scratchpad` (ajout seulement, relu avant chaque phase, survit à la perte du contexte), `bound_synthesis` (ce que le sous-agent renvoie au contexte principal), `phase_brief` (consigne autonome), `next_subtasks` (décomposition adaptative : la suite dépend de ce qui vient d'être découvert).

Le test final explore le faux dépôt de 520 fichiers à partir du paquet `payments` : seuls les paquets atteignables sont explorés, et le contexte principal ne reçoit qu'une petite fraction du volume lu. C'est une simulation avec une doublure de sous-agent : elle prouve le mécanisme, pas le comportement d'un modèle.

Chaînage fixe ou adaptatif (1.6) : une passe par fichier suivie d'une passe transversale (lab 04, exercice 6) convient quand on connaît d'avance la liste des éléments ; une exploration dont les prochaines étapes dépendent des découvertes demande une décomposition adaptative.

## Exercice 5 : sur un vrai dépôt (30 min, non testé)

Pas de code à rendre. Sur un de vos dépôts de plus de 500 fichiers, posez une question d'architecture transversale (par exemple « quels modules appellent le service de facturation et par quel chemin ? »).
1. Première passe dans une session unique ; notez le nombre d'échanges et ce que l'agent oublie ou répète.
2. Seconde passe : sous-agents d'exploration qui renvoient des synthèses, et un fichier de notes que vous relisez au début de chaque phase. Si le contexte se compacte, dirigez la compaction (vérifiez la syntaxe de `/compact` dans votre version).
3. Comparez et consignez le résultat dans le suivi de l'artefact.

Avec un vrai modèle, vérifiez aussi l'exercice 1 : dans une conversation d'une quinzaine d'échanges, l'agent appelle-t-il `note_fact` quand le client donne un montant ? Retrouve-t-il l'engagement pris après troncature ?

## Critères de réussite

- Les 97 tests passent sur votre `starter/`.
- Les trois faits critiques sont restitués exactement après 15 tours, historique tronqué.
- Vous expliquez pourquoi le ton du client n'est pas un critère d'escalade.
- Le rapport sépare « confirmé », « non couvert » et « à retenter », et montre les contradictions sans les trancher.
- Le résumé d'escalade est compris par quelqu'un qui n'a pas vu la conversation (test avec un collègue : donnez-lui seulement le résumé).

## Pièges fréquents

- Faire confiance à l'historique brut ou à un résumé progressif pour garder montants et dates.
- Laisser une sortie d'outil de plusieurs milliers de caractères s'accumuler à chaque tour.
- Couper l'historique au milieu d'un échange d'outils.
- Escalader sur le ton ou sur une confiance auto-déclarée ; ou escalader trop tard, après plusieurs échecs évitables.
- Choisir un client parmi plusieurs correspondances sans le demander.
- Un message d'erreur « échec » sans catégorie, sans mention de réessayable, sans ce qui a été tenté.
- Traiter une absence de résultat comme une panne, ou une panne comme une absence de résultat.
- Supprimer l'échec d'un sous-agent, ou au contraire arrêter tout le travail à cause de lui.
- Trancher en silence entre deux chiffres contradictoires, ou prendre un écart de date pour une contradiction.
- Résultats de sous-agents recollés tels quels dans le contexte principal, sans synthèse.

## Limites connues

- Les tests ne mesurent pas la fiabilité d'un modèle réel, seulement les mécanismes en code.
- L'heuristique `asks_for_human` couvre des formulations courantes en français et en anglais, pas toutes.
- L'exploration du test utilise une doublure de sous-agent et un dépôt fabriqué : le gain de contexte chiffré est un ordre de grandeur de mécanisme.
- Les règles d'escalade et de provenance reposent sur le guide d'examen lu via un résumé automatique.

## Références à ouvrir

Documentation d'Anthropic sur la gestion du contexte, les sous-agents et les fichiers de notes ; cours « Introduction to subagents » et « Claude Code in Action » (voir plus haut).
