"""Exercice 3 : `.mcp.json`. Les contrôles de mcp_config sont fournis ; le fichier de la cible est testé pour de vrai."""
from __future__ import annotations

import os
import sys

from helpers02 import TARGET_DIR, mcp_compat, mcp_config, run, TOOL_NAMES


# --- le contrôleur fourni --------------------------------------------------------------------

def test_expand_supports_plain_and_default_forms():
    assert mcp_config.expand("${A}", {"A": "1"}) == ("1", [])
    assert mcp_config.expand("${A:-x}", {}) == ("x", [])
    assert mcp_config.expand("${A:-x}", {"A": "1"}) == ("1", [])
    text, missing = mcp_config.expand("${B}/mcp", {})
    assert text == "${B}/mcp" and missing == ["B"]  # laissé tel quel, comme le fait Claude Code


def test_checker_flags_the_usual_mistakes():
    check = mcp_config.check_config
    assert check({}) and check({"mcpServers": {}})
    assert any("command" in p for p in check({"mcpServers": {"s": {"type": "stdio"}}}))
    assert any("en clair" in p for p in check({"mcpServers": {"s": {"command": "x", "env": {"SHOP_API_KEY": "sk-123"}}}}))
    assert any("sans valeur" in p for p in check({"mcpServers": {"s": {"command": "x", "env": {"A": "${INCONNUE}"}}}}))
    assert check({"mcpServers": {"s": {"command": "x", "env": {"SHOP_API_KEY": "${SHOP_API_KEY:-demo}"}}}}) == []


# --- le fichier de la cible ------------------------------------------------------------------

def load():
    path = TARGET_DIR / ".mcp.json"
    assert path.exists(), f"créez {path}"
    return mcp_config.load_config(path)


def test_project_mcp_json_is_well_formed_and_has_no_plain_secret():
    assert mcp_config.check_config(load()) == []


def test_project_mcp_json_declares_the_shop_server_in_stdio():
    spec = load()["mcpServers"]["shop"]
    assert spec["type"] == "stdio" and spec["args"] == ["shop_server.py"]


def test_server_declared_in_mcp_json_starts_and_lists_the_three_tools():
    """Lance le serveur comme Claude Code (sous-processus, stdio) avec l'environnement développé.

    `python3` du fichier est remplacé par l'interpréteur courant pour rester portable (sous Windows, la commande est `python`).
    """
    spec = load()["mcpServers"]["shop"]
    env = dict(os.environ)
    for key, value in spec.get("env", {}).items():
        env[key] = mcp_config.expand(value, os.environ)[0]
    command = sys.executable if spec["command"] in ("python", "python3") else spec["command"]

    async def go():
        async with mcp_compat.stdio_session(command, spec["args"], env, str(TARGET_DIR)) as session:
            return await session.list_tools(), await session.call_tool("find_orders", {"customer_email": "nadia@example.com"})

    tools, outcome = run(go())
    assert {t.name for t in tools} == TOOL_NAMES
    assert outcome.is_error is False and outcome.json()["count"] == 0
