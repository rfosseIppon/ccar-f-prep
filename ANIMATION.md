# Guide d'animation des ateliers

Pour la personne qui anime un atelier collectif de 2 heures (voir `PLAN.md`). Le format vise à faire expliquer des choix de conception : l'examen évalue la décision entre options plausibles, pas la mémoire d'une syntaxe.

## Rôle de l'animateur

- Il n'est pas l'expert du domaine : il tient le temps, fait justifier les choix et note les désaccords.
- Il ne donne pas la solution en premier. Si le groupe est bloqué, il pose la question qui sépare les deux options (« que se passe-t-il quand le modèle se trompe ? »).
- Il distingue ce qui est vérifié (testé, relu dans la documentation) de ce qui est une opinion, et le dit à voix haute.

Rotation proposée pour 4 personnes et 5 domaines : une personne par domaine, et la quatrième personne prend deux domaines légers (par exemple D2 et D5 en S2). Écrivez la répartition au kickoff.

## Avant l'atelier (45 minutes pour l'animateur)

1. Faire le lab du domaine jusqu'au bout, puis lire `solution/` et le `README.md` du lab (section « Pièges fréquents »).
2. Relire les task statements du domaine dans `EXAM-MAP.md`, et les pages de documentation citées par les corrections du quiz.
3. Passer les questions du quiz du domaine, lire leurs explications, et noter toute question mal formulée ou qui vous semble fausse. Le quiz a un seul auteur : chaque animateur est le relecteur de son domaine. Les corrections vont dans `quiz-data.js` du dépôt de la page, ou dans un ticket.
4. Choisir trois questions de discussion : une sur un choix de conception du lab, une sur un piège, une qui oppose deux options valables (voir `scenarios/README.md`).
5. Demander aux participants d'apporter, pour chaque exercice, leur choix et l'alternative écartée (une phrase chacun).

## Déroulé type (120 minutes)

| Durée | Étape | Consigne |
|---|---|---|
| 15 min | Rappel | L'animateur présente les task statements du domaine et les 3 idées à retenir. Pas de diaporama : le tableau de `EXAM-MAP.md` suffit |
| 60 min | Revue croisée | Chaque personne présente un choix de conception et l'alternative écartée (10 minutes chacun, 5 de questions). Les autres cherchent le cas où l'alternative aurait été meilleure |
| 30 min | Scénario | Scénario du guide concerné : réponses individuelles par écrit (5 minutes), puis discussion. L'artefact d'étude fournit un scénario à décision pour le domaine 1 |
| 15 min | Pièges | Chacun donne un piège rencontré. L'animateur l'ajoute au `README.md` du lab (section « Pièges fréquents ») |

Conseil : si la revue croisée déborde, couper le scénario plutôt que les pièges. Les pièges rencontrés servent aux personnes qui reprendront le dépôt.

## Contenu par semaine

| Semaine | Question à poser en premier | Exercice à demander en démonstration |
|---|---|---|
| S1, D1 | « Quelle règle de ce lab ne doit jamais dépendre du prompt, et pourquoi ? » | La boucle (`stop_reason`), le plafond financier en code, la liste d'outils d'un sous-agent |
| S2, D2 et D5 | « Que renvoie votre outil quand le client demande la commande d'un autre ? » puis « Qu'est-ce qui survit à une compaction ? » | Une description d'outil réécrite, un message d'erreur structuré, le bloc de faits du dossier client |
| S3, D3 et D4 | « Où mettez-vous cette règle : CLAUDE.md, règle par chemin ou skill ? » puis « Quand un schéma valide produit-il une donnée fausse ? » | Une règle avec `paths`, la configuration CI, un prompt de revue avec critères explicites |
| S4 | Examen blanc, puis « Où avez-vous hésité, et qu'est-ce qui vous a fait trancher ? » | Voir ci-dessous |

## Conduire l'examen blanc de S4

- Les conditions de l'examen réel : livre fermé, pas de recherche ni d'outil de traduction, 60 questions en 120 minutes. Le mode « Examen blanc » de la page d'étude applique le tirage par pondération et le minuteur.
- Le score brut n'est pas la note officielle : celle-ci est échelonnée de 100 à 1 000 avec un seuil de 720, et la conversion n'est pas publique. Le seuil de 80 % de la page sert de marge de sécurité.
- Le guide d'examen contient des questions d'exemple : les passer en complément, en conditions réelles aussi. Ne cherchez ni ne partagez de questions réelles d'examen.
- Correction collective : on ne relit que les questions manquées par au moins une personne, en demandant d'abord à celle qui a juste d'expliquer pourquoi les autres options sont fausses.
- L'examen est en anglais : faites lire les énoncés en anglais pendant la correction, avec le glossaire (`GLOSSAIRE.md`).

## Quand quelqu'un est bloqué

1. Lire le message du test qui échoue : les tests disent ce qu'ils attendent.
2. Relire le `README.md` du lab, section de l'exercice, puis la documentation citée.
3. Après deux essais sérieux, comparer avec `solution/` sur la partie bloquante seulement, puis refaire l'exercice sans regarder.
4. Si le blocage dépasse 30 minutes sur une seule question, passer en binôme : celui qui comprend explique sans taper.
5. Si le test ou la consigne semble faux, ouvrir un ticket : les labs ont un seul auteur.

## Signes qu'un domaine est maîtrisé

- La personne explique en deux minutes un choix de conception et l'option écartée, sans notes.
- Elle reconnaît le piège dans une question à options plausibles, avant de lire les réponses.
- La grille d'auto-évaluation (`checklists/auto-evaluation.md`) est à 3 sur 3 pour la moitié au moins des task statements du domaine, avec les cases manquantes datées.

## Ce que cette préparation ne garantit pas

Aucun cours, lab ou quiz de ce dépôt n'est un contenu d'examen. Les tests des labs tournent avec des faux clients, à l'exception d'une revue CI exécutée une fois avec le vrai CLI (lab 03) : l'exécution réelle avec un modèle et une clé API est à faire par l'équipe (voir la section « Limites connues » des `README.md` des labs 02 à 05). La réussite à l'examen dépend aussi de l'anglais technique et de la gestion du temps.
