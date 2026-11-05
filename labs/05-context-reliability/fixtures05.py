"""Socle du lab 05 (fourni, ne pas modifier) : dossier de 15 tours, sorties d'outils verbeuses, faux dépôt de 520 fichiers."""
from __future__ import annotations

from pathlib import Path
from typing import Any

# --- Exercice 1 : un dossier de 15 tours -------------------------------------------------------------------------

LOOKUP_ORDER_VERBOSE = {
    "order_id": "O-1001",
    "status": "delivered",
    "total_eur": 84.9,
    "owner": "C-77",
    "items": [{"sku": f"SKU-{i:03d}", "label": f"Article {i}", "qty": 1, "warehouse_bin": f"B-{i * 7}"} for i in range(1, 13)],
    "audit_trail": [{"ts": 1730000000 + i * 60, "actor": "system", "event": f"step-{i}"} for i in range(30)],
    "internal_notes": "x" * 600,
    "carrier_payload": {"raw": "y" * 800},
}

FILLERS = [
    "Quels sont les créneaux de livraison ?", "Et pour un retour en point relais ?", "Je peux changer l'adresse ?",
    "Vous livrez le samedi ?", "Et en Belgique ?", "Ma carte fidélité compte pour combien ?", "Comment suivre le colis ?",
    "Et les frais de retour ?", "Je peux avoir une facture ?", "Combien de temps pour le virement ?", "Merci, c'est tout.",
]


def case_events() -> list[dict[str, Any]]:
    """15 tours : les 3 faits critiques (commande, montant, engagement) apparaissent dans les 4 premiers."""
    ev: list[dict[str, Any]] = [
        {"user": "Bonjour, je suis alice@example.com. Ma commande O-1001 est arrivée abîmée.",
         "tools": [("get_customer", {"email": "alice@example.com"}, {"customer_id": "C-77", "name": "Alice", "tier": "gold"}),
                   ("lookup_order", {"order_id": "O-1001"}, dict(LOOKUP_ORDER_VERBOSE))],
         "assistant": "Je vois la commande O-1001, livrée. Que souhaitez-vous ?"},
        {"user": "Je voudrais 80 EUR de remboursement.",
         "tools": [("note_fact", {"key": "amount_discussed_eur", "value": "80 EUR demandés"}, None)],
         "assistant": "Noté : 80 EUR demandés."},
        {"user": "Finalement 60 EUR suffiront, un seul article est abîmé.",
         "tools": [("note_fact", {"key": "amount_discussed_eur", "value": "60 EUR (un article abîmé)"}, None)],
         "assistant": "D'accord pour 60 EUR."},
        {"user": "Quand serai-je remboursée ?",
         "tools": [("note_fact", {"key": "commitment", "value": "Remboursement de 60 EUR sous 5 jours ouvrés, confirmation par e-mail"}, None)],
         "assistant": "Remboursement de 60 EUR sous 5 jours ouvrés, avec un e-mail de confirmation."},
    ]
    for i, q in enumerate(FILLERS):
        tools = [("lookup_order", {"order_id": "O-1001"}, dict(LOOKUP_ORDER_VERBOSE))] if i % 4 == 0 else []
        ev.append({"user": q, "tools": tools, "assistant": f"Réponse {i + 1} à : {q}"})
    assert len(ev) == 15
    return ev


def build_history(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Messages au format de l'API : user, assistant (tool_use), user (tool_result), assistant (texte)."""
    messages: list[dict[str, Any]] = []
    for t, e in enumerate(events, start=1):
        messages.append({"role": "user", "content": e["user"]})
        if e["tools"]:
            messages.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": f"tu_{t}_{i}", "name": n, "input": inp} for i, (n, inp, _) in enumerate(e["tools"])]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"tu_{t}_{i}", "content": str(out)} for i, (_, _, out) in enumerate(e["tools"])]})
        messages.append({"role": "assistant", "content": [{"type": "text", "text": e["assistant"]}]})
    return messages


def replay(events: list[dict[str, Any]], ledger: Any) -> None:
    """Rejoue les appels d'outils d'un dossier dans un registre de faits (le code testé est celui du registre)."""
    for turn, e in enumerate(events, start=1):
        for name, tool_input, output in e["tools"]:
            if name == "note_fact":
                ledger.handle_note_fact(tool_input, turn)
            else:
                ledger.capture_tool_result(name, tool_input, output, turn)


# --- Exercice 4 : un faux dépôt de 520 fichiers -------------------------------------------------------------------

DEPS: dict[str, list[str]] = {
    "api": ["auth", "orders", "payments", "users"], "auth": ["db", "security"], "billing": ["models", "config"],
    "cache": ["config"], "config": [], "db": ["config", "logging"], "events": ["queue", "logging"],
    "export": ["models", "storage"], "http": ["logging"], "i18n": [], "jobs": ["queue", "tasks"], "logging": [],
    "mail": ["config", "i18n"], "models": ["db"], "notify": ["mail", "events"], "orders": ["models", "billing"],
    "payments": ["billing", "db", "security"], "pdf": ["i18n"], "queue": ["config"], "reports": ["export", "pdf"],
    "search": ["db", "cache"], "security": ["config", "logging"], "storage": ["config"], "tasks": ["queue"],
    "users": ["models", "auth"], "utils": [],
}
FILES_PER_PACKAGE = 20


def make_repo(root: Path) -> Path:
    """26 paquets x 20 fichiers = 520 fichiers. Chaque fichier importe les dépendances de son paquet."""
    for pkg, deps in DEPS.items():
        d = root / pkg
        d.mkdir(parents=True)
        for k in range(FILES_PER_PACKAGE):
            imports = [f"from {deps[k % len(deps)]} import helper_{k}"] if deps else []
            body = "\n".join(f"def {pkg}_fn_{k}_{j}(x):\n    return x + {j}  # " + "logique métier " * 8 for j in range(12))
            (d / f"mod{k:02d}.py").write_text("\n".join(imports) + "\n\n" + body + "\n", encoding="utf-8")
    return root


def explore_module(repo: Path, module: str) -> tuple[list[str], int]:
    """Doublure d'un sous-agent d'exploration : lit les fichiers d'un paquet et renvoie ses dépendances et le volume lu."""
    deps: set[str] = set()
    raw = 0
    for f in sorted((repo / module).glob("*.py")):
        text = f.read_text(encoding="utf-8")
        raw += len(text)
        for line in text.splitlines():
            if line.startswith("from "):
                deps.add(line.split()[1])
    return sorted(deps), raw
