# Préparation Claude Certified Architect, Foundations (CCAR-F)

Socle commun d'apprentissage pour préparer l'examen en équipe : labs pratiques, scénarios de discussion, quiz (dans l'artefact d'étude partagé) et planning sur 4 semaines.

## Avant de commencer

- Une page d'étude partagée accompagne ce dépôt : plan, installation pas à pas, quiz de 72 questions (par domaine ou complet, dont 5 à deux bonnes réponses) et examen blanc chronométré de 60 questions en 120 min, scénario à décision et suivi de l'équipe. Lien : à ajouter par la personne qui diffuse le dépôt (la page est privée, il faut la partager avec le niveau Contributeur pour que chacun enregistre sa progression).
- Les caractéristiques de l'examen (60 questions, 120 minutes, seuil 720/1000, 5 domaines pondérés, 30 task statements, 6 scénarios dont 4 tirés au sort) viennent du guide d'examen officiel version 1.0 (juillet 2026), relevées le 29 octobre 2026 à travers un résumé automatique du PDF. Lire le PDF reste la première étape : il fait foi et peut changer sans préavis. La correspondance avec ce dépôt est dans `EXAM-MAP.md`.
- L'examen n'est proposé qu'en anglais et en japonais, sans outil de traduction pendant l'épreuve. Les labs et le quiz sont en français : apprendre le vocabulaire anglais des concepts (stop_reason, tool_use, hooks, subagents).
- Seules les personnes qui travaillent dans une organisation du Claude Partner Network peuvent passer l'examen, avec une adresse professionnelle sur un domaine déclaré. Ippon doit confirmer son statut de partenaire avant de réserver (voir `PLAN.md`).
- Ce repo ne contient aucune question réelle d'examen. N'utilisez pas de banques de questions vendues en ligne.

## Contenu

| Dossier | Rôle |
|---|---|
| `PLAN.md` | Planning de 4 semaines, rituels, critères de passage, faits sur l'examen |
| `EXAM-MAP.md` | Les 30 task statements du guide officiel, avec les labs et le quiz qui les couvrent |
| `labs/00-setup` | Installation et vérification de l'environnement |
| `labs/01-agentic-orchestration` | Domaine 1 (27 %) : boucle agentique, garde-fous, multi-agents. Lab complet avec tests |
| `labs/02-tools-mcp` | Domaine 2 (18 %) : conception d'outils, erreurs structurées, MCP |
| `labs/03-claude-code-config` | Domaine 3 (20 %) : CLAUDE.md, rules, skills, mode headless en CI |
| `labs/04-prompt-structured-output` | Domaine 4 (20 %) : sorties structurées, validation, batch |
| `labs/05-context-reliability` | Domaine 5 (15 %) : gestion du contexte, escalade, pannes partielles |
| `scenarios/` | Les 6 scénarios, avec questions de discussion pour les ateliers |
| `checklists/` | Points logistiques pour le jour de l'examen, et grille d'auto-évaluation des 30 task statements |
| `LIMITES.md` | Ce qui a été vérifié, ce qui ne l'est pas, et les actions pour l'équipe |
| `ANIMATION.md` | Guide pour animer les ateliers de 2 heures et l'examen blanc |
| `GLOSSAIRE.md` | Termes anglais de l'examen avec leur sens et le lab où les travailler |
| `tools/`, `.github/workflows/` | Contrôles pour les mainteneurs : tests des corrigés, starters toujours incomplets |

Chaque README de lab contient un use case (cas fictif de type mission Ippon) et le cours Anthropic Academy associé. La table de correspondance est dans `PLAN.md`.

État d'avancement : les labs 01 à 05 ont chacun un code de départ (`starter/`), un corrigé (`solution/`) et des tests qui tournent sans clé API, avec des faux clients. Les exercices qui appellent un vrai modèle sont décrits dans les README, mais leur exécution réelle reste à faire par l'équipe (voir « Limites connues » dans les labs 02 à 05). Le lab 00 vérifie l'environnement.

## Fonctionnement d'un lab

1. Lire le `README.md` du lab (objectifs, exercices, critères de réussite).
2. Travailler dans `starter/`. Les tests indiquent ce qui manque.
3. Comparer avec `solution/` seulement après avoir tenté l'exercice.
4. Noter vos choix de conception et vos doutes : ils alimentent l'atelier collectif.

## Prérequis

- Python 3.10 ou plus
- Une clé API Anthropic par personne pour les exercices qui appellent le modèle (les tests du lab 01 tournent sans clé)
- Claude Code installé pour les labs 03 et 05

Installation détaillée, Windows compris : `labs/00-setup/README.md`.

## Principe de travail

L'examen porte sur des décisions de conception (quand déléguer, quand escalader, comment décrire un outil, que mettre dans un CLAUDE.md). Pour chaque exercice, écrivez la raison de votre choix et l'alternative écartée. C'est la compétence évaluée, pas la mémorisation d'une syntaxe.
