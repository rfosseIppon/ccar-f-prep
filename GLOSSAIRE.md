# Glossaire anglais et français

L'examen est en anglais ou en japonais, sans outil de traduction. Ce glossaire donne le terme anglais à reconnaître, son sens en français et l'endroit où il se travaille. Les noms de champs, d'options et d'outils sont à retenir tels quels : ce sont eux qui apparaissent dans les énoncés.

Les termes ont été relevés dans la documentation d'Anthropic consultée le 29 octobre 2026 et dans le résumé du guide d'examen. Vérifiez les noms d'options sur votre version de Claude Code (`claude --help`).

## Domaine 1 : agents et orchestration

| Terme | Sens | Où le travailler |
|---|---|---|
| agentic loop | Boucle où le modèle appelle des outils, reçoit les résultats, puis décide de continuer ou de s'arrêter | Lab 01, ex. 1 |
| `stop_reason` | Raison pour laquelle le modèle s'est arrêté : `end_turn` (fini), `tool_use` (veut appeler un outil), `max_tokens` (réponse coupée), `stop_sequence`, `pause_turn`, `refusal`, `model_context_window_exceeded` | Lab 01, ex. 1 |
| `tool_use` / `tool_result` | Bloc de demande d'appel d'outil, et bloc de résultat renvoyé, relié par `tool_use_id`. Tous les résultats d'un même tour reviennent dans un seul message utilisateur | Lab 01, ex. 1 |
| iteration cap | Plafond d'itérations : filet de sécurité, jamais la sortie normale de la boucle | Lab 01, ex. 1 |
| coordinator, hub-and-spoke | Un agent central qui délègue à des sous-agents et fait la synthèse : tout passe par lui | Lab 01, ex. 3 |
| subagent | Agent lancé par un autre, avec son propre contexte. Il ne voit pas l'historique du parent : seule la consigne lui parvient | Lab 01, ex. 3 |
| `AgentDefinition`, `allowedTools` | Définition d'un sous-agent (consigne, outils) et liste des outils autorisés | Lab 01, ex. 3 |
| Task tool / Agent tool | Outil de délégation vers un sous-agent. Le nom dépend de la version : vérifiez la vôtre | Lab 01, ex. 3 |
| hook | Code exécuté à un point précis du cycle, avec une garantie que le prompt ne donne pas | Lab 01, ex. 4 |
| `PreToolUse` / `PostToolUse` | Hook avant l'appel (peut le bloquer) et après (peut transformer le résultat avant que le modèle le lise) | Lab 01, ex. 4 |
| prerequisite gate | Règle d'ordre garantie en code : pas d'étape B avant l'étape A | Lab 01, ex. 2 |
| resume / fork a session | Reprendre une session, ou la copier pour essayer une autre piste (`--resume`, `--fork-session`, `/branch`) | Lab 01, ex. 5 |
| task decomposition | Découper une tâche : chaîne fixe (étapes connues) ou adaptative (la suite dépend des découvertes) | Lab 04, ex. 6 ; lab 05, ex. 4 |

## Domaine 2 : outils et MCP

| Terme | Sens | Où le travailler |
|---|---|---|
| tool description | Texte qui dit au modèle quand et pourquoi utiliser l'outil, ce qu'il ne fait pas, et quels outils voisins existent | Lab 02, ex. 1 |
| `input_schema` | Schéma JSON des paramètres d'un outil | Lab 02, ex. 1 |
| MCP server | Serveur qui expose outils, ressources et prompts à un client selon le protocole MCP | Lab 02, ex. 3 |
| `.mcp.json` | Configuration MCP partagée du projet, versionnée. Jamais de secret en clair : utiliser `${VAR}` | Lab 02, ex. 3 |
| transport (stdio, HTTP) | Mode de communication avec le serveur : processus local ou service distant | Lab 02, ex. 3 |
| resource | Contenu en lecture exposé par un serveur MCP, à distinguer d'un outil (qui agit) | Lab 02, ex. 3 |
| `isError` | Drapeau MCP indiquant qu'un résultat d'outil est une erreur | Lab 02, ex. 2 |
| error category, `isRetryable` | Catégorie d'erreur (validation, permission, métier, transitoire) et indication de réessai. Ces champs sont une convention de votre serveur, citée par le guide, que la spécification MCP n'impose pas | Lab 02, ex. 2 ; lab 05, ex. 3 |
| `tool_choice` | Contrôle de l'appel d'outil : `auto`, `any`, `tool` (un outil précis), `none` | Lab 02, ex. 6 |
| built-in tools | Outils intégrés de Claude Code : Read, Write, Edit, Bash, Grep (contenu), Glob (noms de fichiers) | Lab 02, ex. 5 |

## Domaine 3 : Claude Code

