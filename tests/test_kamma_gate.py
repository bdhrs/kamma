"""Tests for hooks/kamma_gate.py.

The gate is driven as a subprocess with JSON on stdin — the same path Claude Code
uses. Importing spec_gate() directly would prove the plumbing, not the behaviour
the hook is installed for.

Every test runs with HOME redirected into tmp_path. The hook keeps its quick-run
markers under ~/.cache/kamma/, and a leaked marker on a real repo path would
silently switch the gate off.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GATE = REPO_ROOT / "hooks" / "kamma_gate.py"
SESSION = "test-session-0001"


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SESSION)
    return home


def run_gate(
    cwd: Path,
    tool_name: str = "Write",
    tool_input: dict | None = None,
    session_id: str = SESSION,
    subcommand: str = "spec-gate",
) -> tuple[str, int]:
    """Run the gate with a PreToolUse-shaped payload. Returns (stdout, returncode)."""
    payload = {
        "session_id": session_id,
        "cwd": str(cwd),
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input if tool_input is not None else {},
    }
    return run_gate_raw(json.dumps(payload), subcommand)


def run_gate_raw(raw: str, subcommand: str = "spec-gate") -> tuple[str, int]:
    proc = subprocess.run(
        [sys.executable, str(GATE), subcommand],
        input=raw,
        capture_output=True,
        text=True,
    )
    return proc.stdout, proc.returncode


def is_denied(stdout: str) -> bool:
    if not stdout.strip():
        return False
    data = json.loads(stdout)
    decision = data.get("hookSpecificOutput", {}).get("permissionDecision")
    return decision == "deny"


def deny_reason(stdout: str) -> str:
    return json.loads(stdout)["hookSpecificOutput"]["permissionDecisionReason"]


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A scratch repo with kamma set up and an empty threads directory."""
    root = tmp_path / "repo"
    (root / "kamma" / "threads").mkdir(parents=True)
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("x = 1\n")
    return root


def make_thread(repo: Path, name: str, files: tuple[str, ...]) -> Path:
    d = repo / "kamma" / "threads" / name
    d.mkdir(parents=True)
    for f in files:
        (d / f).write_text(f"# {f}\n")
    return d


def quick(repo: Path, subcommand: str) -> int:
    return subprocess.run([sys.executable, str(GATE), subcommand], cwd=repo).returncode


# --- a repo that does not use kamma ----------------------------------------


