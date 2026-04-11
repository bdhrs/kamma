import json
import subprocess

from click.exceptions import Exit

from kammika.agents import (
    DEFAULT_AGENT_ORDER,
    build_launch_command,
    describe_agent,
    detect_available_agents,
)
from kammika.commands import init as init_command


def test_detect_available_agents_keeps_supported_order():
    seen = []

    def fake_run(args: list[str]) -> subprocess.CompletedProcess:
        seen.append(args[0])
        return subprocess.CompletedProcess(
            args=args,
            returncode=0 if args[0] in {"claude", "opencode", "qwen"} else 1,
            stdout="",
            stderr="",
        )

    assert detect_available_agents(fake_run) == ["claude", "opencode", "qwen"]
    assert seen == DEFAULT_AGENT_ORDER


def test_detect_available_agents_skips_missing_binaries():
    def fake_run(args: list[str]) -> subprocess.CompletedProcess:
        if args[0] == "gemini":
            raise FileNotFoundError(args[0])
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    detected = detect_available_agents(fake_run)

    assert "gemini" not in detected
    assert detected[0] == "claude"


def test_build_launch_command_covers_supported_agents():
    prompt = "follow the issue"

    assert build_launch_command("claude", prompt) == [
        "claude",
        "--model",
        "opus",
        "--dangerously-skip-permissions",
        prompt,
    ]
    assert build_launch_command("gemini", prompt) == [
        "gemini",
        "--prompt-interactive",
        prompt,
    ]
    assert build_launch_command("opencode", prompt) == [
        "opencode",
        "--model",
        "openai/gpt-5.4",
        "--prompt",
        prompt,
    ]
    assert build_launch_command("codex", prompt) == ["codex", prompt]
    assert build_launch_command("kilo", prompt) == ["kilo", "--prompt", prompt]
    assert build_launch_command("qwen", prompt) == [
        "qwen",
        "--prompt-interactive",
        prompt,
    ]


def test_describe_agent_includes_model_when_known():
    assert describe_agent("claude", {}) == "Claude Code (opus)"
    assert describe_agent("opencode", {"opencode": "custom/model"}) == "OpenCode (custom/model)"
    assert describe_agent("gemini", {}) == "Gemini CLI"


def test_run_init_persists_detected_agents(tmp_path, monkeypatch):
    kamma_dir = tmp_path / "kamma"
    kamma_dir.mkdir()
    for name in ("tech.md", "workflow.md", "project.md"):
        (kamma_dir / name).write_text("ok\n")

    cfg_path = kamma_dir / "kammika.config.json"

    monkeypatch.setattr(init_command, "target_repo_root", lambda: tmp_path)
    monkeypatch.setattr(init_command, "kamma_dir", lambda: kamma_dir)
    monkeypatch.setattr(init_command, "config_path", lambda: cfg_path)
    monkeypatch.setattr(init_command, "_choose_repo", lambda current=None: "owner/repo")
    monkeypatch.setattr(init_command, "_choose_project", lambda owner, current=None: "owner/1")
    monkeypatch.setattr(init_command, "_detect_local_agents", lambda: ["claude", "opencode"])
    monkeypatch.setattr(init_command, "show_banner", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(init_command, "muted", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(init_command, "success", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(init_command, "info", lambda *_args, **_kwargs: None)

    init_command.run_init(show_next=False)

    config = json.loads(cfg_path.read_text())
    assert config["repo"] == "owner/repo"
    assert config["project"] == "owner/1"
    assert config["agents"] == ["claude", "opencode"]


def test_run_init_exits_when_no_agents_detected(tmp_path, monkeypatch):
    kamma_dir = tmp_path / "kamma"
    kamma_dir.mkdir()
    for name in ("tech.md", "workflow.md", "project.md"):
        (kamma_dir / name).write_text("ok\n")

    cfg_path = kamma_dir / "kammika.config.json"

    monkeypatch.setattr(init_command, "target_repo_root", lambda: tmp_path)
    monkeypatch.setattr(init_command, "kamma_dir", lambda: kamma_dir)
    monkeypatch.setattr(init_command, "config_path", lambda: cfg_path)
    monkeypatch.setattr(init_command, "_choose_repo", lambda current=None: "owner/repo")
    monkeypatch.setattr(init_command, "_choose_project", lambda owner, current=None: "owner/1")
    monkeypatch.setattr(init_command, "_detect_local_agents", lambda: [])
    monkeypatch.setattr(init_command, "show_banner", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(init_command, "muted", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(init_command, "error", lambda *_args, **_kwargs: None)

    try:
        init_command.run_init(show_next=False)
    except Exit as exc:
        assert exc.exit_code == 1
    else:
        raise AssertionError("Expected run_init to exit when no agents are detected")
