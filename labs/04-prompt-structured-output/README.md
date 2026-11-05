# Lab 04 : prompt engineering et sorties structurées (domaine 4, 20 %)

Durée : 4 heures 45 (dont 1 heure pour le contrôle de qualité de l'exercice 7, qui couvre aussi la task statement 5.5 du domaine 5). Scénarios concernés : 6 (extraction de données structurées) et 5 (Claude Code en CI/CD).

Statut : corpus, code de départ (`starter/`), corrigé (`solution/`) et tests hors ligne fournis. Les scripts `run_corpus.py` et `run_review.py` appellent un vrai modèle et demandent une clé API : ils n'ont pas été exécutés à la préparation du dépôt.

## Use case

**Factures fournisseurs d'un client, de la boîte mail à la comptabilité** (cas fictif). Le client reçoit chaque nuit des centaines de documents hétérogènes : PDF de factures, e-mails, comptes rendus. Il veut des données structurées, sans valeur inventée quand un champ manque (numéro de TVA absent, date illisible), et un traitement par lot pour la remontée de nuit. Une valeur inventée coûte plus cher qu'un champ vide, car personne ne la contrôle ensuite.

Mission : extraction par schéma, champs nullables, validation avec règles métier et relance limitée, traitement par lots, contrôle de qualité par segment et relecture humaine ciblée. Exercices 4 et 6 : second cas, la revue de code automatique d'une PR, où l'enjeu est le nombre de faux positifs.

Livrable : tableau d'exactitude avant/après chaque amélioration (sur le corpus fourni de 10 documents avec vérité terrain), aucune valeur inventée sur les 3 documents à champ absent, rapprochement des résultats du lot par `custom_id`, exactitude par segment de documents et seuils de relecture humaine par champ, revue de PR en deux passes.

Scénarios d'examen concernés : 6 (extraction de données structurées) et 5 (Claude Code en CI/CD).

## Cours Anthropic Academy associé

- **Building with the Claude API** (https://anthropic.skilljar.com/claude-with-the-anthropic-api) : bloc 2 (prompts système, données structurées), bloc 3 (évaluation de prompts : jeux de test, notation par code, utile pour mesurer l'exactitude), bloc 4 (clarté, balises XML, exemples few-shot), bloc 5 (schémas d'outils). Seul cours de la liste qui couvre ce domaine.

Non couvert d'après le programme lu : traitement par lots (la page le cite dans sa description, sans leçon dédiée), champs nullables, boucle de validation et relance avec le message d'erreur. À travailler avec la documentation de l'API Messages (utilisation d'outils, sorties structurées) et de l'API Message Batches.

Quand : semaine 3.

Cours en anglais, gratuits, compte Skilljar requis. Les pages consultées le 29 octobre 2026 n'indiquent pas de durée. Le rapprochement avec le lab est une proposition de l'équipe, établie sur les pages de présentation des cours : aucune correspondance officielle avec l'examen n'a été relevée.

## Objectifs

Task statements du guide d'examen : 4.1 à 4.6, plus 5.5 (voir `EXAM-MAP.md`).

- Obtenir un JSON conforme à un schéma via l'utilisation d'outil (`tool_use`) et `tool_choice` (4.3).
- Prévoir des champs nullables, `other` + détail et `unclear` pour éviter que le modèle invente une valeur absente (4.3).
- Valider la sortie (schéma, règles métier, cohérence calculée contre déclarée) et relancer avec le message d'erreur, seulement quand la relance peut aider (4.4).
- Rédiger des critères explicites plutôt que des consignes vagues, et ajouter 2 à 4 exemples pour les cas ambigus (4.1, 4.2).
- Traiter un volume avec l'API Message Batches (4.5).
- Relire du code en plusieurs passes indépendantes (4.6).
- Mesurer l'exactitude par segment et fixer des seuils de relecture humaine par champ (5.5).

## Point d'attention : `tool_choice` selon le modèle

Le guide d'examen décrit `tool_choice` à trois valeurs : `auto`, `any` et un outil précis (forcé). La documentation de l'API indique que, sur les modèles récents utilisés ici (Sonnet 5.5, Opus 5.5, Fable 5.1, Mythos 5.1), `any` et le choix d'un outil précis renvoient une erreur 400 : il faut `auto`, avec des sorties structurées ou l'utilisation d'outil stricte (`strict`). Cette indication vient d'une seule page de documentation et n'a pas été recoupée ni testée par l'équipe : vérifiez-la sur la page « tool use » de la documentation avant l'exercice 1.

Le code fournit donc les deux modes : `build_request(..., mode="auto")` par défaut, `mode="forced"` pour les modèles qui l'acceptent. À l'examen, sachez ce que fait chaque valeur, car les questions suivent le guide.

## Le corpus fourni (`corpus/`)

10 documents courts et bruités (`doc_01.txt` à `doc_10.txt`) et leur vérité terrain (`truth.json`). Ils ont été écrits pour le lab ; aucune donnée réelle.

| Segment | Documents | Particularité |
|---|---|---|
| `pdf_text` | 01, 02, 03, 05, 10 | factures propres ; 05 : date ambiguë (04/05/2026), 10 : devise hors liste (CHF) |
| `email` | 04, 06, 09 | 04 : pas de numéro de TVA ; 06 : conditions de paiement ambiguës ; 09 : pas de numéro de facture |
| `scan_noisy` | 07, 08 | 07 : pas de date ; 08 : total déclaré (980) différent de la somme des lignes (950) |

Chaque document absent ou incohérent est un piège : une extraction correcte laisse `null` et signale, elle n'invente pas. `scoring.py` (fourni) compare champ par champ, en ignorant casse, accents et ponctuation.

Un second corpus, `corpus/review_pr.json`, contient une PR de 3 fichiers pour les exercices 4 et 6 : une injection SQL et une incohérence d'arguments entre deux fichiers sont attendues ; une remarque de style est à ignorer.

## Fichiers à compléter

Chaque fichier de `starter/` contient des fonctions à écrire, avec leur docstring pour consigne. `solution/` contient le corrigé : ne l'ouvrez qu'après avoir essayé.

| Fichier | Exercices |
|---|---|
| `starter/extract.py` | 1, 2, 3 |
| `starter/review.py` | 4, 6 |
| `starter/batch.py` | 5 |
| `starter/quality.py` | 7 |

## Exercice 1 : extraction par schéma (45 min)

Dans `starter/extract.py`, écrivez `INVOICE_TOOL` (schéma d'entrée), `build_request` et `call_extraction`. Tests : `pytest labs/04-prompt-structured-output/tests/test_extract.py -k "request or call or forced or strict or unknown"`.

À savoir justifier : pourquoi `auto` plutôt que forcé sur les modèles récents, ce que change `strict`, pourquoi une sortie JSON valide au sens du schéma ne garantit pas une valeur exacte.

## Exercice 2 : nullables et valeurs inventées (30 min)

Toujours dans `INVOICE_TOOL` : `invoice_number`, `invoice_date`, `vat_number` et `stated_total` acceptent `null` et ne sont pas obligatoires ; `currency` et `payment_terms` ont des valeurs `other` et `unclear` avec un champ de détail ; aucun champ inconnu n'est accepté. Tests : `-k "schema or enums or nullable or required"`.

Avec une clé API, comparez : rendez les quatre champs obligatoires, lancez `run_corpus.py`, lisez la ligne « Valeurs inventées », puis rétablissez les `null`.

## Exercice 3 : validation et nouvelle tentative (45 min)

Écrivez `validate_extraction` (format de date, plausibilité, somme des lignes, quantité fois prix unitaire), `enrich` (total calculé, drapeau de conflit) et `extract_with_retry`. Règles testées :

- la relance renvoie le document, l'extraction précédente et l'erreur précise ;
- 2 relances au plus ;
- une information absente du document ne déclenche pas de relance : elle part en revue humaine ;
- si la relance renvoie les mêmes données, on s'arrête ;
- le motif de chaque défaut (`detected_pattern`) est conservé pour analyser les erreurs récurrentes.

Tests : `pytest labs/04-prompt-structured-output/tests/test_extract.py`.

## Exercice 4 : critères explicites et exemples (30 min)

Dans `starter/review.py`, écrivez `REVIEW_PROMPT` : catégories à signaler (bug, security), liste de ce qu'il faut ignorer (style), trois niveaux de gravité avec un exemple de code chacun, 2 à 4 exemples (`<example>` avec `<why>`), réponse vide autorisée. Écrivez ensuite `review_file`. Tests : `pytest labs/04-prompt-structured-output/tests/test_review.py -k "test_prompt or test_review_file"`.

Les tests sur le texte de la consigne sont des garde-fous grossiers. Pour mesurer, lancez `run_review.py` avec une consigne vague (« signale les problèmes importants »), puis avec la vôtre, et comparez précision et faux positifs.

## Exercice 5 : traitement par lots (30 min)

Dans `starter/batch.py` : `build_batch_requests` (un `custom_id` par document, au format accepté), `submit_batch`, `reconcile` (rapprochement par `custom_id`, quel que soit l'ordre ; catégories réussi, en erreur, expiré, annulé, mal formé, manquant, inconnu), `retry_documents` (on ne relance que les échecs, les documents trop longs sont découpés en `__partN`) et `submission_window_hours` (fréquence de soumission pour tenir un délai). Tests : `pytest labs/04-prompt-structured-output/tests/test_batch.py`.

Questions à noter :
1. Quels cas d'usage d'Ippon se prêtent au lot (remontée de nuit, rétro-migration), lesquels exigent une réponse immédiate (agent de support, bloc de validation avant fusion) ?
2. Pourquoi un lot ne convient-il pas à une boucle agentique avec outils ?
3. Pourquoi un délai de 30 h se tient-il avec une soumission toutes les 6 h au plus ?

## Exercice 6 : revue en plusieurs passes (45 min)

Écrivez `review_in_passes` : une passe locale par fichier, dans une conversation neuve qui ne voit que le diff de ce fichier, puis une passe d'intégration qui reçoit tous les fichiers et les constats locaux pour chercher les problèmes entre fichiers. Dédoublonnez, triez par gravité puis confiance, et envoyez en revue humaine les constats sous le seuil de confiance. Tests : `pytest labs/04-prompt-structured-output/tests/test_review.py`.

Pourquoi une passe unique sur 3 fichiers manque-t-elle le défaut inter-fichiers ? Pourquoi la relecture par l'instance qui a écrit le code est-elle moins fiable qu'une instance indépendante ?

## Exercice 7 : qualité et relecture humaine (1 h, domaine 5.5)

Dans `starter/quality.py` :

- `accuracy_by_segment` et `weak_segments` : une exactitude globale de 97 % peut cacher un segment à 70 %. Les tests le reproduisent ;
- `stratified_sample` : échantillon reproductible par segment pour mesurer en continu ;
- `calibrate_thresholds` : seuil de confiance par champ, calculé sur des valeurs étiquetées (précision visée 95 %, au moins 3 valeurs, sinon le champ passe toujours en revue) ;
- `route_for_review` : quels champs partent en relecture ;
- `prioritize_for_capacity` : quand la capacité de relecture est limitée, les cas les plus incertains d'abord.

Tests : `pytest labs/04-prompt-structured-output/tests/test_quality.py`. Question : pourquoi la confiance déclarée par le modèle ne vaut-elle rien tant qu'on ne l'a pas calibrée sur des données étiquetées ?

## Tout vérifier

```bash
LAB_TARGET=solution pytest labs/04-prompt-structured-output/tests   # corrigé : tout passe, sans clé API
pytest labs/04-prompt-structured-output/tests                      # votre starter
```

`test_pipeline.py` relie les exercices : un faux modèle qui lit la vérité terrain doit obtenir 100 % d'exactitude, aucune valeur inventée, et seuls les documents 07, 08 et 09 partent en relecture. Un modèle qui invente un numéro de TVA doit être pris en défaut.

Avec une clé API : `python labs/04-prompt-structured-output/run_corpus.py --target starter` (options `--mode forced`, `--strict`) et `python labs/04-prompt-structured-output/run_review.py --target starter`. Ces appels sont facturés par Anthropic.

## Critères de réussite

- Tous les tests passent sur votre `starter/`.
- Exactitude mesurée avant et après chaque amélioration, dans un tableau (vrai modèle).
- Aucune valeur inventée sur les 3 documents à champ absent (04, 07, 09).
- Le rapprochement par `custom_id` ne dépend pas de l'ordre de retour.
- Vous expliquez pourquoi on ne relance pas une extraction quand l'information est absente du document.

## Pièges fréquents

- Tous les champs obligatoires : le modèle invente pour satisfaire le schéma.
- Nouvelle tentative sans message d'erreur, ou sans le document et l'extraction précédente : le modèle répète la même sortie.
- Relancer une extraction dont l'information manque : coût inutile, et risque d'invention.
- « Sois précis » ou « sois prudent » à la place de critères observables.
- Supposer que l'ordre des résultats d'un lot suit l'ordre des requêtes.
- Juger la qualité sur l'exactitude globale au lieu de l'exactitude par segment.
- Faire relire du code par l'instance qui l'a écrit.

## Limites connues

- Les corpus sont synthétiques : l'exactitude mesurée dessus ne se transpose pas à un cas client.
- Le comportement réel du modèle (exactitude, relances utiles, faux positifs) n'a pas été mesuré à la préparation : seuls les tests hors ligne ont été exécutés.
- Les restrictions exactes des schémas en mode `strict` n'ont pas été vérifiées : consultez la page « Structured outputs » de la documentation.

## Références à ouvrir

Documentation de l'API Messages (utilisation d'outils, sorties structurées), de l'API Message Batches, et page « tool use » pour les valeurs de `tool_choice` par modèle.