def test_repo_without_kamma_is_untouched(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    stdout, rc = run_gate(
        tmp_path, "Write", {"file_path": str(tmp_path / "src" / "app.py")}
    )
    assert stdout == ""
    assert rc == 0


def test_shell_write_in_a_repo_without_kamma_is_untouched(tmp_path: Path) -> None:
    """The no-kamma bail must cover the Bash branch too, not just file edits."""
    stdout, rc = run_gate(tmp_path, "Bash", {"command": "gh label delete old-label"})
    assert stdout == ""
    assert rc == 0


# --- hole 1: an empty threads directory fails open -------------------------


def test_empty_threads_denies_a_write(repo: Path) -> None:
    """Starting work with no thread at all is the case the gate is named for."""
    stdout, rc = run_gate(repo, "Write", {"file_path": str(repo / "src" / "app.py")})
    assert rc == 0
    assert is_denied(stdout), "an empty threads directory must deny, not fail open"


def test_empty_threads_deny_message_names_both_escapes(repo: Path) -> None:
    """The message is user-facing contract: it has to say how to get unblocked."""
    stdout, _ = run_gate(repo, "Write", {"file_path": str(repo / "src" / "app.py")})
    reason = deny_reason(stdout)
    assert "/kamma:1-plan" in reason
    assert "/kamma:quick" in reason
    assert "kamma/" in reason


def test_incomplete_thread_deny_message_names_the_thread(repo: Path) -> None:
    make_thread(repo, "20260914_halfdone", ("spec.md",))
    stdout, _ = run_gate(repo, "Write", {"file_path": str(repo / "src" / "app.py")})
    reason = deny_reason(stdout)
    assert "20260914_halfdone" in reason
    assert "plan.md" in reason


# --- hole 2: shell commands are never checked ------------------------------


def test_shell_write_command_is_denied(repo: Path) -> None:
    """A destructive external write must be gated like a file edit."""
    make_thread(repo, "20260914_halfdone", ("spec.md",))
    stdout, rc = run_gate(repo, "Bash", {"command": "gh label delete old-label"})
    assert rc == 0
    assert is_denied(stdout), "a shell write command must be gated like a file edit"


# --- paired allow cases ----------------------------------------------------


def test_write_inside_kamma_is_allowed_when_threads_are_empty(repo: Path) -> None:
    """The gate must not deadlock: the agent has to be able to write the thread."""
    target = repo / "kamma" / "threads" / "20260921_new" / "spec.md"
    stdout, rc = run_gate(repo, "Write", {"file_path": str(target)})
    assert rc == 0
    assert stdout == "", "writing the thread that unblocks the gate must be allowed"


def test_file_edit_is_allowed_when_a_complete_thread_exists(repo: Path) -> None:
    make_thread(repo, "20260921_done", ("spec.md", "plan.md"))
    stdout, rc = run_gate(repo, "Write", {"file_path": str(repo / "src" / "app.py")})
    assert rc == 0
    assert stdout == ""


def test_shell_write_is_allowed_when_a_complete_thread_exists(repo: Path) -> None:
    make_thread(repo, "20260921_done", ("spec.md", "plan.md"))
    stdout, rc = run_gate(repo, "Bash", {"command": "gh label delete old-label"})
    assert rc == 0
    assert stdout == ""


def test_target_outside_the_repo_is_ignored(repo: Path, tmp_path: Path) -> None:
    outside = tmp_path / "somewhere-else.txt"
    stdout, rc = run_gate(repo, "Write", {"file_path": str(outside)})
    assert rc == 0
    assert stdout == ""


# --- path handling ---------------------------------------------------------


def test_a_relative_target_resolves_against_the_payload_cwd(repo: Path) -> None:
    stdout, _ = run_gate(repo, "Write", {"file_path": "src/app.py"})
    assert is_denied(stdout), "a relative path must be resolved, not skipped"


def test_a_relative_target_inside_kamma_is_allowed(repo: Path) -> None:
    stdout, _ = run_gate(repo, "Write", {"file_path": "kamma/threads/x/spec.md"})
    assert stdout == ""


def test_a_dotdot_escape_out_of_kamma_is_still_denied(repo: Path) -> None:
    stdout, _ = run_gate(repo, "Write", {"file_path": "kamma/../src/app.py"})
    assert is_denied(stdout), "a .. path must be judged on where it lands"


def test_notebook_path_is_read_like_a_file_path(repo: Path) -> None:
    stdout, _ = run_gate(
        repo, "NotebookEdit", {"notebook_path": str(repo / "src" / "nb.ipynb")}
    )
    assert is_denied(stdout), "NotebookEdit is in the matcher and must be gated"


# --- the shell denylist ----------------------------------------------------

WATCHED = [
    "gh issue create --title x",
    "gh issue edit 42 --add-label bug",
    "gh issue delete 42",
    "gh issue close 42",
    "gh issue reopen 42",
    "gh issue transfer 42 owner/other",
    "gh issue comment 42 --body hi",
    "gh label create nu --color ff0000",
    "gh label delete old-label",
    "gh label edit bug --description x",
    "gh label clone owner/other",
    "gh pr create --fill",
    "gh pr merge 7 --squash",
    "gh pr close 7",
    "gh pr edit 7 --title x",
    "gh pr review 7 --approve",
    "gh release create v1.0",
    "gh release delete v1.0",
    "gh release upload v1.0 dist/app.zip",
    "gh repo create owner/repo",
    "gh repo delete owner/repo",
    "gh repo rename newname",
    "gh project item-create 1 --title x",
    "gh project item-edit --id X --field-id Y",
    "gh project field-create 1 --name Priority",
    "gh project item-delete 1 --id X",
    "gh secret set TOKEN",
    "gh variable delete FOO",
    "gh gist create notes.md",
    "gh workflow run deploy.yml",
    "gh run cancel 12345",
    "gh cache delete abc",
    "gh alias set co 'pr checkout'",
    # -X with and without a space, and the --method=VALUE spelling.
    "gh api -X DELETE repos/owner/repo/labels/bug",
    "gh api -XDELETE repos/owner/repo/labels/bug",
    "gh api --method POST repos/owner/repo/issues",
    "gh api --method=POST repos/owner/repo/issues",
    "gh api repos/owner/repo/issues -f title=hello",
    "gh api graphql -f query='mutation { addLabel { id } }'",
    "gh api graphql --input mutation-body.json",
    "gh api graphql -F query=@body.graphql",
    # A long command split across lines with a trailing backslash.
    "gh api \\\n  -X DELETE repos/owner/repo/labels/bug",
    "curl -X POST https://example.com/api",
    "curl -XPOST https://example.com/api",
    "curl --request DELETE https://example.com/api",
    "curl --request=DELETE https://example.com/api",
    # curl POSTs for these with no -X at all.
    "curl -d name=x https://example.com/api",
    "curl --data-binary @body.json https://example.com/api",
    "curl --data-urlencode a=b https://example.com/api",
    "curl -F file=@x.png https://example.com/upload",
    "curl --form file=@x.png https://example.com/upload",
    "curl -T file.txt https://example.com/upload",
    "curl --upload-file f https://example.com/x",
    "git push --force origin main",
    "git push -f",
    "git push --delete origin oldbranch",
    "npm publish",
    "uv publish",
    "cargo publish",
    "twine upload dist/*",
]

NOT_WATCHED = [
    "gh issue list",
    "gh issue view 42",
    "gh label list",
    "gh pr view 7",
    "gh pr list --state open",
    "gh release list",
    "gh repo view",
    "gh run list",
    "gh workflow list",
    "gh api repos/owner/repo/labels",
    "gh api /repos/owner/repo --jq .name",
    # A read-only call whose OUTPUT is piped into something using -F.
    "gh api repos/owner/repo/issues | grep -F bug",
    "gh api graphql -f query='query { viewer { login } }'",
    # curl -f is --fail and -t is a telnet option; neither writes.
    "curl -f https://example.com/read.json",
    "curl https://example.com/x",
    "curl -s -o out.json https://example.com/x",
    "git push origin main",
    "git status --short",
    "git log --oneline -5",
    "ls -la",
    "cat README.md",
    "grep -rn foo src/",
    "just test",
    "uv run pytest",
]


@pytest.mark.parametrize("command", WATCHED)
def test_watched_shell_commands_are_denied(repo: Path, command: str) -> None:
    stdout, rc = run_gate(repo, "Bash", {"command": command})
    assert rc == 0
    assert is_denied(stdout), f"expected the gate to watch: {command}"


@pytest.mark.parametrize("command", NOT_WATCHED)
def test_read_only_shell_commands_are_ignored(repo: Path, command: str) -> None:
    stdout, rc = run_gate(repo, "Bash", {"command": command})
    assert rc == 0
    assert stdout == "", f"the gate must stay silent on: {command}"


# --- the /kamma:quick exemption --------------------------------------------


def test_quick_marker_suppresses_the_deny(repo: Path) -> None:
    assert quick(repo, "quick-on") == 0
    try:
        stdout, rc = run_gate(
            repo, "Write", {"file_path": str(repo / "src" / "app.py")}
        )
        assert rc == 0
        assert stdout == "", "/kamma:quick is the no-spec path and is never gated"
        stdout, _ = run_gate(repo, "Bash", {"command": "gh label delete old-label"})
        assert stdout == "", "/kamma:quick is never gated for shell writes either"
    finally:
        quick(repo, "quick-off")


def test_quick_off_restores_the_deny(repo: Path) -> None:
    try:
        quick(repo, "quick-on")
        quick(repo, "quick-off")
        stdout, _ = run_gate(repo, "Write", {"file_path": str(repo / "src" / "app.py")})
        assert is_denied(stdout)
    finally:
        quick(repo, "quick-off")


def test_quick_marker_does_not_leak_to_another_session(repo: Path) -> None:
    """Two agents share one tree. One session's quick run must not ungate the other."""
    assert quick(repo, "quick-on") == 0
    try:
        stdout, _ = run_gate(
            repo,
            "Write",
            {"file_path": str(repo / "src" / "app.py")},
            session_id="a-different-session",
        )
        assert is_denied(stdout), (
            "the exemption must be scoped to the session that set it"
        )
    finally:
        quick(repo, "quick-off")


def test_quick_on_from_a_subdirectory_still_marks_the_repo(repo: Path) -> None:
    """quick-on walks up to the repo root, so it cannot orphan its own marker."""
    assert quick(repo / "src", "quick-on") == 0
    try:
        stdout, _ = run_gate(repo, "Write", {"file_path": str(repo / "src" / "app.py")})
        assert stdout == ""
    finally:
        quick(repo / "src", "quick-off")


def test_an_expired_quick_marker_does_not_suppress_the_deny(repo: Path) -> None:
    assert quick(repo, "quick-on") == 0
    try:
        sys.path.insert(0, str(REPO_ROOT / "hooks"))
        try:
            import kamma_gate

            marker = kamma_gate.quick_marker_path(repo.resolve(), SESSION)
            assert marker.is_file()
            stale = marker.stat().st_mtime - (kamma_gate.QUICK_MARKER_TTL_SECONDS + 60)
            os.utime(marker, (stale, stale))
        finally:
            sys.path.pop(0)
        stdout, _ = run_gate(repo, "Write", {"file_path": str(repo / "src" / "app.py")})
        assert is_denied(stdout), "an abandoned quick run must not disable the gate"
    finally:
        quick(repo, "quick-off")


# --- the hook must never raise ---------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "not json at all",
        "[1, 2, 3]",
        '"a string"',
        "{}",
        '{"cwd": "/definitely/does/not/exist"}',
    ],
)
def test_malformed_input_exits_quietly(raw: str) -> None:
    stdout, rc = run_gate_raw(raw)
    assert rc == 0
    assert stdout == ""


