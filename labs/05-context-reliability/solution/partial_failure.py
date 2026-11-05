"""CORRIGÉ exercice 3 : panne partielle, provenance des affirmations, contradictions."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable

TRANSIENT = (TimeoutError, ConnectionError)


@dataclass(frozen=True)
class Claim:
    text: str
    source_name: str = ""
    source_url: str = ""
    date: str = ""  # ISO 8601
    metric: str = ""
    value: float | None = None

    @property
    def sourced(self) -> bool:
        return bool(self.source_name and self.source_url)


@dataclass
class SubResult:
    source: str
    status: str  # "ok" | "empty" | "timeout" | "unreachable"
    claims: list[Claim] = field(default_factory=list)
    error: str = ""
    attempts: int = 1


def run_with_recovery(source: str, fetch: Callable[[], list[Claim]], max_attempts: int = 3) -> SubResult:
    """Réessaie localement les erreurs transitoires ; remonte le reste avec ce qui a été tenté. Ne lève jamais."""
    last = ""
    for attempt in range(1, max_attempts + 1):
        try:
            claims = fetch()
        except TRANSIENT as exc:
            last = f"{type(exc).__name__}: {exc}"
            continue
        except Exception as exc:  # accès refusé, introuvable... : réessayer ne servirait à rien
            return SubResult(source, "unreachable", error=f"{type(exc).__name__}: {exc}", attempts=attempt)
        return SubResult(source, "ok" if claims else "empty", claims=list(claims), attempts=attempt)
    return SubResult(source, "timeout", error=last, attempts=max_attempts)


@dataclass
class Conflict:
    metric: str
    claims: list[Claim]
    same_period: bool


def find_conflicts(claims: list[Claim]) -> list[Conflict]:
    """Des valeurs différentes pour une même mesure, issues de sources différentes. On ne tranche pas."""
    by_metric: dict[str, list[Claim]] = defaultdict(list)
    for c in claims:
        if c.metric and c.value is not None and c.sourced:
            by_metric[c.metric].append(c)
    out: list[Conflict] = []
    for metric, group in by_metric.items():
        if len({c.value for c in group}) > 1 and len({c.source_name for c in group}) > 1:
            out.append(Conflict(metric, group, same_period=len({c.date for c in group}) == 1))
    return out


def _line(c: Claim) -> str:
    return f"- {c.text} (source : {c.source_name}, {c.source_url}, {c.date or 'date inconnue'})"


def build_report(question: str, results: list[SubResult]) -> str:
    """Rapport : synthèse en tête, confirmé, contradictions, puis lacunes (non couvert, à retenter)."""
    all_claims = [c for r in results for c in r.claims]
    confirmed = [c for c in all_claims if c.sourced]
    unsourced = [c for c in all_claims if not c.sourced]
    conflicts = find_conflicts(confirmed)
    in_conflict = {id(c) for k in conflicts for c in k.claims}
    ok = [r for r in results if r.status in ("ok", "empty")]
    out: list[str] = [f"# {question}", ""]
    out += [f"Couverture : {len(ok)} source(s) consultée(s) sur {len(results)}. "
            f"{len(confirmed)} constat(s) sourcé(s), {len(conflicts)} contradiction(s).", ""]

    out += ["## Confirmé"]
    plain = [c for c in confirmed if id(c) not in in_conflict]
    out += [_line(c) for c in plain] or ["Aucun constat confirmé."]
    empty = [r.source for r in results if r.status == "empty"]
    if empty:
        out += ["", "Consultées sans résultat (absence de résultat, pas une panne) : " + ", ".join(empty)]

    if conflicts:
        out += ["", "## Contradictions (à trancher par une personne)"]
        for k in conflicts:
            note = "même période" if k.same_period else "périodes différentes : peut-être un simple écart de date"
            out.append(f"- {k.metric} ({note})")
            out += ["  " + _line(c) for c in k.claims]

    if unsourced:
        out += ["", "## Non vérifié (affirmations sans source exploitable)"]
        out += [f"- {c.text}" for c in unsourced]

    lost = [r for r in results if r.status == "unreachable"]
    retry = [r for r in results if r.status == "timeout"]
    out += ["", "## Lacunes"]
    out += ["### Non couvert (source inaccessible, ne rien en conclure)"]
    out += [f"- {r.source} : {r.error}" for r in lost] or ["- aucune"]
    out += ["### À retenter (échec transitoire)"]
    out += [f"- {r.source} : {r.error} ({r.attempts} tentative(s))" for r in retry] or ["- aucune"]
    return "\n".join(out)
