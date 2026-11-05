# Plan sur 4 semaines

Hypothèses : 4 personnes, bon niveau d'usage de Claude, échéance fin novembre 2026. La charge réelle des labs, des quiz et des ateliers est d'environ 36 heures par personne, soit 9 heures par semaine en moyenne et jusqu'à 12 heures en S3 (voir « Charge de travail » plus bas). Une charge de 5 heures par semaine ne suffit pas pour tenir ce calendrier.

## Calendrier proposé

| Semaine | Dates | Domaines | Lab | Atelier collectif |
|---|---|---|---|---|
| S0 | 28 au 30 oct | Cadrage | `00-setup` | Kickoff de 1 h : accès à l'examen, lecture du guide officiel, répartition des animations |
| S1 | 2 au 6 nov | D1 Architecture agentique et orchestration (27 %) | `01-agentic-orchestration` | Revue des exercices, scénarios 1 et 3 |
| S2 | 9 au 13 nov | D2 Outils et MCP (18 %), D5 Contexte et fiabilité (15 %) | `02-tools-mcp`, `05-context-reliability` | Revue des descriptions d'outils, scénario sur les pannes partielles |
| S3 | 16 au 20 nov | D3 Claude Code (20 %), D4 Prompt et sorties structurées (20 %) | `03-claude-code-config`, `04-prompt-structured-output` | Revue des configurations, scénarios 2, 5 et 6 |
| S4 | 23 au 27 nov | Révision | Points faibles du suivi | Examen blanc interne en conditions (60 questions, 120 min), puis session de correction |

## Charge de travail par personne

Durées des labs : celles de leur `README.md`. Quiz : environ 2 minutes par question, soit 0,5 h par quiz de domaine et 1,5 h pour la banque complète. Hors cours Anthropic Academy, dont aucune durée n'est publiée sur les pages de présentation.

| Semaine | Contenu | Heures |
|---|---|---|
| S0 | Kickoff 1 h, installation 0,5 h | 1,5 |
| S1 | Lab 01 (3,5 h), quiz D1 (0,5 h), atelier (2 h) | 6 |
| S2 | Labs 02 (4 h) et 05 (3,5 h), quiz D2 et D5 (1 h), atelier (2 h) | 10,5 |
| S3 | Labs 03 (4 h) et 04 (4,75 h), quiz D3 et D4 (1 h), atelier (2 h) | 11,75 |
| S4 | Banque complète (1,5 h), examen blanc (2 h), correction (2 h), points faibles (1 h) | 6,5 |
| Total | | environ 36 |

Décision à prendre avant le kickoff, parce que 5 heures par semaine ne suffisent pas :

1. Réserver 9 à 12 heures par semaine pendant 4 semaines (le calendrier ci-dessus tient).
2. Étaler sur 6 semaines à 6 heures par semaine, et décaler la fenêtre d'examen en conséquence.
3. Garder 4 semaines à 5 heures et accepter de ne faire que les exercices des task statements pondérés le plus lourd (D1, D3, D4), avec une préparation moins sûre sur D2 et D5.

Lisser sans rien décaler : faire le lab 05 en S1 pour ceux qui ont fini le lab 01 tôt (il suppose le lab 01), et commencer le lab 04 en S2.

Passage de l'examen : fenêtre du 26 au 30 nov à confirmer selon les disponibilités et l'accès partenaire (voir la section suivante). Si l'échéance est plus proche, démarrer la S1 dès cette semaine et regrouper D3 et D4 en une demi-semaine.

## L'examen : ce que disent les sources officielles

Relevé le 29 octobre 2026 sur la page de la certification, la FAQ, la page d'éligibilité et le guide d'examen version 1.0 (juillet 2026, via un résumé automatique du PDF). À relire avant de réserver.

| Sujet | Information | Source |
|---|---|---|
| Format | 60 questions à choix simple ou multiple, 120 minutes, 4 scénarios tirés parmi 6, score de 100 à 1 000, seuil 720, pas de pénalité mentionnée | Guide |
| Langues | Anglais et japonais seulement. Pas de traduction automatique pendant l'épreuve | FAQ |
| Condition | Livre fermé, surveillance Pearson VUE (en ligne ou en centre), pièce d'identité, 18 ans minimum | FAQ |
| Accès | Personnes d'organisations du Claude Partner Network, avec une adresse professionnelle sur un domaine déclaré. Ajout d'un domaine : 7 à 10 jours. Sinon : inscription impossible | Page d'éligibilité, FAQ |
| Prix | 125 USD. Remise de 50 % pour les partenaires Select, Preferred et Global Premier (non vérifié pour Ippon) | FAQ |
| Tentatives | 4 par période de 12 mois, attentes de 14, 30 et 90 jours après les échecs | FAQ |
| Validité | Certification : 12 mois | Guide, FAQ |
| Annulation | Pas de report ni d'annulation à moins de 48 heures | FAQ |

