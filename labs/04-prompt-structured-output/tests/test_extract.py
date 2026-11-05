"""Tests hors ligne des exercices 1 à 3. LAB_TARGET=starter (défaut) ou solution."""
from __future__ import annotations

import json
from datetime import date

import pytest
from jsonschema import Draft202012Validator

from helpers import FakeClient, extract, reply, tool_use, valid_extraction

TODAY = date(2026, 10, 29)


def client_returning(*extractions):
    return FakeClient([reply(tool_use(extract.TOOL_NAME, **e)) for e in extractions])


# --- exercice 1 : requête et appel -------------------------------------------------------------

def test_request_uses_the_tool_with_auto_choice_by_default():
    req = extract.build_request("TEXTE DU DOCUMENT")
    assert [t["name"] for t in req["tools"]] == [extract.TOOL_NAME]
    assert req["tool_choice"] == {"type": "auto"}
    assert "strict" not in req["tools"][0]
    assert "TEXTE DU DOCUMENT" in str(req["messages"])


def test_forced_mode_forces_the_extraction_tool():
    req = extract.build_request("x", mode="forced")
    assert req["tool_choice"] == {"type": "tool", "name": extract.TOOL_NAME}


def test_strict_option_marks_the_tool_strict():
    assert extract.build_request("x", strict=True)["tools"][0]["strict"] is True


def test_unknown_mode_is_rejected():
    with pytest.raises(ValueError):
        extract.build_request("x", mode="n_importe_quoi")


def test_call_extraction_returns_the_tool_input():
    client = client_returning(valid_extraction())
    assert extract.call_extraction(client, "doc") == valid_extraction()


def test_call_extraction_without_tool_use_raises():
    from types import SimpleNamespace as NS

    client = FakeClient([NS(stop_reason="end_turn", content=[NS(type="text", text="Voici")])])
    with pytest.raises(extract.ExtractionError):
        extract.call_extraction(client, "doc")


# --- exercice 2 : schéma, valeurs absentes ----------------------------------------------------

SCHEMA = lambda: extract.INVOICE_TOOL["input_schema"]  # noqa: E731


def test_schema_is_a_valid_json_schema():
    Draft202012Validator.check_schema(SCHEMA())


def test_fields_missing_from_the_document_can_be_null_and_are_not_required():
    props, required = SCHEMA()["properties"], SCHEMA()["required"]
    for name in ("invoice_number", "invoice_date", "vat_number", "stated_total"):
        assert name in props, name
        assert name not in required, f"{name} ne doit pas être obligatoire"
        assert "null" in props[name]["type"], f"{name} doit accepter null"


def test_core_fields_are_required():
    assert {"supplier_name", "currency", "payment_terms", "line_items"} <= set(SCHEMA()["required"])


def test_enums_leave_room_for_other_and_unclear_with_a_detail_field():
    props = SCHEMA()["properties"]
    for name, detail in (("currency", "currency_detail"), ("payment_terms", "payment_terms_detail")):
        assert {"other", "unclear"} <= set(props[name]["enum"]), name
        assert detail in props, detail


def test_schema_rejects_unknown_fields():
    assert SCHEMA().get("additionalProperties") is False


def test_schema_accepts_a_document_without_vat_number():
    data = valid_extraction()
    del data["vat_number"]
    assert not list(Draft202012Validator(SCHEMA()).iter_errors(data))
    assert not list(Draft202012Validator(SCHEMA()).iter_errors(valid_extraction(vat_number=None)))


# --- exercice 3 : validation ------------------------------------------------------------------

def kinds(issues):
    return {(i.kind, i.pattern) for i in issues}


def test_valid_extraction_has_no_issue():
    assert extract.validate_extraction(valid_extraction(), TODAY) == []


def test_schema_error_is_reported_as_format():
    issues = extract.validate_extraction(valid_extraction(currency="XYZ"), TODAY)
    assert ("format", "schema") in kinds(issues)


def test_date_must_be_iso_and_plausible():
    assert ("format", "bad_date") in kinds(extract.validate_extraction(valid_extraction(invoice_date="12/03/2026"), TODAY))
    assert ("format", "bad_date") in kinds(extract.validate_extraction(valid_extraction(invoice_date="2031-01-01"), TODAY))
    assert ("format", "bad_date") in kinds(extract.validate_extraction(valid_extraction(invoice_date="2026-13-45"), TODAY))


def test_total_must_match_the_sum_of_the_lines():
    issues = extract.validate_extraction(valid_extraction(stated_total=130.0), TODAY)
    assert ("arithmetic", "total_mismatch") in kinds(issues)


def test_line_amount_must_match_quantity_times_unit_price():
    bad = valid_extraction(line_items=[{"description": "x", "quantity": 3, "unit_price": 50.0, "amount": 100.0}], stated_total=100.0)
    assert ("arithmetic", "line_mismatch") in kinds(extract.validate_extraction(bad, TODAY))


def test_missing_invoice_number_is_an_absent_information_not_a_format_error():
    issues = extract.validate_extraction(valid_extraction(invoice_number=None), TODAY)
    assert kinds(issues) == {("absent", "missing_invoice_number")}


def test_missing_vat_number_is_acceptable():
    assert extract.validate_extraction(valid_extraction(vat_number=None), TODAY) == []


def test_enrich_adds_calculated_total_and_conflict_flag():
    ok = extract.enrich(valid_extraction())
    assert ok["calculated_total"] == 100.0 and ok["conflict_detected"] is False
    bad = extract.enrich(valid_extraction(stated_total=130.0))
    assert bad["calculated_total"] == 100.0 and bad["conflict_detected"] is True


def test_retry_sends_document_previous_extraction_and_error():
    client = client_returning(valid_extraction(invoice_date="12/03/2026"), valid_extraction())
    result = extract.extract_with_retry(client, "TEXTE DU DOCUMENT", today=TODAY)
    assert result.attempts == 2 and result.needs_review is False
    retry_request = str(client.calls[1]["messages"])
    assert "TEXTE DU DOCUMENT" in retry_request
    assert "12/03/2026" in retry_request
    assert "invoice_date" in retry_request and "plausible" in retry_request
    assert "bad_date" in result.detected_patterns


def test_retry_is_capped():
    bad = valid_extraction(invoice_date="12/03/2026")
    third = valid_extraction(invoice_date="13/03/2026")
    second = valid_extraction(invoice_date="14/03/2026")
    result = extract.extract_with_retry(client_returning(bad, second, third), "doc", today=TODAY)
    assert result.attempts == 3 and result.needs_review is True
    result0 = extract.extract_with_retry(client_returning(bad), "doc", max_retries=0, today=TODAY)
    assert result0.attempts == 1 and result0.needs_review is True


def test_no_retry_when_the_information_is_absent_from_the_document():
    client = client_returning(valid_extraction(invoice_number=None))  # une seule réponse scriptée
    result = extract.extract_with_retry(client, "doc", today=TODAY)
    assert result.attempts == 1 and len(client.calls) == 1
    assert result.needs_review is True
    assert kinds(result.issues) == {("absent", "missing_invoice_number")}


def test_retry_stops_when_it_changes_nothing():
    mismatch = valid_extraction(stated_total=130.0)  # le défaut est dans le document
    client = client_returning(mismatch, dict(mismatch), dict(mismatch))
    result = extract.extract_with_retry(client, "doc", today=TODAY)
    assert result.attempts == 2 and len(client.calls) == 2
    assert result.needs_review is True
    assert result.data["conflict_detected"] is True
    assert json.dumps(result.data["calculated_total"]) == "100.0"
