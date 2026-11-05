"""Exercice 2 : un skill à contexte isolé et une commande slash."""
from __future__ import annotations

import pytest

from helpers03 import build_repo, config_checks, context_sim


@pytest.fixture()
def repo(tmp_path):
    return build_repo(tmp_path)


def skill(repo):
    path = repo / ".claude/skills/revue-securite/SKILL.md"
    front, body = context_sim.split_frontmatter(path.read_text(encoding="utf-8"))
    return path, front, body


def test_skill_passes_the_form_checks(repo):
    path, _, _ = skill(repo)
    assert config_checks.check_skill(path) == []


def test_skill_runs_in_a_forked_context_with_a_task_description_that_triggers_it(repo):
    _, front, _ = skill(repo)
    assert front["context"] == "fork"
    description = front["description"].lower()
    assert "sécurité" in description and ("quand" in description or "utiliser" in description)


def test_skill_is_read_only_by_pre_approval_AND_by_removal(repo):
    """`allowed-tools` pré-approuve, il ne restreint pas : pour retirer des outils, `disallowed-tools`."""
    _, front, _ = skill(repo)
    allowed = set(config_checks.tool_list(front.get("allowed-tools")))
    disallowed = set(config_checks.tool_list(front.get("disallowed-tools")))
    assert allowed and allowed <= config_checks.READ_ONLY_TOOLS
    assert {"Edit", "Write"} <= disallowed
    assert not allowed & disallowed


def test_skill_prompt_states_three_explicit_criteria_and_what_to_ignore(repo):
    _, _, body = skill(repo)
    low = body.lower()
    assert "$ARGUMENTS" in body
    assert "injection" in low and "secret" in low and "contrôle d'accès" in low
    assert "ignorer" in low or "ignore" in low


def test_skill_asks_for_a_structured_answer_and_allows_an_empty_one(repo):
    _, _, body = skill(repo)
    low = body.lower()
    assert all(w in low for w in ("fichier", "ligne", "gravité"))
    assert "aucun problème" in low


def test_skill_has_an_argument_hint(repo):
    _, front, _ = skill(repo)
    assert front.get("argument-hint")


# --- commande slash ----------------------------------------------------------------------

def test_slash_command_passes_the_form_checks(repo):
    assert config_checks.check_command(repo / ".claude/commands/test-module.md") == []


def test_slash_command_expands_its_argument_into_a_pytest_call(repo):
    _, body = context_sim.split_frontmatter((repo / ".claude/commands/test-module.md").read_text(encoding="utf-8"))
    expanded = config_checks.expand_arguments(body, "discounts")
    assert "tests/test_discounts.py" in expanded and "$ARGUMENTS" not in expanded


def test_slash_command_pre_approves_only_the_test_command(repo):
    front, _ = context_sim.split_frontmatter((repo / ".claude/commands/test-module.md").read_text(encoding="utf-8"))
    tools = config_checks.tool_list(front.get("allowed-tools"))
    assert tools and all(t.startswith("Bash(python -m pytest") for t in tools)
