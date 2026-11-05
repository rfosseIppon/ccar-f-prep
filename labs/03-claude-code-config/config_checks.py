"""Contrôles de forme des fichiers de configuration Claude Code (fournis).

Chaque fonction renvoie une liste de défauts lisibles ; liste vide si tout va bien. Règles tirées de la documentation
de Claude Code (pages « memory » et « skills », consultées le 29 octobre 2026).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from context_sim import split_frontmatter

MAX_CLAUDE_MD_LINES = 200  # « target under 200 lines per CLAUDE.md file »
MAX_DESCRIPTION_CHARS = 1536  # description + when_to_use tronquées au-delà dans la liste des skills
READ_ONLY_TOOLS = {"Read", "Grep", "Glob"}


def tool_list(value: Any) -> list[str]:
    """`allowed-tools` accepte une chaîne séparée par des espaces ou des virgules, ou une liste YAML."""
    if value is None:
        return []
    if isinstance(value, str):
        # Un motif comme `Bash(git add *)` contient des espaces : on lit des mots, ou des mots suivis de `(...)`.
        return re.findall(r"[^\s,()]+(?:\([^)]*\))?", value)
    return [str(t) for t in value]


def check_skill(path: Path) -> list[str]:
    problems: list[str] = []
    front, body = split_frontmatter(path.read_text(encoding="utf-8"))
    if front is None:
        return [f"{path.name} : frontmatter absent ou illisible"]
    if "TODO" in path.read_text(encoding="utf-8"):
        problems.append("le fichier contient encore un TODO")
    name = front.get("name", path.parent.name)
    if name != path.parent.name:
        problems.append(f"name `{name}` différent du dossier `{path.parent.name}`")
    description = str(front.get("description", "")).strip()
    if not description:
        problems.append("description absente : c'est elle qui décide du déclenchement")
    if len(description) + len(str(front.get("when_to_use", ""))) > MAX_DESCRIPTION_CHARS:
        problems.append(f"description + when_to_use dépassent {MAX_DESCRIPTION_CHARS} caractères")
    if front.get("context") not in (None, "fork"):
        problems.append("`context` ne vaut que `fork`")
    if front.get("context") == "fork" and len(body.split()) < 40:
        problems.append("`context: fork` demande des consignes explicites : le corps du skill devient le prompt du sous-agent")
    return problems


def check_command(path: Path) -> list[str]:
    problems: list[str] = []
    front, body = split_frontmatter(path.read_text(encoding="utf-8"))
    if front is None:
        return [f"{path.name} : frontmatter absent ou illisible"]
    if "TODO" in path.read_text(encoding="utf-8"):
        problems.append("le fichier contient encore un TODO")
    if not str(front.get("description", "")).strip():
        problems.append("description absente")
    if "$ARGUMENTS" not in body and not re.search(r"\$\d|\$ARGUMENTS\[\d\]", body):
        problems.append("aucun `$ARGUMENTS` : les arguments seraient ajoutés en fin de texte")
    if "$ARGUMENTS" in body and not front.get("argument-hint"):
        problems.append("`argument-hint` manquant : l'autocomplétion n'indique pas l'argument attendu")
    return problems


def expand_arguments(body: str, arguments: str) -> str:
    """Substitution documentée de `$ARGUMENTS` (et `$0`, `$1`... par position)."""
    parts = arguments.split()
    text = body.replace("$ARGUMENTS", arguments)
    return re.sub(r"\$(\d+)", lambda m: parts[int(m.group(1))] if int(m.group(1)) < len(parts) else "", text)
