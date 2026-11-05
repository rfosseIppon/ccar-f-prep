"""Exercice 6 : sonde de tool_choice, testée hors ligne avec un faux modèle (le vrai comportement se mesure avec run_tool_choice.py)."""
from __future__ import annotations

import pytest

from helpers02 import Api400, FakeClient, baseline, reply, tool_choice_probe as probe, tool_use

TOOLS = baseline.BASELINE_TOOLS


def test_build_tool_choice_shapes():
    assert probe.build_tool_choice("auto", TOOLS) == {"type": "auto"}
    assert probe.build_tool_choice("any", TOOLS) == {"type": "any"}
    assert probe.build_tool_choice("tool", TOOLS) == {"type": "tool", "name": TOOLS[0]["name"]}
    with pytest.raises(ValueError):
        probe.build_tool_choice("toujours", TOOLS)


def strict_model(kwargs):
    """Modèle qui n'accepte que `auto`, comme l'indique la documentation pour les modèles récents."""
    if kwargs["tool_choice"]["type"] != "auto":
        raise Api400("tool_choice any/tool non pris en charge par ce modèle")
    return reply(tool_use("lookup_order"))


def test_probe_records_which_values_the_model_accepts():
    client = FakeClient(strict_model)
    result = probe.probe_tool_choice(client, "modele-x", TOOLS)
    assert result["auto"] == {"accepted": True, "tools_called": ["lookup_order"]}
    assert result["any"]["accepted"] is False and result["any"]["status"] == 400 and "non pris en charge" in result["any"]["error"]
    assert result["tool"]["accepted"] is False
    assert [c["tool_choice"]["type"] for c in client.calls] == ["auto", "any", "tool"]
    assert all(c["model"] == "modele-x" and c["tools"] == TOOLS for c in client.calls)


def test_probe_on_a_permissive_model():
    result = probe.probe_tool_choice(FakeClient(lambda kw: reply(tool_use("find_orders"))), "modele-y", TOOLS)
    assert all(r["accepted"] for r in result.values())


def test_probe_can_be_limited_to_some_values():
    client = FakeClient(strict_model)
    assert list(probe.probe_tool_choice(client, "m", TOOLS, choices=("auto",))) == ["auto"]
    assert len(client.calls) == 1
