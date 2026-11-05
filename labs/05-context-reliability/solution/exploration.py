"""CORRIGÉ exercice 4 : exploration d'un gros dépôt (notes persistées, synthèses bornées, sous-tâches adaptatives)."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

MAX_SYNTHESIS_CHARS = 600


class Scratchpad:
    """Fichier de notes d'exploration. Il survit à la perte du contexte : on le relit avant chaque phase."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def add(self, phase: str, finding: str) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"phase": phase, "finding": finding}, ensure_ascii=False) + "\n")

    def entries(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def render(self, max_chars: int = 2000) -> str:
        """Notes les plus récentes d'abord retenues si la place manque, affichées dans l'ordre chronologique."""
        kept: list[str] = []
        used = 0
        for e in reversed(self.entries()):
            line = f"- [{e['phase']}] {e['finding']}"
            if used + len(line) > max_chars:
                break
            kept.append(line)
            used += len(line) + 1
        return "\n".join(reversed(kept)) or "(aucune note)"


def bound_synthesis(text: str, max_chars: int = MAX_SYNTHESIS_CHARS) -> str:
    """Ce qu'un sous-agent renvoie au contexte principal : une synthèse courte, jamais la lecture brute."""
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 12]
    stop = max(cut.rfind(". "), cut.rfind("; "))
    cut = cut[: stop + 1] if stop > max_chars // 2 else cut
    return cut.rstrip() + " [tronqué]"


def phase_brief(pad: Scratchpad, phase: str, question: str, module: str) -> str:
    """Consigne d'un sous-agent : tout le contexte utile est écrit dedans (il ne voit pas la conversation)."""
    return (
        f"Question d'ensemble : {question}\n"
        f"Phase : {phase}. Module à examiner : {module}.\n"
        f"Notes déjà établies :\n{pad.render()}\n"
        f"Réponds en {MAX_SYNTHESIS_CHARS} caractères au plus : rôle du module, modules dont il dépend, "
        "fichiers clés. Ne recopie pas de code."
    )


@dataclass
class Finding:
    module: str
    depends_on: list[str] = field(default_factory=list)
    note: str = ""


def next_subtasks(findings: list[Finding], explored: set[str], budget: int) -> list[str]:
    """Décomposition adaptative : la suite dépend de ce qui vient d'être découvert, pas d'une liste fixée d'avance."""
    inbound: Counter[str] = Counter()
    for f in findings:
        for dep in f.depends_on:
            inbound[dep] += 1
    candidates = [m for m in inbound if m not in explored]
    candidates.sort(key=lambda m: (-inbound[m], m))
    return candidates[: max(budget, 0)]
