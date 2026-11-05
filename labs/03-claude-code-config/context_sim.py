"""Simulation du chargement des instructions de Claude Code (fournie).

Elle reprend les règles décrites dans la page « How Claude remembers your project » de la documentation
(consultée le 29 octobre 2026). Ce n'est PAS le code de Claude Code : le vrai contrôle se fait dans Claude Code avec
la commande `/memory`, qui liste les fichiers chargés. Règles simulées :

  - au lancement : `CLAUDE.md`, `.claude/CLAUDE.md` et `CLAUDE.local.md` du dossier de travail, plus les règles de
    `.claude/rules/` qui n'ont pas de `paths` (ou dont le frontmatter YAML est illisible : il est alors ignoré) ;
  - les fichiers sont concaténés, ils ne s'écrasent pas ;
  - `@chemin` importe un fichier (relatif au fichier qui l'importe, 4 niveaux au plus), sauf dans un bloc de code ;
  - à l'accès à un fichier (Read, Write, Edit) : le `CLAUDE.md` des sous-dossiers traversés et les règles dont un
    motif `paths` correspond au fichier se chargent à ce moment-là.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

MAX_IMPORT_DEPTH = 4
IMPORT = re.compile(r"(?<![\w`])@([\w./-]+\.[\w]+)")


@dataclass(frozen=True)
class Loaded:
    path: str  # relatif à la racine du dépôt
    reason: str  # launch, import, subdir, rule, rule-path


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """(frontmatter, corps). Frontmatter None s'il est absent ou si le YAML est illisible."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    raw, body = text[4:end], text[end + 4:].lstrip("\n")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, body
    return (data if isinstance(data, dict) else None), body


def expand_braces(pattern: str) -> list[str]:
    m = re.search(r"\{([^{}]*)\}", pattern)
    if not m:
        return [pattern]
    out: list[str] = []
    for alt in m.group(1).split(","):
        out.extend(expand_braces(pattern[: m.start()] + alt + pattern[m.end():]))
    return out


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    i, out = 0, ""
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
            continue
        if pattern.startswith("**", i):
            out += ".*"
            i += 2
            continue
        out += {"*": "[^/]*", "?": "[^/]"}.get(c, re.escape(c))
        i += 1
    return re.compile(out + r"\Z")


def matches(patterns: list[str] | str, relpath: str) -> bool:
    if isinstance(patterns, str):
        patterns = [p.strip() for p in patterns.split(",") if p.strip()]
    return any(glob_to_regex(expanded).match(relpath) for p in patterns for expanded in expand_braces(p))


def rule_paths(path: Path) -> list[str] | None:
    """Motifs `paths` d'une règle, ou None si elle est inconditionnelle."""
    front, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    if not front or "paths" not in front:
        return None
    value = front["paths"]
    if isinstance(value, str):
        return [p.strip() for p in value.split(",") if p.strip()]
    return [str(p) for p in value] if isinstance(value, list) else None


def imports_of(path: Path) -> list[str]:
    """Chemins importés par `@...` (hors blocs de code et code en ligne)."""
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    return IMPORT.findall(text)


class Context:
    def __init__(self, repo: Path):
        self.repo = repo
        self.loaded: list[Loaded] = []
        self._seen: set[str] = set()

    def _rel(self, path: Path) -> str:
        return path.relative_to(self.repo).as_posix()

    def _add(self, path: Path, reason: str, depth: int = 0) -> None:
        rel = self._rel(path)
        if rel in self._seen or not path.is_file():
            return
        self._seen.add(rel)
        self.loaded.append(Loaded(rel, reason))
        if depth < MAX_IMPORT_DEPTH:
            for target in imports_of(path):
                self._add((path.parent / target).resolve(), "import", depth + 1)

    def launch(self) -> "Context":
        for name in ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md"):
            self._add(self.repo / name, "launch")
        for rule in sorted((self.repo / ".claude" / "rules").rglob("*.md")):
            if rule_paths(rule) is None:
                self._add(rule, "rule")
        return self

    def access(self, relpath: str) -> "Context":
        target = self.repo / relpath
        parts = Path(relpath).parent.parts
        for i in range(1, len(parts) + 1):
            directory = self.repo.joinpath(*parts[:i])
            for name in ("CLAUDE.md", "CLAUDE.local.md"):
                self._add(directory / name, "subdir")
        for rule in sorted((self.repo / ".claude" / "rules").rglob("*.md")):
            patterns = rule_paths(rule)
            if patterns is not None and matches(patterns, relpath):
                self._add(rule, "rule-path")
        _ = target
        return self

    def paths(self) -> list[str]:
        return [item.path for item in self.loaded]