def test_missing_tool_input_exits_quietly(repo: Path) -> None:
    stdout, rc = run_gate_raw(json.dumps({"cwd": str(repo), "tool_name": "Write"}))
    assert rc == 0
    assert stdout == ""


def test_bash_payload_with_no_command_exits_quietly(repo: Path) -> None:
    stdout, rc = run_gate(repo, "Bash", {})
    assert rc == 0
    assert stdout == ""


def test_tool_input_of_the_wrong_type_exits_quietly(repo: Path) -> None:
    stdout, rc = run_gate_raw(
        json.dumps({"cwd": str(repo), "tool_name": "Bash", "tool_input": "oops"})
    )
    assert rc == 0
    assert stdout == ""


def test_a_huge_command_does_not_hang_the_gate(repo: Path) -> None:
    """The patterns must stay linear — a hook that hangs blocks the tool call."""
    import time

    command = "gh api graphql " + ("x" * 2_000_000)
    started = time.monotonic()
    stdout, rc = run_gate(repo, "Bash", {"command": command})
    assert time.monotonic() - started < 10
    assert rc == 0
    assert stdout == ""


# --- heredoc bodies are data, not commands ---------------------------------

HEREDOC_ALLOWED = [
    # A commit message that merely names a watched command. This blocked real
    # commits before the fix.
    "git commit -F - <<'MSGEOF'\nfix: the gate\n- covers gh, curl and git push --force\nMSGEOF\n",
    # Writing a document that quotes a watched command.
    "cat > notes.md <<'EOF'\nrun gh label delete old-label\nEOF\n",
    "cat > notes.md <<EOF\ngh issue edit 42 --add-label bug\nEOF\n",
    "cat > notes.md <<-EOF\nnpm publish\n\tEOF\n",
    # A double-quoted delimiter, with a watched command quoted in the body.
    'cat > body.md <<"END"\ncurl -X POST https://x/y\nEND\n',
]

