"""Exercice 5 : outils intégrés de Claude Code."""
from __future__ import annotations

from helpers02 import builtin_tasks, builtin_tools


def test_every_task_has_an_answer_from_the_allowed_tools():
    assert set(builtin_tools.CHOICES) == set(builtin_tasks.TASKS)
    assert all(v in builtin_tasks.ALLOWED for v in builtin_tools.CHOICES.values())


def test_answers_match_the_expected_tools():
    assert set(builtin_tools.CHOICES) == set(builtin_tasks.TASKS), "répondez à chaque tâche"
    wrong = {t: v for t, v in builtin_tools.CHOICES.items() if v not in builtin_tasks.ACCEPTED[t]}
    assert not wrong, f"à revoir : {wrong}"
