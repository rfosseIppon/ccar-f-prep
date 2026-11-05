# Lab 00 : environnement

Durée : 30 minutes, en semaine 0. Cette page reprend la section « Setup » de la page d'étude partagée.

Systèmes pris en charge par Claude Code : macOS 13 ou plus, Windows 10 (1809) ou plus, Ubuntu 20.04 ou plus, Debian 10 ou plus ; 4 Go de RAM au minimum. Les commandes viennent des documentations d'Anthropic (Claude Code, fiche PyPI du SDK). En cas d'erreur à l'installation, la page de dépannage de Claude Code fait foi.

## Use case

Un consultant arrive lundi sur une mission chez un client. Il doit être productif dans la matinée : Claude Code installé et connecté, Python prêt, clé API déclarée, tests lancés. Le lab 00 est la répétition de cette matinée, avec les mêmes pièges (PATH, variables d'environnement, droits sur le poste).

Livrable : la sortie de `check_env.py` sans ligne `MANQUE`, et tous les tests du lab 01 verts sur le corrigé. Aucun scénario d'examen n'est associé à ce lab.

## Cours Anthropic Academy associé

- **Claude Code 101** (https://anthropic.skilljar.com/claude-code-101) : module « Introduction à Claude Code » (fonctionnement, premier prompt, installation). Public annoncé : débutants et ingénieurs qui n'ont pas encore utilisé d'agent de codage. À sauter si Claude Code est déjà installé et utilisé.
- **Claude Platform 101** (https://anthropic.skilljar.com/claude-platform-101), facultatif : premier appel API. Seule la description du catalogue a été lue, pas le programme.

Quand : semaine 0.

Cours en anglais, gratuits, compte Skilljar requis. Les pages consultées le 29 octobre 2026 n'indiquent pas de durée. Le rapprochement avec le lab est une proposition de l'équipe, établie sur les pages de présentation des cours : aucune correspondance officielle avec l'examen n'a été relevée.

## À installer

| Outil | Précisions | Utile pour |
|---|---|---|
| Python | 3.10 ou plus, exigé par le SDK Claude Agent | Tous les labs |
| Git | Version récente. Sous Windows natif, Git for Windows est recommandé par la documentation de Claude Code. WSL n'en a pas besoin pour Claude Code | Dépôt, lab 03 |
| Claude Code | Installeur natif, sans Node.js. Compte Pro, Max, Team, Enterprise ou Console requis : le plan gratuit de claude.ai n'inclut pas Claude Code | Labs 03 et 05, ateliers |
| Clé API Anthropic | Une par personne, créée dans la Console, jamais écrite dans le dépôt | Exercices qui appellent le modèle (les tests du lab 01 tournent sans clé) |
| Node.js | Facultatif : installation de Claude Code via npm (version 22 ou plus) ou MCP Inspector avec `npx` (vérifier la version demandée par l'Inspector) | Lab 02 |
| Compte Anthropic Academy | Gratuit, cours de pré-lecture listés dans `PLAN.md` | Semaines 0 et 1 |

## Pas à pas

### 1. Récupérer le dépôt

macOS, Linux, WSL :

```bash
unzip ccar-f-prep.zip
cd ccar-f-prep
```

Windows (PowerShell) :

```powershell
Expand-Archive ccar-f-prep.zip -DestinationPath .
cd ccar-f-prep
```

Ou cloner le dépôt Git interne une fois qu'il existe (adresse à définir).

### 2. Créer l'environnement Python

macOS, Linux, WSL :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell) :

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell refuse le script d'activation, passer par l'invite CMD et `.venv\Scripts\activate.bat`.

Le paquet `claude-agent-sdk` embarque son propre Claude Code, mais les labs 03 et 05 utilisent la commande `claude` : l'étape suivante reste nécessaire.

### 3. Installer et connecter Claude Code

macOS, Linux, WSL :

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows (PowerShell) :

```powershell
irm https://claude.ai/install.ps1 | iex
```

Ouvrir ensuite un nouveau terminal, puis vérifier :

```bash
claude --version
claude doctor
```

Lancer `claude` une première fois et suivre la connexion dans le navigateur. Autres méthodes : `brew install --cask claude-code` (Homebrew) ou `winget install Anthropic.ClaudeCode` (WinGet). Elles ne se mettent pas à jour seules.

### 4. Déclarer la clé API

Créer la clé dans la Console Anthropic et la placer dans une variable d'environnement. Le fichier `.env` est déjà ignoré par Git. La variable ne vaut que pour la session de terminal en cours.

macOS, Linux, WSL :

```bash
export ANTHROPIC_API_KEY="votre-clé"
```

Windows (PowerShell) :

```powershell
$env:ANTHROPIC_API_KEY="votre-clé"
```

Quand cette variable est définie, Claude Code demande s'il doit utiliser la clé plutôt que le compte. À trancher avec la question du budget.

### 5. Vérifier l'installation

```bash
python labs/00-setup/check_env.py
python labs/00-setup/check_env.py --ping
```

`check_env.py` contrôle les modules Python, la présence de la clé API (sans l'afficher) et la commande `claude`, sans appel réseau. Avec `--ping`, il envoie une requête minimale au modèle, ce qui consomme quelques tokens. Le modèle se règle avec la variable `CLAUDE_MODEL` (valeur par défaut : `claude-sonnet-5-5`).

### 6. Lancer les tests du lab 01

macOS, Linux, WSL :

```bash
LAB_TARGET=solution pytest labs/01-agentic-orchestration/tests
```

Windows (PowerShell) :

```powershell
$env:LAB_TARGET="solution"; pytest labs/01-agentic-orchestration/tests
```

Sur le corrigé, tous les tests passent, sans clé API. Sur le `starter` (`LAB_TARGET=starter`), ils échouent : c'est voulu, ils indiquent ce qu'il reste à écrire.

## Pièges fréquents

- `claude` introuvable après l'installation : ouvrir un nouveau terminal. Si cela persiste, le dossier d'installation n'est pas dans le PATH ; la page de dépannage de Claude Code explique la correction.
- Variables d'environnement perdues : elles disparaissent avec le terminal. Pour les garder, les ajouter au profil du shell.
- Options de `claude -p` : leurs noms évoluent. Les contrôler avec `claude --help` avant de suivre une consigne de lab.
- Clé API : ne pas la coller dans un fichier du dépôt, ni dans une question posée à l'équipe.

## Notes pour Windows

Les labs ont été développés et testés sous Linux. Rien n'a été exécuté sous Windows : les points suivants viennent de la lecture du code et des documentations, plus une émulation d'une locale non UTF-8 (288 tests sur 289 passent, le dernier échoue à cause de la locale ASCII de l'émulation sur les arguments de commande, pas sous Windows).

- Les README des labs 02 à 05 écrivent les commandes à la façon bash (`LAB_TARGET=solution pytest ...`). Sous PowerShell : `$env:LAB_TARGET="solution"; pytest ...`. Sous CMD : `set LAB_TARGET=solution && pytest ...`. La variable reste définie dans la session : la supprimer ou la changer avant de passer au `starter` (`$env:LAB_TARGET="starter"`).
- Les fichiers du dépôt sont en UTF-8 et en fins de ligne LF (`.gitattributes`). Si un éditeur les convertit en CRLF ou en Windows-1252, des tests qui comparent du texte peuvent échouer.
- Les appels à `claude -p` depuis Python lisent et écrivent en UTF-8 explicitement : c'est voulu, ne le retirez pas.
- Le script d'activation du venv peut être bloqué par la politique d'exécution de PowerShell : voir l'étape 2.
- Si une commande de la documentation d'Anthropic donne un résultat différent sous Windows natif et sous WSL, notez-le dans le README du lab : c'est exactement le type de piège à partager.

## Critères de réussite

- `check_env.py` n'affiche aucune ligne `MANQUE`.
- Les tests du lab 01 passent sur le corrigé.
- `claude --version` affiche un numéro de version et la connexion est faite.

## À décider avant le kickoff

Qui fournit les clés API et avec quel budget ; où héberger le dépôt Git ; accès à l'examen (voir `PLAN.md`).
