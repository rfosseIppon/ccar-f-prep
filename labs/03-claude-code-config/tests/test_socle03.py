"""Intégrité du socle fourni (passe quelle que soit la cible)."""
from __future__ import annotations

import shutil
import subprocess
import sys

import pytest

from helpers03 import LAB, config_checks, context_sim, plan_tasks


def test_sample_repo_tests_pass():
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(LAB / "sample_repo")], capture_output=True, encoding="utf-8", errors="replace", cwd=LAB / "sample_repo")
    assert proc.returncode == 0, proc.stdout[-300:]


@pytest.mark.skipif(shutil.which("git") is None, reason="git absent")
def test_the_sample_pull_request_diff_applies_to_the_sample_repo(tmp_path):
    repo = tmp_path / "r"
    shutil.copytree(LAB / "sample_repo", repo, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    proc = subprocess.run(["git", "apply", "--check", str(LAB / "sample_repo" / "pr.diff")], cwd=repo, capture_output=True, encoding="utf-8", errors="replace")
    assert proc.returncode == 0, proc.stderr


def test_glob_matching_follows_the_documented_patterns():
    m = context_sim.matches
    assert m(["**/*.ts"], "a/b/c.ts") and m(["**/*.ts"], "c.ts")
    assert m(["src/**/*"], "src/a/b.py") and not m(["src/**/*"], "lib/a.py")
    assert m(["*.md"], "README.md") and not m(["*.md"], "docs/README.md")
    assert m(["src/components/*.tsx"], "src/components/A.tsx") and not m(["src/components/*.tsx"], "src/components/x/A.tsx")
    assert m(["src/**/*.{ts,tsx}"], "src/a/B.tsx") and not m(["src/**/*.{ts,tsx}"], "src/a/B.js")
    assert m("src/**/*.py, lib/*.py", "lib/x.py")  # chaîne séparée par des virgules


def test_frontmatter_that_does_not_parse_is_ignored():
    front, body = context_sim.split_frontmatter("---\npaths: [oups\n---\ncorps\n")
    assert front is None and "corps" in body


def test_imports_ignore_code_spans_and_blocks(tmp_path):
    f = tmp_path / "CLAUDE.md"
    f.write_text("Voir @docs/a.md et `@docs/b.md`\n```\n@docs/c.md\n```\n", encoding="utf-8")
    assert context_sim.imports_of(f) == ["docs/a.md"]


def test_import_depth_is_capped_at_four_hops(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("@n1.md\n", encoding="utf-8")
    for i in range(1, 8):
        (tmp_path / f"n{i}.md").write_text(f"@n{i + 1}.md\n", encoding="utf-8")
    (tmp_path / "n8.md").write_text("fin\n", encoding="utf-8")
    loaded = context_sim.Context(tmp_path).launch().paths()
    assert loaded == ["CLAUDE.md", "n1.md", "n2.md", "n3.md", "n4.md"]


def test_expand_arguments():
    assert config_checks.expand_arguments("Teste $ARGUMENTS", "billing") == "Teste billing"
    assert config_checks.expand_arguments("a=$0 b=$1", "x y") == "a=x b=y"


def test_plan_task_data_is_consistent():
    assert set(plan_tasks.TASKS_PLAN) == set(plan_tasks.PLAN_ACCEPTED)
    assert set(plan_tasks.SITUATIONS) == set(plan_tasks.TECHNIQUES_ACCEPTED)
    assert all(a <= set(plan_tasks.TECHNIQUES) for a in plan_tasks.TECHNIQUES_ACCEPTED.values())
