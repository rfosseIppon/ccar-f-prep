"""Garde-fou pour les mainteneurs du dépôt (pas pour les apprenants).

Les dossiers `starter/` doivent rester incomplets : seuls les tests d'intégrité du socle fournis
passent. Ce script lance les tests avec LAB_TARGET=starter et compare les tests qui passent à la liste
`tools/starter-passing.txt`.

- Un test qui passe sans figurer dans la liste : une solution a fuité dans un starter (ou un test est devenu trivial).
- Un test de la liste qui échoue : le socle fourni est cassé.

Usage :
    python tools/check_starters.py            # vérifie
    python tools/check_starters.py --update   # réécrit la liste après un changement voulu
"""
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTE = ROOT / "tools" / "starter-passing.txt"


def tests_qui_passent() -> set[str]:
    with tempfile.TemporaryDirectory() as tmp:
        xml = Path(tmp) / "starter.xml"
        env = dict(os.environ, LAB_TARGET="starter")
        subprocess.run(
            [sys.executable, "-m", "pytest", "labs", "-q", "-p", "no:cacheprovider", f"--junitxml={xml}"],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
        arbre = ET.parse(xml)
    passes = set()
    for cas in arbre.iter("testcase"):
        if cas.find("failure") is None and cas.find("error") is None and cas.find("skipped") is None:
            passes.add(f"{cas.get('classname')}::{cas.get('name')}")
    return passes


def main() -> int:
    actuels = tests_qui_passent()
    if "--update" in sys.argv:
        LISTE.write_text("\n".join(sorted(actuels)) + "\n", encoding="utf-8")
        print(f"{len(actuels)} tests écrits dans {LISTE.relative_to(ROOT)}")
        return 0
    attendus = {l.strip() for l in LISTE.read_text(encoding="utf-8").splitlines() if l.strip()}
    en_trop, manquants = sorted(actuels - attendus), sorted(attendus - actuels)
    for t in en_trop:
        print(f"FUITE ? passe sur le starter alors qu'il devrait échouer : {t}")
    for t in manquants:
        print(f"SOCLE CASSÉ ? devrait passer sur le starter et échoue : {t}")
    if en_trop or manquants:
        return 1
    print(f"Starters conformes : {len(actuels)} tests d'intégrité passent, tous les autres échouent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
