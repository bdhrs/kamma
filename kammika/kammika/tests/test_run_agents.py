import subprocess
from pathlib import Path

import pytest
from click.exceptions import Exit

from kammika.commands.triage import Candidate
from kammika.commands import run as run_command
from kammika.config import KammikaConfig


def test_choose_agent_retries_until_valid(monkeypatch):
    answers = iter(["9", "2"])

    monkeypatch.setattr(run_command, "prompt_text", lambda *_args, **_kwargs: next(answers))
    monkeypatch.setattr(run_command, "muted", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(run_command.console, "print", lambda *_args, **_kwargs: None)

    assert run_command._choose_agent(["claude", "opencode"]) == "opencode"


def test_choose_agent_exits_when_no_supported_agents():
    with pytest.raises(Exit) as exc:
        run_command._choose_agent(["unknown"])

    assert exc.value.exit_code == 1


def test_launch_agent_uses_selected_agent_command(monkeypatch):
    recorded = {}

    def fake_run(args, cwd=None):
        recorded["args"] = args
        recorded["cwd"] = cwd
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(run_command.subprocess, "run", fake_run)
    monkeypatch.setattr(run_command, "info", lambda *_args, **_kwargs: None)

    exit_code = run_command._launch_agent(
        "do the work",
        "opencode",
        Path("/tmp/repo"),
        models={"opencode": "custom/model"},
    )

    assert exit_code == 0
    assert recorded == {
        "args": ["opencode", "--model", "custom/model", "--prompt", "do the work"],
        "cwd": "/tmp/repo",
    }


def test_launch_agent_returns_error_for_unknown_agent():
    assert run_command._launch_agent("do the work", "missing", Path("/tmp/repo")) == 1


def test_pick_issue_auto_selects_single_candidate_without_llm(tmp_path, monkeypatch):
    queue_file = tmp_path / "kammika.queue.json"
    config = KammikaConfig(repo="owner/repo", project="owner/1", agents=["claude", "opencode"])
    candidate = Candidate(number=7, title="Only issue", body="Fix it", labels=["P1"], age_days=3)

    monkeypatch.setattr(run_command, "_load_pending_queue", lambda: None)
    monkeypatch.setattr(run_command, "queue_path", lambda: queue_file)
    monkeypatch.setattr(run_command, "show_banner", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(run_command, "success", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(run_command.console, "print", lambda *_args, **_kwargs: None)

    def fake_get_candidates(_config):
        return [candidate]

    def fake_llm_pick(*_args, **_kwargs):
        raise AssertionError("_llm_pick should not be called for a single candidate")

    monkeypatch.setattr("kammika.commands.triage.get_candidates", fake_get_candidates)
    monkeypatch.setattr("kammika.commands.triage._llm_pick", fake_llm_pick)

    queue = run_command._pick_issue(config)

    assert queue == {
        "number": 7,
        "title": "Only issue",
        "body": "Fix it",
        "rationale": "Auto-selected because it is the only actionable issue",
        "source": "automatic",
        "picked_at": queue["picked_at"],
    }
    assert queue_file.exists()
    assert '"number": 7' in queue_file.read_text()
    assert '"source": "automatic"' in queue_file.read_text()
    assert '"rationale": "Auto-selected because it is the only actionable issue"' in queue_file.read_text()
