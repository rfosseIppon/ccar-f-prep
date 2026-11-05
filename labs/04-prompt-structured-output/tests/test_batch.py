"""Tests hors ligne de l'exercice 5 (lots). LAB_TARGET=starter (défaut) ou solution."""
from __future__ import annotations

import random
from types import SimpleNamespace as NS

import pytest

from helpers import FakeClient, batch, extract, tool_use, valid_extraction

DOCS = {f"doc_{i:02d}": f"Texte du document {i}\nsuite {i}\n" for i in range(1, 7)}


def success(custom_id, **extraction):
    message = NS(content=[tool_use(extract.TOOL_NAME, **(extraction or valid_extraction()))])
    return NS(custom_id=custom_id, result=NS(type="succeeded", message=message))


def failure(custom_id, kind):
    return NS(custom_id=custom_id, result=NS(type=kind))


def sample_results():
    return [
        success("doc_01"),
        failure("doc_02", "errored"),
        failure("doc_03", "expired"),
        failure("doc_04", "canceled"),
        NS(custom_id="doc_05", result=NS(type="succeeded", message=NS(content=[NS(type="text", text="pas d'outil")]))),
        # doc_06 : aucun résultat
        failure("doc_99", "errored"),
    ]


def test_build_batch_requests_gives_one_request_per_document_with_its_custom_id():
    requests = batch.build_batch_requests(DOCS)
    assert [r["custom_id"] for r in requests] == list(DOCS)
    assert all("model" in r["params"] and "messages" in r["params"] for r in requests)
    assert "Texte du document 3" in str(requests[2]["params"]["messages"])


def test_invalid_custom_id_is_rejected():
    with pytest.raises(ValueError):
        batch.build_batch_requests({"facture 1/2026": "x"})


def test_submit_batch_returns_the_batch_id():
    captured = {}

    def create(requests):
        captured["requests"] = requests
        return NS(id="msgbatch_42")

    client = NS(messages=NS(batches=NS(create=create)))
    assert batch.submit_batch(client, DOCS) == "msgbatch_42"
    assert len(captured["requests"]) == len(DOCS)


def test_reconcile_sorts_every_result_into_its_bucket():
    out = batch.reconcile(sample_results(), DOCS)
    assert list(out.succeeded) == ["doc_01"]
    assert out.errored == ["doc_02"]
    assert out.expired == ["doc_03"]
    assert out.canceled == ["doc_04"]
    assert out.malformed == ["doc_05"]
    assert out.missing == ["doc_06"]
    assert out.unknown == ["doc_99"]


def test_reconcile_does_not_depend_on_the_order_of_results():
    results = [success(f"doc_0{i}", **valid_extraction(supplier_name=f"Fournisseur {i}")) for i in range(1, 6)]
    shuffled = results[:]
    random.Random(1).shuffle(shuffled)
    a = batch.reconcile(results, DOCS)
    b = batch.reconcile(shuffled, DOCS)
    assert a.succeeded == b.succeeded
    assert b.succeeded["doc_03"]["supplier_name"] == "Fournisseur 3"


def test_retry_documents_resubmits_only_failures():
    out = batch.reconcile(sample_results(), DOCS)
    retry = batch.retry_documents(out, DOCS)
    assert set(retry) == {"doc_02", "doc_03", "doc_05", "doc_06"}
    assert "doc_01" not in retry and "doc_04" not in retry
    assert retry["doc_02"] == DOCS["doc_02"]


def test_split_long_document_keeps_every_line():
    text = "".join(f"ligne {i:03d}\n" for i in range(50))
    chunks = batch.split_long_document(text, 100)
    assert "".join(chunks) == text
    assert all(len(c) <= 100 for c in chunks) and len(chunks) > 1


def test_retry_documents_splits_long_documents_with_part_ids():
    docs = {"doc_01": "".join(f"ligne {i:03d}\n" for i in range(50)), "doc_02": "court\n"}
    out = batch.BatchOutcome(errored=["doc_01", "doc_02"])
    retry = batch.retry_documents(out, docs, max_chars=100)
    assert "doc_01" not in retry and retry["doc_02"] == "court\n"
    parts = [k for k in retry if k.startswith("doc_01__part")]
    assert parts and parts[0] == "doc_01__part1"
    assert "".join(retry[k] for k in parts) == docs["doc_01"]


def test_submission_window_from_the_sla():
    assert batch.submission_window_hours(30) == 6
    assert batch.submission_window_hours(48) == 24
    with pytest.raises(ValueError):
        batch.submission_window_hours(24)