| Terme | Sens | Où le travailler |
|---|---|---|
| `CLAUDE.md` | Instructions persistantes. Les fichiers découverts sont concaténés : en cas de contradiction, le résultat est arbitraire | Lab 03, ex. 1 |
| `@import` | Inclusion d'un autre fichier dans un `CLAUDE.md` | Lab 03, ex. 1 |
| `.claude/rules/`, `paths` | Règles chargées pour certains chemins seulement, déclarées dans l'en-tête YAML | Lab 03, ex. 1 |
| skill | Dossier d'instructions chargé à la demande, avec un `SKILL.md` | Lab 03, ex. 2 |
| `allowed-tools` (skill) | Pré-approuve des outils pour le skill : ce n'est pas une restriction | Lab 03, ex. 2 |
| slash command | Commande `/nom` qui lance une consigne réutilisable | Lab 03, ex. 2 |
| plan mode | Claude lit et propose un plan, sans éditer avant votre approbation (`--permission-mode plan`, Maj+Tab) | Lab 03, ex. 3 |
| headless mode, `-p` | Exécution non interactive, pour la CI et les scripts | Lab 03, ex. 5 |
| `--output-format json`, `--json-schema` | Sortie JSON avec métadonnées, et sortie conforme à un schéma (champ `structured_output`) | Lab 03, ex. 5 |
| `--bare` | Démarre sans charger hooks, skills, plugins, serveurs MCP, mémoire ni CLAUDE.md : même résultat sur toutes les machines | Lab 03, ex. 5 |
| `--max-turns` | Limite le nombre de tours d'une exécution | Lab 03, ex. 5 |
| iterative refinement | Affiner par exemples d'entrée et de sortie, tests écrits d'abord, ou questions posées par Claude (interview) | Lab 03, ex. 4 |

## Domaine 4 : prompts et sorties structurées

| Terme | Sens | Où le travailler |
|---|---|---|
| explicit criteria | Critères écrits de ce qu'il faut signaler ou ignorer, avec définition de chaque gravité | Lab 04, ex. 4 |
| false positive | Constat signalé à tort, qui érode la confiance dans les vrais constats | Lab 04, ex. 4 |
| few-shot examples | Exemples d'entrée et de sortie dans le prompt, utiles surtout sur les cas ambigus | Lab 04, ex. 4 |
| structured output | Sortie conforme à un schéma, obtenue par tool use ou par le mode de sortie structurée | Lab 04, ex. 1 et 2 |
| JSON Schema | Langage de description de la forme d'un JSON. Un JSON valide peut rester faux : le schéma ne vérifie pas le sens | Lab 04, ex. 2 |
| validation-retry loop | Valider la sortie, puis relancer avec l'erreur précise, avec un plafond de tentatives | Lab 04, ex. 3 |
| Message Batches API | Traitement asynchrone à moitié prix, résultat en moins de 24 heures : pour le différé, pas pour une étape bloquante | Lab 04, ex. 5 |
| `custom_id` | Identifiant que vous donnez à chaque requête d'un lot, pour relier les résultats (l'ordre n'est pas garanti) | Lab 04, ex. 5 |
| multi-pass review | Revue en passes : fichier par fichier pour le local, puis passe transversale pour la cohérence | Lab 04, ex. 6 |

## Domaine 5 : contexte et fiabilité

| Terme | Sens | Où le travailler |
|---|---|---|
| context window | Ensemble de ce que le modèle voit à un tour. Une grande fenêtre ne dispense pas de choisir ce qu'on y met | Lab 05, ex. 1 |
| compaction | Remplacement d'un long historique par un résumé : ce qui n'est que dans l'historique peut disparaître | Lab 05, ex. 1 |
| lost in the middle | Les informations placées au milieu d'un long contexte sont moins bien exploitées : les constats critiques vont au début | Lab 05, ex. 1 |
| case facts block | Bloc de faits du dossier (identité, montants, dates) tenu hors de l'historique et remis à chaque tour | Lab 05, ex. 1 |
| escalation | Transfert à un humain : demande explicite, règle non couverte, plafond dépassé, échecs répétés | Lab 05, ex. 2 |
| handoff summary | Résumé autonome pour le conseiller : faits, tentatives, raison, suite proposée | Lab 05, ex. 2 |
| partial failure | Une source ou un sous-agent échoue : on continue, et le rapport dit ce qui manque | Lab 05, ex. 3 |
| coverage gap | Lacune de couverture signalée dans le rapport : non couvert, ou à retenter | Lab 05, ex. 3 |
| provenance | Lien entre chaque affirmation, sa source et sa date, conservé jusqu'à la synthèse | Lab 05, ex. 3 |
| scratchpad | Fichier de notes d'exploration qui survit au contexte | Lab 05, ex. 4 |
| stratified sampling | Échantillonnage par strates pour la relecture humaine, avec des seuils de confiance par champ | Lab 04, ex. 7 |
| confidence calibration | Vérifier que la confiance affichée correspond au taux réel de réussite, sur des données étiquetées | Lab 04, ex. 7 |