Un blog tiers annonçait 99 USD ou 49,50 USD et quatre cours obligatoires comme prérequis : la page officielle indique 125 USD et ne mentionne aucun prérequis de cours.

Décision à prendre avant le kickoff : Ippon est-il dans le Claude Partner Network, et à quel niveau ? Les domaines de messagerie des quatre personnes sont-ils déclarés ? Contacts cités par la FAQ : partner-support@anthropic.com (accès partenaire), certifications-support@anthropic.com (remboursements).

La langue de l'examen change la préparation : les labs et le quiz sont en français, l'examen est en anglais. Apprendre le vocabulaire anglais (stop_reason, tool_use, hooks, subagents, scratchpad).

## Labs, use cases et cours Anthropic Academy

Les cours sont gratuits, en anglais, sur anthropic.skilljar.com (compte Skilljar requis). Leurs programmes ont été relevés sur les pages de présentation le 29 octobre 2026 ; aucune durée n'y figure. Le rapprochement avec les labs est une proposition de l'équipe : aucune correspondance officielle avec l'examen n'a été relevée.

| Lab | Use case (fictif) | Cours principal | Compléments | Semaine |
|---|---|---|---|---|
| 00 Environnement | Poste prêt pour une mission | Claude Code 101 (introduction) | Claude Platform 101 (facultatif, programme non lu) | S0 |
| 01 Orchestration | Agent de support e-commerce, dossier d'avant-vente multi-agents | Introduction to subagents | Building with the Claude API, blocs 5 et 10 | S1 |
| 02 Outils et MCP | Outils d'accès aux commandes et serveur MCP | Introduction to Model Context Protocol | MCP: Advanced Topics ; API, blocs 5 et 8 | S2 |
| 03 Claude Code | Quatre consultants sur un dépôt, revue de PR en CI | Claude Code in Action | Introduction to agent skills ; Claude Code 101 en rattrapage | S3 |
| 04 Prompt et sorties structurées | Extraction de factures fournisseurs, revue de code | Building with the Claude API, blocs 2 à 5 | Aucun autre cours de la liste | S3 |
| 05 Contexte et fiabilité | Dossier client sur 15 tours, panne partielle, gros dépôt | Aucun cours dédié | Claude Code in Action (modules 1 et 4) ; Introduction to subagents ; API, blocs 7 et 10 | S2 |

Liens : Claude Code 101 (anthropic.skilljar.com/claude-code-101), Claude Platform 101 (claude-platform-101), Building with the Claude API (claude-with-the-anthropic-api), Introduction to Model Context Protocol (introduction-to-model-context-protocol), Model Context Protocol: Advanced Topics (model-context-protocol-advanced-topics), Introduction to subagents (introduction-to-subagents), Introduction to agent skills (introduction-to-agent-skills), Claude Code in Action (claude-code-in-action).

Les trous de couverture sont listés dans le README de chaque lab (section « Cours Anthropic Academy associé ») : lots (batches), erreurs structurées d'outils, règles par chemin, escalade et pannes partielles ne figurent pas aux programmes lus. Les compléter avec la documentation officielle.

## Format d'un atelier (2 h)

1. 15 min : rappel des points clés du domaine par la personne qui anime.
2. 60 min : revue croisée des labs. Chacun présente un choix de conception et l'alternative écartée.
3. 30 min : scénario à décision (artefact d'étude), réponses individuelles puis discussion.
4. 15 min : liste des pièges rencontrés, ajoutée au `README.md` du lab.

Rotation : quatre personnes, cinq domaines. Une personne anime deux domaines (par exemple D2 et D5 en S2).

## Critères de passage (proposition interne)

- Chaque lab terminé avec les critères de réussite validés.
- Au moins 80 % de bonnes réponses au quiz de chaque domaine avant de passer au suivant.
- Banque complète de 72 questions à 80 % ou plus, puis examen blanc en ligne de 60 questions à 80 % ou plus (score brut : il ne se convertit pas en note officielle de 100 à 1 000).
- Examen blanc interne d'équipe avant de réserver : l'examen blanc en ligne de la page, puis les 12 questions d'exemple du guide, à passer en S4. Viser 80 % de bonnes réponses : la note officielle est échelonnée de 100 à 1 000 (seuil de 720) et sa conversion n'est pas publique, donc 80 % sert de marge de sécurité et ne prédit pas le résultat. La page de préparation officielle ne mentionne pas d'examen blanc.

Ces seuils sont une proposition de l'équipe, pas une exigence d'Anthropic.
