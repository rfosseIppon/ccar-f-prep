"""Vérifie l'environnement de préparation. Aucun appel réseau sauf avec --ping."""
from __future__ import annotations

import importlib
import os
import shutil
import sys

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
MODULES = ["anthropic", "claude_agent_sdk", "mcp", "jsonschema", "pytest", "yaml"]


def check() -> int:
    manques = 0
    for name in MODULES:
        try:
            importlib.import_module(name)
            print(f"OK     module {name}")
        except ImportError:
            print(f"MANQUE module {name} (pip install -r requirements.txt)")
            manques += 1

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("OK     ANTHROPIC_API_KEY définie")
    else:
        print("MANQUE ANTHROPIC_API_KEY (nécessaire pour les exercices qui appellent le modèle)")
        manques += 1

    if shutil.which("claude"):
        print("OK     commande claude trouvée")
    else:
        print("MANQUE commande claude (nécessaire pour les labs 03 et 05)")
        manques += 1

    return manques


def ping() -> None:
    import anthropic

    client = anthropic.Anthropic()
    reponse = client.messages.create(
        model=MODEL,
        max_tokens=20,
        messages=[{"role": "user", "content": "Réponds uniquement par le mot : prêt"}],
    )
    texte = "".join(b.text for b in reponse.content if b.type == "text")
    print(f"Réponse du modèle {MODEL} : {texte.strip()}")


if __name__ == "__main__":
    manques = check()
    if "--ping" in sys.argv:
        ping()
    sys.exit(1 if manques else 0)
