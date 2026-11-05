"""Mécanique de la mesure de sélection (fournie) : testée avec un faux modèle."""
from __future__ import annotations

from helpers02 import FakeClient, baseline, reply, selection, tool_use


def oracle(kwargs):
    query = kwargs["messages"][0]["content"]
    expected = next(q["expected"] for q in selection.load_queries() if q["query"] == query)
    return reply(tool_use(expected))


def test_perfect_model_scores_twenty_out_of_twenty():
    report = selection.evaluate_selection(FakeClient(oracle), baseline.BASELINE_TOOLS)
    assert report == {"correct": 20, "total": 20, "wrong": []}


def test_wrong_and_missing_choices_are_reported_with_the_query_id():
    def rule(kwargs):
        query = kwargs["messages"][0]["content"]
        if "CMD-10002 de marie" in query and "Où en est" in query:
            return reply(tool_use("find_orders"))
        if "casque Bluetooth ?" in query:
            return reply()  # répond sans outil
        return oracle(kwargs)

    report = selection.evaluate_selection(FakeClient(rule), baseline.BASELINE_TOOLS)
    assert report["correct"] == 18
    assert {(w["id"], w["got"]) for w in report["wrong"]} == {("q01", "find_orders"), ("q15", None)}


def test_the_request_lets_the_model_choose_among_the_given_tools():
    client = FakeClient(oracle)
    selection.evaluate_selection(client, baseline.BASELINE_TOOLS, selection.load_queries()[:1])
    call = client.calls[0]
    assert call["tool_choice"] == {"type": "auto"} and call["tools"] == baseline.BASELINE_TOOLS
