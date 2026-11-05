"""Tests hors ligne de l'exercice 3 : ils vérifient la CONFIGURATION du système multi-agents.

Ils ne prouvent pas le comportement du modèle : l'exécution réelle demande une clé API. Les contrôles sur
le texte des prompts sont des garde-fous grossiers, pas une évaluation de leur qualité.
LAB_TARGET=starter (défaut) ou solution.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("claude_agent_sdk")

LAB = Path(__file__).resolve().parent.parent
TARGET = os.environ.get("LAB_TARGET", "starter")
_spec = importlib.util.spec_from_file_location("multi_agent_under_test", LAB / TARGET / "multi_agent_research.py")
ma = importlib.util.module_from_spec(_spec)
sys.modules["multi_agent_under_test"] = ma
_spec.loader.exec_module(ma)

DELEGATION = {"Agent", "Task"}  # « Task » dans le guide d'examen, « Agent » dans les versions récentes


@pytest.fixture(scope="module")
def options():
    return ma.build_options()


def prompt_of(options) -> str:
    text = (options.system_prompt or "").strip().lower()
    assert not text.startswith("todo"), "le prompt du coordinateur est encore le texte de départ"
    return text


def test_coordinator_can_only_delegate(options):
    assert options.allowed_tools, "le coordinateur doit disposer de l'outil de délégation"
    assert set(options.allowed_tools) <= DELEGATION


def test_three_subagents_are_defined(options):
    assert {"searcher", "analyst", "writer"} <= set(options.agents)
    for name, agent in options.agents.items():
        assert agent.description.strip() and not agent.description.startswith("TODO"), name
        assert agent.prompt.strip() and not agent.prompt.startswith("TODO"), name


def test_subagent_tool_lists_are_minimal(options):
    allowed = {
        "searcher": {"WebSearch", "WebFetch"},
        "analyst": {"Read", "Grep", "Glob"},
        "writer": {"Write", "Read"},
    }
    for name, tools in allowed.items():
        listed = set(options.agents[name].tools or [])
        assert listed, f"{name} : liste d'outils vide ou absente"
        assert listed <= tools, f"{name} a des outils superflus : {sorted(listed - tools)}"
    for agent in options.agents.values():
        assert "Bash" not in (agent.tools or [])
        assert not set(agent.tools or []) & DELEGATION, "un sous-agent ne délègue pas"


def test_coordinator_prompt_states_that_subagents_do_not_share_context(options):
    text = prompt_of(options)
    assert "ne voit pas" in text or "n'hérite" in text or "ne partage" in text


def test_coordinator_prompt_launches_independent_work_in_parallel(options):
    text = prompt_of(options)
    assert "même tour" in text or "parallèle" in text


def test_coordinator_prompt_requires_a_gaps_section(options):
    assert "lacunes" in prompt_of(options)


def test_coordinator_prompt_distinguishes_access_failure_from_empty_result(options):
    text = prompt_of(options)
    assert "inaccessible" in text and ("rien trouvé" in text or "aucun résultat" in text)


def test_searcher_returns_claims_with_source_metadata(options):
    searcher = options.agents["searcher"].prompt.lower()
    assert "source_url" in searcher
    assert "confiance" in searcher
