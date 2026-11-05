# Limites connues et actions pour l'équipe

État au 29 octobre 2026. Ce fichier dit ce qui a été vérifié, comment, et ce qui reste à faire par des personnes. Aucun point de la colonne « Non vérifié » ne doit être présenté comme acquis.

## Ce qui a été vérifié

| Sujet | Vérification | Preuve |
|---|---|---|
| Labs 01 à 05 | 289 tests sur les corrigés, sans clé API, avec des faux clients ; mutations pour les labs 05 et le quiz | `LAB_TARGET=solution pytest labs` |
| Starters | Seuls 38 tests d'intégrité passent, tous les autres échouent | `python tools/check_starters.py` |
| Python | Corrigés exécutés en venv neuf sous Python 3.10 et 3.13 | commandes du workflow `.github/workflows/tests.yml` |
| Correspondance avec le guide | 30 task statements sur 30 ont un exercice et au moins une question de quiz | `EXAM-MAP.md` |
| Quiz | 72 questions valides (bornes, doublons, liens de documentation, répartition par domaine suffisante pour tirer 60 questions) | `check_quiz.js` dans le dépôt de la page |
| Page d'étude | 113 vérifications automatisées en navigateur (choix multiples, examen, minuteur, sauvegarde), axe-core sans violation, pas de défilement horizontal à 320 px, parcours clavier d'une question | scripts de test de la page |

## Non vérifié

| Sujet | Pourquoi | Que faire |
|---|---|---|
| Le guide d'examen lui-même | Les 30 task statements, les pondérations et les scénarios viennent d'un résumé automatique du PDF, pas d'une lecture du PDF | Lire le PDF du guide v1.0 et corriger `EXAM-MAP.md` |
| Questions du quiz | Un seul auteur, aucune relecture humaine ; questions originales, pas des questions d'examen. Les questions à deux réponses comptent tout ou rien | Chaque animateur relit les questions de son domaine (voir `ANIMATION.md`) |
| Score de l'examen blanc | Score brut sur 60. La note officielle va de 100 à 1 000 (seuil 720), conversion non publique | Ne pas en déduire une note ; viser 80 % comme marge |
| Exercices avec un vrai modèle | Les tests utilisent des faux clients. Une revue CI a été exécutée une fois avec le vrai CLI (version 2.1.312). Sélection d'outils, `tool_choice`, mesure de faux positifs, API Batches : jamais appelés pour de vrai | Une personne par lab exécute les scripts `run_*.py` avec une clé API et note l'écart |
| Coût d'exécution | Clés API et budget non attribués | Décider avant le kickoff (voir `PLAN.md`) |
| Workflow GitHub Actions du dépôt | Ses commandes ont tourné en local, pas sur GitHub | Ouvrir une pull request et vérifier les deux jobs |
| Workflow de revue du lab 03 | Contrôlé par des tests de structure, jamais exécuté sur GitHub | L'exécuter sur un dépôt d'essai |
| Windows | Rien exécuté sous Windows ; seule une locale non UTF-8 a été émulée | Une personne sous Windows suit `labs/00-setup/README.md` et note les écarts |
| Accessibilité de la page | axe-core, parcours clavier et reflow vérifiés ; pas de test avec un lecteur d'écran, pas d'audit RGAA. La page n'est pas « conforme » à un référentiel | Tester avec NVDA ou VoiceOver si une personne de l'équipe en dépend. Le minuteur de l'examen blanc reproduit une limite de temps réelle |
| Documentation Anthropic | Les faits techniques datent du 29 octobre 2026 ; Claude Code évolue vite (noms d'options, outil de délégation) | Contrôler avec `claude --help` et la documentation avant chaque lab |
| Cours Anthropic Academy | Programmes lus sur les pages de présentation, contenus non suivis ; le rapprochement avec les labs est une proposition de l'équipe | Noter les écarts après avoir suivi les cours |
| Accès à l'examen | Statut de partenaire d'Ippon dans le Claude Partner Network, domaines de messagerie déclarés, prix ou remise : non confirmés | Confirmer auprès du contact partenaire avant de réserver (voir `PLAN.md`) |

## Ce que ce dépôt ne fait pas

Il ne contient aucune question réelle d'examen et ne garantit pas la réussite. Il prépare à des décisions de conception ; l'anglais technique et la gestion du temps restent à travailler (voir `GLOSSAIRE.md`).
