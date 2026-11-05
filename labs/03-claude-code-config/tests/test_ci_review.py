"""Exercice 5 : script de revue CI. Tout est testé hors ligne avec un faux exécuteur ; un test lance le vrai CLI
sans identifiants pour vérifier le chemin d'échec."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from helpers03 import LAB, TARGET_DIR, build_repo, ci_review

SQL = {
    "file": "src/api/invoices.py", "line": 13, "category": "security", "severity": "high",
    "title": "Injection SQL", "explanation": "f-string dans la requête", "snippet": "query = f\"SELECT id, total FROM invoices WHERE customer_name = '{customer_name}'\"",
    "suggestion": "Utiliser une requête paramétrée.",
}
ARITY = {
    "file": "src/api/invoices.py", "line": 11, "category": "cross_file", "severity": "high",
    "title": "Appelant non mis à jour", "explanation": "apply_discount exige désormais cap", "snippet": "return apply_discount(invoice[\"total\"], rate)",
    "suggestion": None,
}
STYLE = {**SQL, "category": "bug", "severity": "low", "title": "Nom", "snippet": "x = 1"}


def cli_json(findings=None, **extra):
    payload = {"type": "result", "is_error": False, "result": "ok", "session_id": "s"}
    if findings is not None:
        payload["structured_output"] = {"findings": findings}
    payload.update(extra)
    return json.dumps(payload)


class FakeRun:
    def __init__(self, stdout, code=0, stderr=""):
        self.stdout, self.code, self.stderr = stdout, code, stderr
        self.calls = []

    def __call__(self, argv, stdin):
        self.calls.append((argv, stdin))
        return self.code, self.stdout, self.stderr


def flag_value(argv, flag):
    return argv[argv.index(flag) + 1]


# --- la ligne de commande ----------------------------------------------------------------------

def test_command_is_a_non_interactive_json_run_with_a_schema():
    argv = ci_review.build_command()
    assert argv[0] == "claude" and "-p" in argv
    assert flag_value(argv, "--output-format") == "json"
    schema = json.loads(flag_value(argv, "--json-schema"))
    Draft202012Validator.check_schema(schema)
    assert schema == ci_review.REVIEW_SCHEMA


def test_command_limits_tools_to_read_only_and_caps_the_budget():
    argv = ci_review.build_command(max_budget_usd=0.25)
    tools = set(flag_value(argv, "--allowedTools").split(","))
    assert tools and tools <= {"Read", "Grep", "Glob"}
    assert flag_value(argv, "--max-budget-usd") == "0.25"
    assert "--dangerously-skip-permissions" not in argv


def test_review_runs_in_a_fresh_session_that_is_not_kept():
    argv = ci_review.build_command()
    assert "--resume" not in argv and "--continue" not in argv and "-c" not in argv and "-r" not in argv
    assert "--no-session-persistence" in argv


def test_bare_mode_is_on_by_default_for_ci_and_can_be_turned_off():
    assert "--bare" in ci_review.build_command()
    assert "--bare" not in ci_review.build_command(bare=False)
    assert flag_value(ci_review.build_command(model="m"), "--model") == "m"


def test_prompt_states_three_explicit_criteria_and_what_to_ignore():
    prompt = flag_value(ci_review.build_command(), "-p").lower()
    assert not prompt.startswith("todo")
    assert "security" in prompt and "bug" in prompt and "cross_file" in prompt
    assert "ignore" in prompt
    assert "vide" in prompt, "autoriser une liste vide"
    assert not any(w in prompt for w in ("sois prudent", "problèmes importants"))


def test_the_diff_goes_through_stdin_not_the_command_line():
    run = FakeRun(cli_json([]))
    ci_review.run_review(run, "DIFF-SECRET-123")
    argv, stdin = run.calls[0]
    assert stdin == "DIFF-SECRET-123"
    assert not any("DIFF-SECRET-123" in a for a in argv)


def test_schema_describes_the_findings():
    schema = ci_review.REVIEW_SCHEMA
    item = schema["properties"]["findings"]["items"]
    assert {"file", "category", "severity", "title", "explanation", "snippet"} <= set(item["required"])
    assert set(item["properties"]["severity"]["enum"]) == {"high", "medium", "low"}
    assert set(item["properties"]["category"]["enum"]) == {"security", "bug", "cross_file"}
    assert Draft202012Validator(schema).is_valid({"findings": []})


# --- lecture du résultat -----------------------------------------------------------------------

def test_parse_returns_the_findings_from_structured_output():
    assert ci_review.parse_result(cli_json([SQL, ARITY])) == [SQL, ARITY]
    assert ci_review.parse_result(cli_json([])) == []


def test_missing_structured_output_is_an_error_not_an_empty_review():
    with pytest.raises(ci_review.ReviewError):
        ci_review.parse_result(cli_json(None))


def test_error_flag_unreadable_output_and_invalid_schema_are_errors():
    with pytest.raises(ci_review.ReviewError, match="Authentication"):
        ci_review.parse_result(json.dumps({"is_error": True, "result": "Authentication error"}))
    with pytest.raises(ci_review.ReviewError):
        ci_review.parse_result("pas du json")
    with pytest.raises(ci_review.ReviewError):
        ci_review.parse_result(cli_json([{**SQL, "severity": "critique"}]))


# --- ne signaler que le nouveau ----------------------------------------------------------------

def test_fingerprint_survives_a_line_shift_and_whitespace_but_not_another_defect():
    moved = {**SQL, "line": 40, "snippet": "  " + SQL["snippet"].replace(" ", "  ")}
    assert ci_review.fingerprint(moved) == ci_review.fingerprint(SQL)
    assert ci_review.fingerprint(ARITY) != ci_review.fingerprint(SQL)
    assert ci_review.fingerprint({**SQL, "file": "src/api/other.py"}) != ci_review.fingerprint(SQL)


def test_only_findings_not_already_reported_are_kept():
    known = {ci_review.fingerprint(SQL)}
    assert ci_review.only_new([SQL, ARITY], known) == [ARITY]
    assert ci_review.only_new([SQL], known) == []


# --- orchestration et code de sortie -----------------------------------------------------------

def test_run_review_reports_new_findings_and_blocks_on_a_new_high_one():
    outcome = ci_review.run_review(FakeRun(cli_json([SQL, ARITY])), "diff")
    assert outcome.findings == [SQL, ARITY] and outcome.new_findings == [SQL, ARITY]
    assert outcome.blocking is True and outcome.exit_code == 1


def test_already_reported_findings_do_not_block_again():
    outcome = ci_review.run_review(FakeRun(cli_json([SQL])), "diff", known={ci_review.fingerprint(SQL)})
    assert outcome.new_findings == [] and outcome.blocking is False and outcome.exit_code == 0


def test_low_severity_findings_do_not_block():
    assert ci_review.run_review(FakeRun(cli_json([STYLE])), "diff").exit_code == 0


def test_empty_review_succeeds():
    outcome = ci_review.run_review(FakeRun(cli_json([])), "diff")
    assert outcome.new_findings == [] and outcome.exit_code == 0


def test_cli_failures_are_errors_never_a_green_review():
    with pytest.raises(ci_review.ReviewError):
        ci_review.run_review(FakeRun("", code=1, stderr="Error: boom"), "diff")
    with pytest.raises(ci_review.ReviewError):
        ci_review.run_review(FakeRun(cli_json([]), code=1, stderr="crash"), "diff")
    with pytest.raises(ci_review.ReviewError, match="Authentication"):
        ci_review.run_review(FakeRun(json.dumps({"is_error": True, "result": "Authentication error"}), code=1), "diff")


def test_main_returns_2_when_the_review_is_unusable(monkeypatch, capsys):
    monkeypatch.setattr(ci_review, "subprocess_runner", FakeRun("", code=1, stderr="x"))
    monkeypatch.setattr(sys, "stdin", __import__("io").StringIO("diff"))
    assert ci_review.main() == 2
    assert "inexploitable" in capsys.readouterr().err


def test_main_prints_findings_as_json_and_exits_1_on_a_blocking_one(monkeypatch, capsys):
    monkeypatch.setattr(ci_review, "subprocess_runner", FakeRun(cli_json([SQL])))
    monkeypatch.setattr(sys, "stdin", __import__("io").StringIO("diff"))
    assert ci_review.main() == 1
    assert json.loads(capsys.readouterr().out)["new_findings"][0]["title"] == "Injection SQL"


# --- le vrai CLI, chemin d'échec ----------------------------------------------------------------

@pytest.mark.skipif(shutil.which("claude") is None, reason="CLI claude absent")
def test_real_cli_without_credentials_fails_cleanly(tmp_path):
    """`--bare` ignore les identifiants de connexion : sans ANTHROPIC_API_KEY, le CLI répond une erreur d'authentification,
    et notre script doit la transformer en ReviewError (pas en revue verte)."""
    import os

    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN")}
    env["HOME"] = str(tmp_path)

    def real_runner(argv, stdin):
        import subprocess

        proc = subprocess.run(argv, input=stdin, capture_output=True, encoding="utf-8", errors="replace", timeout=120, env=env, cwd=tmp_path)
        return proc.returncode, proc.stdout, proc.stderr

    with pytest.raises(ci_review.ReviewError):
        ci_review.run_review(real_runner, "diff vide")


# --- workflow ----------------------------------------------------------------------------------

def test_github_workflow_runs_on_pull_requests_with_minimal_permissions_and_a_secret(tmp_path):
    path = build_repo(tmp_path) / ".github/workflows/review.yml"
    text = path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    triggers = workflow.get("on", workflow.get(True))  # YAML lit `on` comme le booléen True
    assert "pull_request" in triggers
    assert workflow["permissions"] == {"contents": "read"}
    assert "secrets.ANTHROPIC_API_KEY" in text and "sk-ant" not in text
    assert "ci_review.py" in text and "@anthropic-ai/claude-code" in text
