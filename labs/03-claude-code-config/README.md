# Lab 03 : configuration et workflows Claude Code (domaine 3, 20 %)

Durée : 4 heures. Scénarios concernés : génération de code avec Claude Code, Claude Code en CI/CD, productivité développeur.

Statut : dépôt d'exemple, code de départ (`starter/`), corrigé (`solution/`) et tests hors ligne fournis. La revue CI du corrigé a été exécutée une fois avec le vrai CLI (version 2.1.312) sur le diff d'exemple ; le comportement de vos fichiers de configuration dans Claude Code reste à constater par vous (voir « Limites connues »).

## Use case

**Quatre consultants, un même dépôt client** (cas fictif). Chacun configure Claude Code à sa façon : les résultats diffèrent d'une personne à l'autre, un CLAUDE.md de 400 lignes n'est plus suivi, et une migration d'API sur 40 fichiers a été lancée sans plan. Le client demande aussi une revue automatique des pull requests, sans que le relecteur voie le raisonnement qui a produit le code.

Mission : une configuration partagée et versionnée (CLAUDE.md court, règles par chemin, skill de revue de sécurité à contexte isolé), une règle de choix entre mode plan et exécution directe, et un script de revue pour la CI dont la sortie JSON est lue par un programme.

Livrable : `CLAUDE.md` plus `.claude/` (règles, skill de revue, commande), tableau des 5 tâches avec le mode choisi, script de revue pour la CI avec 3 critères explicites et sortie JSON validée par un schéma, workflow GitHub Actions.

Scénarios d'examen concernés : 2 (génération de code), 5 (Claude Code en CI/CD) et 4 (productivité développeur).

## Cours Anthropic Academy associé