HEREDOC_DENIED = [
    # `<<` as a left shift is not a heredoc, so what follows is still scanned.
    "python3 -c 'x = 1 << 2' ; gh label delete old-label",
    # A watched command before a heredoc.
    "gh label delete old-label && cat > n.md <<'EOF'\nhi\nEOF\n",
    # A watched command after the heredoc terminator.
    "cat > n.md <<'EOF'\nhi\nEOF\ngh label delete old-label",
    # The heredoc body is ignored, but the command feeding it is a write in its
    # own right and is still denied.
    'gh issue comment 1 --body-file - <<"END"\nhello\nEND\n',
]


@pytest.mark.parametrize("command", HEREDOC_ALLOWED)
def test_a_heredoc_body_is_not_scanned(repo: Path, command: str) -> None:
    stdout, rc = run_gate(repo, "Bash", {"command": command})
    assert rc == 0
    assert stdout == "", f"a heredoc body is data, not a command: {command!r}"


@pytest.mark.parametrize("command", HEREDOC_DENIED)
def test_commands_around_a_heredoc_are_still_scanned(repo: Path, command: str) -> None:
    stdout, rc = run_gate(repo, "Bash", {"command": command})
    assert rc == 0
    assert is_denied(stdout), f"expected the gate to watch: {command!r}"
