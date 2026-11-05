"""Lecture et contrôle d'un fichier `.mcp.json` (fourni).

Règles reprises de la documentation de Claude Code : `${VAR}` et `${VAR:-défaut}` sont développés dans `command`,
`args`, `env`, `url` et `headers` ; une variable absente sans valeur par défaut reste telle quelle (Claude Code
affiche alors un avertissement). Un secret écrit en clair dans un fichier versionné est un défaut.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
SECRET_NAME = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD)", re.IGNORECASE)


def expand(value: str, env: dict[str, str]) -> tuple[str, list[str]]:
    """Développe les variables ; renvoie le texte et la liste des variables non résolues."""
    missing: list[str] = []

    def repl(match: re.Match[str]) -> str:
        name, default = match.group(1), match.group(2)
        if name in env:
            return env[name]
        if default is not None:
            return default
        missing.append(name)
        return match.group(0)

    return VAR.sub(repl, value), missing


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_config(config: dict[str, Any], env: dict[str, str] | None = None) -> list[str]:
    """Liste de défauts lisibles ; liste vide si le fichier est correct."""
    env = env or {}
    problems: list[str] = []
    servers = config.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        return ["`mcpServers` absent ou vide"]
    for name, spec in servers.items():
        kind = spec.get("type", "stdio" if "command" in spec else "http" if "url" in spec else None)
        if kind == "stdio":
            if not spec.get("command"):
                problems.append(f"{name} : serveur stdio sans `command`")
        elif kind in ("http", "sse"):
            if not spec.get("url"):
                problems.append(f"{name} : serveur {kind} sans `url`")
        else:
            problems.append(f"{name} : type de transport inconnu ou absent")
        secrets = {**spec.get("env", {}), **spec.get("headers", {})}
        for key, value in secrets.items():
            if isinstance(value, str) and SECRET_NAME.search(key) and "${" not in value:
                problems.append(f"{name} : `{key}` contient une valeur en clair ; utiliser ${{{key}}}")
        for text in [spec.get("command", ""), *spec.get("args", []), *[v for v in spec.get("env", {}).values() if isinstance(v, str)], spec.get("url", "")]:
            if isinstance(text, str):
                _, missing = expand(text, env)
                problems.extend(f"{name} : variable ${{{m}}} sans valeur ni défaut" for m in missing)
    return problems
