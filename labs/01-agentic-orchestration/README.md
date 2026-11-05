# Lab 01 : architecture agentique et orchestration (domaine 1, 27 %)

Durée : 3 heures 30. Scénarios concernés : agent de support client, système de recherche multi-agents.

## Use case

**Agent de support d'un e-commerçant** (cas fictif). Un distributeur en ligne veut qu'un agent traite retours et remboursements dès le premier contact. Règles du client : pas de remboursement sans client identifié, uniquement sur ses propres commandes, et au-delà de 100 EUR un conseiller prend la main. Un incident récent a coûté cher : l'agent avait remboursé une commande qui n'appartenait pas au client en ligne. Les exercices 1 et 2 construisent cet agent et ses garde-fous.

Second cas pour l'exercice 3 : **dossier d'avant-vente**. Avant un rendez-vous, un coordinateur confie à trois sous-agents (recherche, analyse, rédaction) la préparation d'une note sur un prospect. Une source est inaccessible le jour J : la note doit le dire au lieu de combler le trou.

Livrable : tous les tests verts (agent, multi-agents, hooks), un rapport multi-agents avec section « Lacunes », et l'explication orale de la différence entre guidage par prompt et garde-fou en code.

Scénarios d'examen concernés : 1 (support client) et 3 (recherche multi-agents).

## Cours Anthropic Academy associé

- **Introduction to subagents** (https://anthropic.skilljar.com/introduction-to-subagents) : les 4 leçons (contexte séparé, création, conception, quand déléguer et anti-patterns). Appuie les exercices 3 et 4.
- **Building with the Claude API** (https://anthropic.skilljar.com/claude-with-the-anthropic-api) : bloc 5 « Tool use » (blocs de messages, renvoi des résultats, plusieurs outils) pour l'exercice 1, et bloc 10 « Agents et workflows » (chaînage, routage, parallélisation, workflows contre agents) pour la conception du coordinateur.

Non couvert d'après les programmes lus : garde-fous métier en code, hooks de l'Agent SDK, plafond d'itérations, reprise et bifurcation de session. À travailler avec la documentation de Claude Code et de l'Agent SDK, et les exercices.

Quand : semaine 1.

Cours en anglais, gratuits, compte Skilljar requis. Les pages consultées le 29 octobre 2026 n'indiquent pas de durée. Le rapprochement avec le lab est une proposition de l'équipe, établie sur les pages de présentation des cours : aucune correspondance officielle avec l'examen n'a été relevée.

## Objectifs

Task statements du guide d'examen : 1.1 à 1.7 (voir `EXAM-MAP.md`).

- Écrire une boucle agentique pilotée par `stop_reason`, sans heuristique sur le texte du modèle.
- Distinguer ce qui se règle dans le prompt (guidage) de ce qui se garantit en code (règle métier non négociable).
- Concevoir un coordinateur et des sous-agents : rôles, outils minimaux, contexte transmis explicitement, délégations parallèles, sources conservées.
- Écrire deux hooks de l'Agent SDK : bloquer un appel en amont, normaliser un résultat en aval.
- Prévoir les pannes partielles et un garde-fou contre les boucles sans fin.

## Exercice 1 : la boucle (45 min)

Dans `starter/agent.py`, implémentez `run_agent`. Tests : `pytest labs/01-agentic-orchestration/tests/test_agent.py -k "not refund and not escalation and not bad_calls"`.

À savoir justifier :
- pourquoi tous les `tool_result` d'un même tour reviennent dans un seul message utilisateur ;
- pourquoi `end_turn` est la seule condition de sortie normale, et ce qu'on fait des autres `stop_reason` ;
- pourquoi un plafond d'itérations est un filet de sécurité et jamais la condition de sortie normale (le guide d'examen range le plafond arbitraire utilisé comme condition de fin parmi les anti-patterns), et pourquoi on escalade à son atteinte plutôt que de lever une exception.

## Exercice 2 : garde-fous en code (45 min)

Dans `starter/agent.py`, implémentez `execute_tool`. Tests : `pytest labs/01-agentic-orchestration/tests/test_agent.py`.

Le prompt dit « identifie toujours le client avant d'agir ». Un modèle peut quand même l'oublier. Les règles suivantes doivent tenir même si le modèle se trompe :
- prérequis : pas de remboursement sans client identifié ;
- propriété : on ne rembourse que les commandes du client identifié ;
- plafond : au-delà de 100 EUR, refus en code et consigne d'escalade dans le message d'erreur.

Demande à plusieurs sujets : le test `two_refunds` envoie deux remboursements dans le même tour, un valide et un hors plafond. Chaque appel est contrôlé séparément et les deux résultats reviennent ensemble.

Questions de conception à noter :
1. Quelles règles méritent un garde-fou en code, lesquelles peuvent rester dans le prompt ?
2. Pourquoi l'erreur de prérequis est-elle réessayable et celle du plafond non ?
3. Que perd-on si le message d'erreur est un simple « échec » ?

## Exercice 3 : coordinateur et sous-agents (60 min)

Dans `starter/multi_agent_research.py`, définissez le prompt du coordinateur et trois sous-agents (searcher, analyst, writer). Tests de configuration : `pytest labs/01-agentic-orchestration/tests/test_multi_agent.py`. Ils vérifient les outils et le texte des consignes, pas le comportement du modèle. L'exécution réelle demande une clé API et n'a pas été testée à la préparation du dépôt.

Points de contrôle :
- chaque sous-agent a la liste d'outils la plus courte possible ;
- le coordinateur ne dispose que de l'outil de délégation (« Task » dans le guide d'examen, « Agent » dans les versions récentes : vérifiez la vôtre) ;
- la consigne de délégation contient tout le contexte utile, car un sous-agent ne voit pas l'historique du coordinateur ;
- les sous-questions indépendantes sont déléguées dans le même tour ;
- le sous-agent de recherche renvoie les affirmations et leurs métadonnées (URL, nom de la source, date) séparément, pour que l'attribution survive à la synthèse ;
- un sous-agent en échec n'arrête pas la recherche, et le rapport final signale les lacunes ;
- le coordinateur distingue « source inaccessible » de « source consultée, rien trouvé » et relance une recherche si la couverture est insuffisante.

