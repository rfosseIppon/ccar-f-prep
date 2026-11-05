"""Chargement des modules testés (LAB_TARGET=starter par défaut, ou solution) et dépôt de test du lab 03."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
TARGET = os.environ.get("LAB_TARGET", "starter")
TARGET_DIR = LAB / TARGET
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(TARGET_DIR))

import config_checks  # noqa: E402
import context_sim  # noqa: E402
import plan_tasks  # noqa: E402
import ci_review  # noqa: E402
import choices  # noqa: E402


def build_repo(tmp: Path) -> Path:
    """Dépôt d'exemple + configuration de la cible, dans un dossier temporaire."""
    repo = tmp / "repo"
    shutil.copytree(LAB / "sample_repo", repo)
    shutil.copytree(TARGET_DIR / "config", repo, dirs_exist_ok=True)
    return repo
