"""Tests hors ligne de l'exercice 7 (qualité, relecture humaine). LAB_TARGET=starter (défaut) ou solution."""
from __future__ import annotations

from helpers import quality


def records():
    rows = [{"segment": "pdf_text", "correct": True} for _ in range(97)]
    rows += [{"segment": "pdf_text", "correct": False} for _ in range(3)]
    rows += [{"segment": "scan_noisy", "correct": True} for _ in range(7)]
    rows += [{"segment": "scan_noisy", "correct": False} for _ in range(3)]
    return rows


def test_a_high_global_accuracy_hides_a_weak_segment():
    rows = records()
    overall = sum(r["correct"] for r in rows) / len(rows)
    by_segment = quality.accuracy_by_segment(rows)
    assert overall > 0.94
    assert by_segment == {"pdf_text": 0.97, "scan_noisy": 0.7}
    assert quality.weak_segments(by_segment, floor=0.9) == ["scan_noisy"]


def test_stratified_sample_takes_each_stratum_and_is_reproducible():
    rows = [{"id": i, "segment": "a" if i < 50 else "b" if i < 95 else "c"} for i in range(100)]
    sample = quality.stratified_sample(rows, "segment", 5, seed=3)
    counts = {s: sum(1 for r in sample if r["segment"] == s) for s in "abc"}
    assert counts == {"a": 5, "b": 5, "c": 5}
    assert quality.stratified_sample(rows, "segment", 5, seed=3) == sample
    small = quality.stratified_sample([{"segment": "x"}, {"segment": "x"}], "segment", 5)
    assert len(small) == 2


def test_thresholds_are_calibrated_per_field_on_labeled_data():
    labeled = (
        [("invoice_date", 0.95, True)] * 5
        + [("invoice_date", 0.9, True)] * 3
        + [("invoice_date", 0.7, False)] * 3
        + [("invoice_date", 0.6, False)] * 2
        + [("vat_number", 0.9, False)] * 5
    )
    thresholds = quality.calibrate_thresholds(labeled, target_precision=0.95, min_count=3)
    assert thresholds["invoice_date"] == 0.9
    assert thresholds["vat_number"] > 1.0  # jamais assez fiable : toujours en revue


def test_route_for_review_uses_threshold_missing_confidence_and_flags():
    thresholds = {"invoice_date": 0.9}
    confidence = {"invoice_date": 0.85, "currency": 0.95, "vat_number": None, "supplier_name": 0.99}
    assert quality.route_for_review(confidence, thresholds, flagged_fields={"currency"}) == ["currency", "invoice_date", "vat_number"]
    assert quality.route_for_review(confidence, thresholds) == ["invoice_date", "vat_number"]


def test_limited_reviewer_capacity_takes_the_most_uncertain_cases_first():
    items = [{"id": i, "confidence": c} for i, c in enumerate([0.9, 0.2, 0.6, 0.4, 0.95])]
    chosen = quality.prioritize_for_capacity(items, 2)
    assert [i["id"] for i in chosen] == [1, 3]


def test_a_threshold_needs_enough_labeled_values_to_be_trusted():
    labeled = [("currency", 0.99, True)] * 2 + [("currency", 0.5, False)] * 4
    assert quality.calibrate_thresholds(labeled, target_precision=0.95, min_count=3)["currency"] > 1.0
    assert quality.calibrate_thresholds(labeled, target_precision=0.95, min_count=2)["currency"] == 0.99


def test_unknown_fields_use_the_default_threshold():
    confidence = {"payment_terms": 0.7, "supplier_name": 0.85}
    assert quality.route_for_review(confidence, {}, default_threshold=0.8) == ["payment_terms"]