Essayez ensuite de faire échouer volontairement une recherche (sujet inexistant) et observez le rapport.

## Exercice 4 : hooks de l'Agent SDK (30 min)

Dans `starter/hooks.py`, implémentez deux hooks et leur branchement. Tests : `pytest labs/01-agentic-orchestration/tests/test_hooks.py`.

- `block_large_refund` (PreToolUse) : refuse `process_refund` au-dessus du plafond, avec la raison et la suite à donner.
- `normalize_tool_result` (PostToolUse) : transforme les timestamps Unix en dates ISO 8601 et les codes de statut numériques en libellés avant que le modèle lise le résultat.
- `build_hooks` : les enregistre dans les options de l'agent.

Questions de conception à noter :
1. Ce plafond existe déjà dans `execute_tool` (exercice 2). Quand le placer dans un hook plutôt que dans la boucle que vous écrivez vous-même ?
2. Pourquoi un hook donne-t-il une garantie que le prompt ne donne pas ?
3. Que se passe-t-il si le hook plante ? Vérifiez dans la documentation des hooks de votre version.
4. Pourquoi normaliser les formats avant que le modèle lise le résultat, plutôt que de lui demander de s'y retrouver ?

## Exercice 5 : sessions (30 min, discussion)

Dans Claude Code, comparez la reprise d'une session (`claude --resume`) et sa bifurcation (`claude --resume ... --fork-session`). Vérifiez les options de votre version avec `claude --help`.

Questions :
- Dans quel cas faut-il repartir d'un contexte neuf avec un résumé plutôt que reprendre une longue session ?
- Vous reprenez une investigation nommée après que des fichiers ont changé : que dites-vous à l'agent ? Que faites-vous si les résultats d'outils de la session précédente sont périmés ?
- Deux stratégies de test à comparer à partir d'une même analyse : reprise ou bifurcation ?

## Critères de réussite

- Tous les tests passent sur votre `starter/` (agent, multi-agents, hooks).
- Vous expliquez à voix haute, en 2 minutes, la différence entre guidage par prompt et garde-fou en code (ou hook), avec un exemple du lab.
- Votre multi-agent produit un rapport avec une section « Lacunes » non vide quand une recherche échoue.

## Pièges fréquents

- Sortir de la boucle en cherchant un mot-clé dans le texte au lieu de lire `stop_reason`, ou prendre le plafond d'itérations pour la condition de sortie.
- Renvoyer un `tool_result` par message, ou oublier le `tool_use_id`.
- Confier à tous les sous-agents tous les outils.
- Compter sur le prompt pour appliquer un plafond financier.
- Supposer que le sous-agent connaît ce que le coordinateur a lu.
- Résumer les résultats des sous-agents sans garder la source de chaque affirmation.
- Écrire un hook de normalisation sans le tester sur un vrai résultat d'outil : la forme de `tool_response` dépend de l'outil et de la version.

## Pour aller plus loin

Quiz et scénario à décision du domaine 1 : artefact d'étude partagé de l'équipe.
