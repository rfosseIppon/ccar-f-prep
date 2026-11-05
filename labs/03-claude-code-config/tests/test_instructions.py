"""Exercice 1 : hiérarchie d'instructions. Les tests simulent le chargement décrit dans la documentation ;
le contrôle réel se fait dans Claude Code avec `/memory`."""
from __future__ import annotations

import pytest

from helpers03 import build_repo, config_checks, context_sim


@pytest.fixture()
def repo(tmp_path):
    return build_repo(tmp_path)


def read(repo, rel):
    return (repo / rel).read_text(encoding="utf-8")


# --- CLAUDE.md racine -----------------------------------------------------------------------

def test_root_claude_md_is_short_and_has_no_todo(repo):
    text = read(repo, "CLAUDE.md")
    assert "todo" not in text.lower()
    assert 5 <= len(text.splitlines()) <= config_checks.MAX_CLAUDE_MD_LINES


def test_root_claude_md_gives_test_command_architecture_and_constraints(repo):
    text = read(repo, "CLAUDE.md").lower()
    assert "pytest" in text
    assert "architecture" in text and "contraintes" in text


def test_root_claude_md_imports_the_architecture_document(repo):
    assert "docs/architecture.md" in context_sim.imports_of(repo / "CLAUDE.md")


def test_no_secret_is_written_in_instruction_files(repo):
    for rel in ("CLAUDE.md", "src/api/CLAUDE.md"):
        assert "todo" not in read(repo, rel).lower(), f"{rel} est encore le texte de départ"
        assert "sk-" not in read(repo, rel)


def test_personal_notes_file_is_gitignored(repo):
    assert "CLAUDE.local.md" in read(repo, ".gitignore").splitlines()


# --- ce qui se charge, et quand -------------------------------------------------------------

def test_launch_loads_root_instructions_the_import_and_unscoped_rules_only(repo):
    loaded = context_sim.Context(repo).launch().paths()
    assert "CLAUDE.md" in loaded and "docs/architecture.md" in loaded
    assert ".claude/rules/testing.md" in loaded
    assert ".claude/rules/api.md" not in loaded, "la règle de l'API doit être limitée à src/api par `paths`"
    assert "src/api/CLAUDE.md" not in loaded, "le CLAUDE.md d'un sous-dossier se charge à la demande"


def test_touching_an_api_file_loads_the_local_instructions_and_the_api_rule(repo):
    ctx = context_sim.Context(repo).launch().access("src/api/invoices.py")
    reasons = {item.path: item.reason for item in ctx.loaded}
    assert reasons.get("src/api/CLAUDE.md") == "subdir"
    assert reasons.get(".claude/rules/api.md") == "rule-path", "la règle doit se charger à l'accès au fichier, pas au lancement"


def test_touching_billing_or_tests_does_not_load_api_instructions(repo):
    for rel in ("src/billing/discounts.py", "tests/test_discounts.py"):
        loaded = context_sim.Context(repo).launch().access(rel).paths()
        assert "src/api/CLAUDE.md" not in loaded and ".claude/rules/api.md" not in loaded, rel


def test_api_rule_frontmatter_is_valid_yaml_with_a_scoped_glob(repo):
    patterns = context_sim.rule_paths(repo / ".claude/rules/api.md")
    assert patterns, "frontmatter `paths` absent ou illisible : la règle se chargerait partout"
    assert context_sim.matches(patterns, "src/api/invoices.py")
    assert not context_sim.matches(patterns, "src/billing/discounts.py")


def test_local_instructions_do_not_repeat_the_root_ones(repo):
    root = {line.strip() for line in read(repo, "CLAUDE.md").splitlines() if line.strip()}
    local = [line.strip() for line in read(repo, "src/api/CLAUDE.md").splitlines() if line.strip()]
    assert local and "todo" not in " ".join(local).lower() and not [line for line in local if line in root]
    assert len(local) <= 30