- **Claude Code in Action** (https://anthropic.skilljar.com/claude-code-in-action) : pilotage des sessions et mode plan, CLAUDE.md, skills, modes de permission, hooks, mode headless, GitHub Actions et revue de code, plugins. Couvre les exercices 1, 3 et 4.
- **Introduction to agent skills** (https://anthropic.skilljar.com/introduction-to-agent-skills) : 6 modules (frontmatter et description, divulgation progressive, `allowed-tools`, partage, dépannage). Appuie l'exercice 2.
- **Claude Code 101** (https://anthropic.skilljar.com/claude-code-101), en rattrapage : workflows quotidiens, CLAUDE.md, subagents, skills, MCP, hooks. Public annoncé : débutants et ingénieurs qui découvrent les agents de codage.

Non cité dans les pages de présentation : règles par chemin (`.claude/rules/` et clé `paths`), `context: fork`, options exactes de `claude -p`. À travailler avec la documentation de Claude Code (code.claude.com/docs).

Quand : semaine 3.

Cours en anglais, gratuits, compte Skilljar requis. Les pages consultées le 29 octobre 2026 n'indiquent pas de durée. Le rapprochement avec le lab est une proposition de l'équipe, établie sur les pages de présentation des cours : aucune correspondance officielle avec l'examen n'a été relevée.

## Objectifs

Task statements du guide d'examen : 3.1 à 3.6 (voir `EXAM-MAP.md`).

- Structurer les instructions : CLAUDE.md utilisateur, projet et sous-dossier, `@import`, règles modulaires (3.1).
- Écrire un skill avec `context: fork` et une commande slash avec argument (3.2).
- Limiter une règle à certains chemins avec `.claude/rules/` et la clé `paths` (3.3).
- Choisir entre mode plan et exécution directe (3.4).
- Affiner par itération : exemples, tests d'abord, entretien préalable, un message ou plusieurs (3.5).
- Lancer Claude Code en non interactif dans une CI : `claude -p`, `--output-format json`, `--json-schema`, constats nouveaux seulement, relecteur indépendant (3.6).

## Faits à connaître (documentation consultée le 29 octobre 2026)

| Sujet | Ce que dit la documentation |
|---|---|
| Chargement | `CLAUDE.md` et `CLAUDE.local.md` du dossier de travail et de ses parents se chargent au lancement ; ceux des sous-dossiers se chargent quand Claude lit, écrit ou modifie un fichier de ce sous-dossier |
| Priorité | Les fichiers sont concaténés, pas écrasés : le plus proche du dossier de travail est lu en dernier. Deux consignes contradictoires donnent un résultat arbitraire : évitez le conflit |
| Taille | Cible : moins de 200 lignes par fichier ; au-delà, l'adhésion baisse |
| Import | `@chemin` importe un fichier (relatif au fichier qui l'importe, 4 niveaux au plus) ; sans effet dans un bloc de code ou entre accents graves |
| Règles | `.claude/rules/*.md`, une par sujet. Sans `paths` : chargées au lancement. Avec `paths` (liste YAML ou chaîne séparée par des virgules) : chargées quand Claude utilise Read, Write ou Edit sur un fichier correspondant. Si le YAML est illisible, le frontmatter est ignoré et la règle se charge partout (`claude --debug` affiche l'erreur) |
| Fichier personnel | `CLAUDE.local.md`, à mettre dans `.gitignore` |
| Garantie | CLAUDE.md et règles sont du contexte, pas de la configuration appliquée : pour interdire une action, un hook PreToolUse ou une règle de permission |
| Skill | `.claude/skills/<nom>/SKILL.md`. `description` décide du déclenchement. `context: fork` : le contenu du skill devient le prompt d'un sous-agent qui ne voit pas la conversation (`agent` choisit son type). `allowed-tools` pré-approuve des outils pour le tour : il ne restreint rien. `disallowed-tools` retire des outils. `argument-hint` s'affiche à l'autocomplétion |
| Commande slash | `.claude/commands/<nom>.md` et un skill du même nom créent la même commande ; la doc recommande les skills pour les nouveaux besoins. `$ARGUMENTS` reçoit les arguments saisis |
| Mode non interactif | `claude -p`, `--output-format text|json|stream-json`, `--json-schema` (le résultat est dans `structured_output`, absent si le modèle n'a pas produit de sortie valide), `--allowedTools`, `--permission-mode`, `--append-system-prompt`, `--bare` (recommandé pour la CI : ne charge ni hooks, ni CLAUDE.md, ni serveurs MCP du poste) |

À noter sur la version 2.1.312 testée : `claude --help` ne liste pas `--max-turns`, que la documentation de l'action GitHub cite pourtant dans `claude_args` ; une exécution avec `--max-turns 1` a été acceptée. Le script du lab utilise `--max-budget-usd` (documenté dans `--help`) pour plafonner le coût.

## Ce qui est fourni

| Fichier | Rôle |
|---|---|
| `sample_repo/` | dépôt d'exemple « factu-api » (Python), avec `docs/architecture.md` et `pr.diff` (une injection SQL et une signature changée sans mise à jour de l'appelant) |
| `context_sim.py` | simulation du chargement des instructions, d'après les règles du tableau ci-dessus |
| `config_checks.py` | contrôles de forme d'un skill et d'une commande |
| `plan_tasks.py` | tâches et situations des exercices 3 et 4 |
| `run_ci_review.py` | lance votre revue CI avec le vrai CLI sur le diff d'exemple |

Votre travail va dans `starter/config/` (fichiers de configuration, recopiés par les tests sur le dépôt d'exemple) et `starter/*.py`.

## Exercice 1 : hiérarchie d'instructions (60 min)

Dans `starter/config/` : un `CLAUDE.md` racine (commandes de test, architecture importée par `@docs/architecture.md`, contraintes), `.claude/rules/testing.md` (sans `paths`), `.claude/rules/api.md` limitée à `src/api/**/*.py`, `src/api/CLAUDE.md` (consigne locale qui ne répète pas la racine) et `.gitignore` contenant `CLAUDE.local.md`. Tests : `pytest labs/03-claude-code-config/tests/test_instructions.py`.

Les tests simulent le chargement : au lancement seuls la racine, l'import et les règles sans `paths` sont chargés ; l'accès à `src/api/invoices.py` charge la règle de l'API et le `CLAUDE.md` local ; l'accès à `src/billing/` ne charge ni l'un ni l'autre.

Dans Claude Code, vérifiez à la main : `/memory` liste vos fichiers CLAUDE.md et de mémoire. Demandez à Claude de lire `src/api/invoices.py` puis de vous dire quelles consignes il applique. Notez l'écart éventuel avec la simulation.

Questions à noter : pourquoi une règle propre à un dossier ne va-t-elle pas dans le CLAUDE.md racine ? Que se passe-t-il si le YAML de `paths` est mal formé ? Pourquoi un CLAUDE.md ne garantit-il pas qu'une interdiction est respectée ?

## Exercice 2 : un skill à contexte isolé et une commande (60 min)

Dans `starter/config/.claude/` :
- `skills/revue-securite/SKILL.md` : description qui dit quand l'utiliser, `context: fork`, `argument-hint`, 3 critères explicites (injection SQL, secret en dur, contrôle d'accès absent), liste de ce qu'il faut ignorer, format de réponse, `allowed-tools` en lecture seule **et** `disallowed-tools` pour retirer Edit et Write ;
- `commands/test-module.md` : `argument-hint`, `$ARGUMENTS`, pré-approbation limitée à `Bash(python -m pytest *)`.

Tests : `pytest labs/03-claude-code-config/tests/test_skill_command.py`.

Pourquoi les deux champs d'outils ? `allowed-tools` pré-approuve : les autres outils restent appelables. Pour interdire, `disallowed-tools`. Dans Claude Code, essayez `/revue-securite src/api` : le skill s'exécute dans un sous-agent qui ne voit pas la conversation. Notez ce qu'il renvoie.

## Exercice 3 : plan ou exécution directe (30 min)

Dans `starter/choices.py` : pour les 5 tâches de `plan_tasks.py`, `PLAN_OR_DIRECT` et une phrase de justification. Tests : `pytest labs/03-claude-code-config/tests/test_choices.py -k "mode or justification"`. La règle de décision, d'après le guide : plan pour les changements à grande échelle, plusieurs approches possibles ou décisions d'architecture ; exécution directe pour un changement dont le périmètre est clair.

## Exercice 4 : affinage itératif (30 min)

Dans `starter/choices.py` : `TECHNIQUE` associe à chacune des 5 situations de `plan_tasks.py` la technique d'affinage adaptée. Tests : `-k technique`.

Pratique, hors test : prenez une fonction dont la consigne est ambiguë (par exemple la normalisation de numéros de téléphone), décrivez-la en prose, notez deux interprétations différentes, puis ajoutez 3 exemples d'entrée et de sortie et constatez la différence. Seconde passe : demandez d'abord à Claude de vous interroger.

## Exercice 5 : Claude Code en CI (60 min)

Dans `starter/ci_review.py` : schéma de sortie, consigne à 3 critères, `build_command`, `parse_result`, `fingerprint`, `only_new`, `run_review`. Tests : `pytest labs/03-claude-code-config/tests/test_ci_review.py`. Écrivez aussi `starter/config/.github/workflows/review.yml` (déclenché sur `pull_request`, permissions minimales, secret `ANTHROPIC_API_KEY` lu depuis les secrets, jamais en clair). Le workflow suppose `ci_review.py` à la racine du dépôt : copiez-le.

Règles vérifiées :
- la sortie JSON est lue par un programme (`structured_output`), jamais à la main ; son absence est une erreur, pas une revue vide ;
- la revue est une session neuve et non conservée (ni `--resume` ni `--continue`) : le relecteur ne voit pas le raisonnement qui a produit le code ;
- 3 critères explicites et une liste de ce qu'il faut ignorer, au lieu de « sois prudent » ;
- outils en lecture seule et budget plafonné ;
- le diff passe par l'entrée standard ;
- seuls les constats nouveaux sont remontés, via une empreinte indépendante du numéro de ligne ;
- les codes de sortie : 0 rien de bloquant, 1 constat nouveau de gravité high, 2 revue inexploitable.

Avec le vrai CLI (identifiants requis, appel facturé) : `python labs/03-claude-code-config/run_ci_review.py --target starter`. Sur le corrigé, une exécution réelle a trouvé l'injection SQL, la signature changée sans mise à jour de l'appelant et un défaut de bornage de la formule de plafond.

Questions à noter :
1. Pourquoi `--bare` pour la CI, et pourquoi faut-il alors une clé API ?
2. Pourquoi l'absence de `structured_output` ne doit-elle jamais être traitée comme « aucun problème » ?
3. Où conserver les empreintes d'une revue à l'autre (commentaire de PR avec marqueur, cache, artefact) ? Le lab ne l'implémente pas.
4. Qu'apporte l'action officielle `anthropics/claude-code-action@v1` par rapport à ce script, et que perd-on en la choisissant ?

## Tout vérifier

```bash
LAB_TARGET=solution pytest labs/03-claude-code-config/tests   # corrigé : tout passe, sans clé API
pytest labs/03-claude-code-config/tests                       # votre starter
```

## Critères de réussite

- Tous les tests passent sur votre `starter/`.
- Vous avez comparé la simulation de chargement à ce que fait Claude Code (`/memory`, lecture d'un fichier de `src/api`) et noté les écarts.
- La revue CI tourne avec le vrai CLI et sa sortie est lue par le programme.
- Vous expliquez la différence entre `allowed-tools` et `disallowed-tools`, et entre un CLAUDE.md et un hook.

## Pièges fréquents

- CLAUDE.md fourre-tout de plusieurs centaines de lignes, ou règle propre à un dossier posée à la racine.
- Frontmatter `paths` mal formé : la règle se charge partout sans erreur visible.
- Description de skill vague : il ne se déclenche jamais ou trop souvent.
- Croire qu'`allowed-tools` interdit les autres outils.
- `context: fork` sur un skill qui ne contient que des consignes générales : le sous-agent n'a pas de tâche.
- Faire relire du code par la session qui l'a écrit.
- Traiter une sortie absente ou une erreur d'authentification comme une revue sans problème.
- Un secret en clair dans un workflow.

## Limites connues

- Le simulateur applique les règles documentées ; ce n'est pas le code de Claude Code. Le comportement réel dépend de la version : constatez-le avec `/memory` et par l'usage.
- Les tests hors ligne ne mesurent pas la qualité de vos consignes (skill, critères de revue) : seule une exécution réelle le fait.
- Le workflow GitHub Actions n'a pas été exécuté sur GitHub : seule sa forme est testée.
- Les empreintes de constats ne sont pas persistées entre deux exécutions.
- Plan contre exécution directe et choix de la technique d'affinage reposent sur le guide d'examen lu via un résumé automatique : relisez le PDF.

## Références à ouvrir

Documentation Claude Code (« How Claude remembers your project », skills, mode non interactif, GitHub Actions), cours Anthropic Academy « Claude Code in Action » et « Introduction to Agent Skills ».
