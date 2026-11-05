"""Le pipeline complet, hors ligne : un faux modèle qui lit la vérité terrain. LAB_TARGET=starter (défaut) ou solution."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace as NS

from helpers import LAB, extract, scoring, tool_use

sys.path.insert(0, str(LAB))
import run_corpus  # noqa: E402

DOCS, TRUTH = scoring.load_corpus()


class TruthClient:
    """Retrouve le document dans la requête et renvoie l'extraction de la vérité terrain."""

    def __init__(self, invent_vat_for=None):
        self.invent_vat_for = invent_vat_for or set()
        self.messages = NS(create=self._create)

    def _create(self, **kwargs):
        text = str(kwargs["messages"])
        doc_id = next(d for d, body in DOCS.items() if body.strip().splitlines()[0] in text)
        t = TRUTH[doc_id]
        data = {k: t[k] for k in ("supplier_name", "invoice_number", "invoice_date", "currency", "vat_number", "payment_terms", "stated_total")}
        data["line_items"] = t["line_items"]
        if doc_id in self.invent_vat_for:
            data["vat_number"] = "FR00000000000"
        return NS(stop_reason="tool_use", content=[tool_use(extract.TOOL_NAME, **data)])


def test_a_faithful_model_scores_perfectly_and_flags_only_the_problem_documents():
    report = run_corpus.evaluate(TruthClient(), extract.extract_with_retry)
    assert all(v == 1.0 for v in report["by_field"].values())
    assert report["invented"] == {}
    assert report["needs_review"] == ["doc_07", "doc_08", "doc_09"]  # date absente, total incohérent, numéro absent


def test_a_model_that_invents_a_vat_number_is_caught():
    report = run_corpus.evaluate(TruthClient(invent_vat_for={"doc_04"}), extract.extract_with_retry)
    assert report["invented"] == {"doc_04": ["vat_number"]}
    assert report["by_field"]["vat_number"] < 1.0
