"""Exercices 3 et 4 : choix du mode et technique d'affinage."""
from __future__ import annotations

from helpers03 import choices, plan_tasks


def test_every_task_has_a_mode_and_a_one_sentence_justification():
    assert set(choices.PLAN_OR_DIRECT) == set(plan_tasks.TASKS_PLAN), "répondez à chaque tâche"
    assert set(choices.JUSTIFICATION) == set(plan_tasks.TASKS_PLAN)
    assert all(len(text.split()) >= 5 for text in choices.JUSTIFICATION.values())


def test_modes_match_the_expected_ones():
    assert set(choices.PLAN_OR_DIRECT) == set(plan_tasks.TASKS_PLAN), "répondez à chaque tâche"
    wrong = {t: v for t, v in choices.PLAN_OR_DIRECT.items() if v not in plan_tasks.PLAN_ACCEPTED[t]}
    assert not wrong, f"à revoir : {wrong}"


def test_every_situation_has_a_technique_from_the_list():
    assert set(choices.TECHNIQUE) == set(plan_tasks.SITUATIONS), "répondez à chaque situation"
    assert all(v in plan_tasks.TECHNIQUES for v in choices.TECHNIQUE.values())


def test_techniques_match_the_expected_ones():
    assert set(choices.TECHNIQUE) == set(plan_tasks.SITUATIONS), "répondez à chaque situation"
    wrong = {s: v for s, v in choices.TECHNIQUE.items() if v not in plan_tasks.TECHNIQUES_ACCEPTED[s]}
    assert not wrong, f"à revoir : {wrong}"
