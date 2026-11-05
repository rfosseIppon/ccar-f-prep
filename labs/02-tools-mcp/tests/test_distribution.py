"""Exercice 4 : répartition des 15 outils entre 3 agents."""
from __future__ import annotations

from helpers02 import distribution, tools15

D = distribution.DISTRIBUTION


def agents():
    assert D, "DISTRIBUTION est vide"
    return D.items()


def test_three_agents():
    assert len(D) == 3


def test_every_tool_goes_to_exactly_one_agent():
    assigned = [t for _, tools in agents() for t in tools]
    assert sorted(assigned) == sorted(tools15.DOMAIN), "chaque outil une fois, aucun outil inconnu"


def test_four_or_five_tools_per_agent():
    assert all(4 <= len(tools) <= 5 for _, tools in agents())


def test_each_agent_covers_at_most_two_domains():
    for agent, tools in agents():
        assert len({tools15.DOMAIN[t] for t in tools}) <= 2, f"{agent} mélange trop de domaines"


def test_each_agent_holds_at_most_two_write_tools():
    for agent, tools in agents():
        assert sum(t in tools15.WRITES for t in tools) <= 2, f"{agent} concentre trop d'outils qui écrivent"


def test_each_boundary_is_justified_in_one_sentence():
    assert set(distribution.RATIONALE) == set(D)
    assert D and all(len(text.split()) >= 6 for text in distribution.RATIONALE.values())
