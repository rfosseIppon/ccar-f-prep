"""Chargement des modules testés (LAB_TARGET=starter par défaut, ou solution) et outils de test du lab 02."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

LAB = Path(__file__).resolve().parent.parent
TARGET = os.environ.get("LAB_TARGET", "starter")
TARGET_DIR = LAB / TARGET
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(TARGET_DIR))

import baseline  # noqa: E402
import builtin_tasks  # noqa: E402
import mcp_compat  # noqa: E402
import mcp_config  # noqa: E402
import selection  # noqa: E402
import shop_backend  # noqa: E402
import tools15  # noqa: E402
import tool_defs  # noqa: E402
import distribution  # noqa: E402
import builtin_tools  # noqa: E402
import tool_choice_probe  # noqa: E402

TOOL_NAMES = {"lookup_order", "find_orders", "search_orders"}


def run(coro: Any) -> Any:
    return asyncio.run(coro)


def tool_use(name: str, **input_: Any) -> NS:
    return NS(type="tool_use", id="toolu_x", name=name, input=input_)


def reply(*blocks: NS) -> NS:
    return NS(stop_reason="tool_use", content=list(blocks))


class FakeClient:
    """Répond avec une fonction `rule(kwargs) -> réponse` et garde une photo des requêtes."""

    def __init__(self, rule: Any):
        self.rule = rule
        self.calls: list[dict[str, Any]] = []
        self.messages = NS(create=self._create)

    def _create(self, **kwargs: Any) -> NS:
        self.calls.append(kwargs)
        return self.rule(kwargs)


class Api400(Exception):
    status_code = 400
