"""Intégrité du corpus fourni (passe quelle que soit la cible)."""
from __future__ import annotations

from helpers import scoring


def test_corpus_has_ten_documents_with_truth():
    docs, truth = scoring.load_corpus()
    assert len(docs) == 10
    assert set(docs) == set(truth)
    assert all(text.strip() for text in docs.values())


def test_lines_total_matches_line_items():
    _, truth = scoring.load_corpus()
    for doc_id, t in truth.items():
        assert abs(sum(i["amount"] for i in t["line_items"]) - t["lines_total"]) < 0.005, doc_id


def test_exactly_three_documents_have_a_really_absent_field():
    _, truth = scoring.load_corpus()
    absent = {d: [f for f in ("invoice_number", "invoice_date", "vat_number") if t[f] is None] for d, t in truth.items()}
    assert {d for d, f in absent.items() if f} == {"doc_04", "doc_07", "doc_09"}


def test_one_document_has_an_inconsistent_total():
    _, truth = scoring.load_corpus()
    assert [d for d, t in truth.items() if t["conflict_detected"]] == ["doc_08"]


def test_two_documents_carry_an_ambiguity_note():
    _, truth = scoring.load_corpus()
    assert {"doc_05", "doc_06"} <= {d for d, t in truth.items() if "ambiguë" in t.get("note", "")}


def test_scoring_ignores_case_accents_and_punctuation():
    truth = {"supplier_name": "Dupuis Électricité SARL", "vat_number": "FR11222333444"}
    pred = {"supplier_name": "DUPUIS ELECTRICITE SARL", "vat_number": "FR 11 222 333 444"}
    scores = scoring.score_extraction(pred, truth)
    assert scores["supplier_name"] and scores["vat_number"]


def test_invented_values_detects_filled_absent_fields():
    assert scoring.invented_values({"vat_number": "FR00000000000"}, {"vat_number": None}) == ["vat_number"]
    assert scoring.invented_values({"vat_number": None}, {"vat_number": None}) == []
