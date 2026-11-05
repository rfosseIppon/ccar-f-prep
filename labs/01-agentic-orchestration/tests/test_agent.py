"""Tests hors ligne du lab 01 : un faux client scripte les réponses du modèle.

LAB_TARGET=starter (défaut) ou LAB_TARGET=solution.
"""
from __future__ import annotations

import importlib.util
import itertools
import os
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

LAB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB))
TARGET = os.environ.get("LAB_TARGET", "starter")

_spec = importlib.util.spec_from_file_location("agent_under_test", LAB / TARGET / "agent.py")
agent = importlib.util.module_from_spec(_spec)
sys.modules["agent_under_test"] = agent  # requis par les dataclasses (annotations différées)
_spec.loader.exec_module(agent)


# --- outils de test ---------------------------------------------------------

def text(t: str) -> NS:
    return NS(type="text", text=t)


def tool_use(id_: str, name: str, **input_: object) -> NS:
    return NS(type="tool_use", id=id_, name=name, input=input_)


def resp(stop_reason: str, *blocks: NS) -> NS:
    return NS(stop_reason=stop_reason, content=list(blocks))


class FakeClient:
    """Rejoue des réponses scriptées et garde une photo des messages à chaque appel."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls: list[dict] = []
        self.messages = NS(create=self._create)

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        if not self._responses:
            raise AssertionError("Plus de réponse scriptée : la boucle ne s'arrête pas.")
        return self._responses.pop(0)


class LoopingClient:
    """Demande un outil à chaque tour, sans jamais conclure."""

    def __init__(self):
        self.count = 0
        self._ids = itertools.count(1)
        self.messages = NS(create=self._create)

    def _create(self, **kwargs):
        self.count += 1
        return resp("tool_use", tool_use(f"t{next(self._ids)}", "lookup_order", order_id="O-1001"))


def verified_state(email: str = "alice@example.com"):
    state = agent.SessionState()
    out = agent.execute_tool("get_customer", {"email": email}, state)
    assert not out.get("isError")
    return state


# --- exercice 1 : la boucle -------------------------------------------------

def test_stops_on_end_turn():
    client = FakeClient([resp("end_turn", text("Bonjour"))])
    result = agent.run_agent(client, "Salut")
    assert result.final_text == "Bonjour"
    assert result.stop_reason == "end_turn"
    assert len(client.calls) == 1


def test_continues_while_tool_use():
    client = FakeClient(
        [
            resp("tool_use", tool_use("t1", "get_customer", email="alice@example.com")),
            resp("tool_use", tool_use("t2", "lookup_order", order_id="O-1001")),
            resp("end_turn", text("Votre commande est livrée.")),
        ]
    )
    result = agent.run_agent(client, "Où en est ma commande O-1001 ? alice@example.com")
    assert len(client.calls) == 3
    assert [name for name, _ in result.tool_calls] == ["get_customer", "lookup_order"]
    assert result.final_text == "Votre commande est livrée."


def test_tool_results_of_one_turn_share_one_user_message():
    client = FakeClient(
        [
            resp(
                "tool_use",
                tool_use("t1", "get_customer", email="alice@example.com"),
                tool_use("t2", "lookup_order", order_id="O-1001"),
            ),
            resp("end_turn", text("ok")),
        ]
    )
    agent.run_agent(client, "x")
    history = client.calls[1]["messages"]
    assert history[-2]["role"] == "assistant"
    assert history[-1]["role"] == "user"
    blocks = history[-1]["content"]
    assert [b["type"] for b in blocks] == ["tool_result", "tool_result"]
    assert {b["tool_use_id"] for b in blocks} == {"t1", "t2"}


def test_error_results_are_flagged():
    client = FakeClient(
        [
            resp("tool_use", tool_use("t1", "lookup_order", order_id="O-9999")),
            resp("end_turn", text("Introuvable.")),
        ]
    )
    agent.run_agent(client, "x")
    block = client.calls[1]["messages"][-1]["content"][0]
    assert block["is_error"] is True


def test_iteration_cap_escalates_instead_of_looping():
    client = LoopingClient()
    result = agent.run_agent(client, "x", max_iterations=3)
    assert client.count == 3
    assert result.stop_reason == "max_iterations"
    assert result.escalated is True


def test_unexpected_stop_reason_does_not_crash():
    client = FakeClient([resp("max_tokens", text("coupé"))])
    result = agent.run_agent(client, "x")
    assert result.stop_reason == "max_tokens"
    assert result.final_text == "coupé"


# --- exercice 2 : garde-fous en code -----------------------------------------

def test_refund_requires_identified_customer():
    out = agent.execute_tool("process_refund", {"order_id": "O-1001", "amount_eur": 10.0}, agent.SessionState())
    assert out["isError"] is True
    assert out["errorCategory"] == "prerequisite_not_met"
    assert out["isRetryable"] is True


def test_refund_over_limit_is_blocked_in_code():
    state = verified_state()
    out = agent.execute_tool("process_refund", {"order_id": "O-1002", "amount_eur": 250.0}, state)
    assert out["isError"] is True
    assert out["errorCategory"] == "policy_limit"
    assert out["isRetryable"] is False
    assert "refund_id" not in out
    assert "escalate_to_human" in out["message"]


def test_refund_within_limit_succeeds():
    state = verified_state()
    out = agent.execute_tool("process_refund", {"order_id": "O-1001", "amount_eur": 42.0}, state)
    assert not out.get("isError")
    assert out["refund_id"] == "R-O-1001"


def test_refund_on_another_customers_order_is_forbidden():
    state = verified_state("alice@example.com")
    out = agent.execute_tool("process_refund", {"order_id": "O-2001", "amount_eur": 10.0}, state)
    assert out["isError"] is True
    assert out["errorCategory"] == "forbidden"


def test_escalation_updates_state():
    state = agent.SessionState()
    out = agent.execute_tool(
        "escalate_to_human",
        {"summary": "Client demande un humain.", "reason": "customer_request"},
        state,
    )
    assert state.escalated is True
    assert out["status"] == "queued"


def test_two_refunds_in_one_turn_are_guarded_independently():
    """Demande à plusieurs sujets : chaque appel d'un même tour est contrôlé séparément."""
    client = FakeClient(
        [
            resp("tool_use", tool_use("t1", "get_customer", email="alice@example.com")),
            resp(
                "tool_use",
                tool_use("t2", "process_refund", order_id="O-1001", amount_eur=42.0),
                tool_use("t3", "process_refund", order_id="O-1002", amount_eur=250.0),
            ),
            resp("end_turn", text("Un remboursement effectué, l'autre transmis à un conseiller.")),
        ]
    )
    agent.run_agent(client, "x")
    blocks = client.calls[2]["messages"][-1]["content"]
    assert [b["tool_use_id"] for b in blocks] == ["t2", "t3"]
    assert not blocks[0].get("is_error")
    assert blocks[1]["is_error"] is True


@pytest.mark.parametrize(
    "name,args",
    [("outil_inconnu", {}), ("lookup_order", {"mauvais_champ": 1})],
)
def test_bad_calls_return_validation_errors(name, args):
    out = agent.execute_tool(name, args, agent.SessionState())
    assert out["isError"] is True
    assert out["errorCategory"] == "validation"
