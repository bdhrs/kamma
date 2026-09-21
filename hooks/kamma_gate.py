#!/usr/bin/env python3
"""Kamma Claude Code hooks: spec-gate (PreToolUse) and stop-gate (Stop).

Repo-agnostic: reads `cwd` from stdin and checks that directory for a kamma/
setup. Exits 0 silently wherever kamma is not in use. Never raises — a hook
that crashes must not turn into a blocked tool call.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

LOOP_MARKER = "> **Thread type:** Loop (standing thread)"

# A /kamma:quick run marks itself here. The marker expires so an abandoned run
# cannot leave the gate switched off forever.
QUICK_MARKER_TTL_SECONDS = 4 * 60 * 60

# Used when the host exposes no session id to the shell.
SHARED_SESSION_KEY = "shared"

# Shell commands that write to a live external system. The gate treats these
# like a file edit. Read-only commands (`gh issue list`, `gh api` with no write
# flag) deliberately match nothing. This list is a treadmill and is meant to be
# extended rather than made clever.
_GH_WRITE_SUBCOMMANDS = (
    r"issue\s+(create|edit|delete|close|reopen|transfer|comment|lock|unlock|pin|unpin)",
    r"label\s+(create|delete|edit|clone)",
    r"pr\s+(create|merge|close|edit|reopen|comment|review|ready)",
    r"release\s+(create|delete|edit|upload)",
    r"repo\s+(create|delete|rename|edit|fork|archive|unarchive)",
    r"project\s+(create|delete|edit|close|copy|link|unlink"
    r"|item-create|item-edit|item-delete|item-archive"
    r"|field-create|field-delete)",
    r"secret\s+(set|delete)",
    r"variable\s+(set|delete)",
    r"gist\s+(create|delete|edit|rename|clone)",
    r"workflow\s+(run|enable|disable)",
    r"run\s+(cancel|rerun|delete)",
    r"cache\s+delete",
    r"alias\s+(set|delete)",
)

# Most patterns ignore case. The curl ones below must not: curl's `-f` is
# --fail (read-only) while `-F` is --form (a write), and `-t` is a telnet
# option while `-T` is --upload-file.
_CASE_INSENSITIVE_PATTERNS = (
    *(rf"\bgh\s+{sub}\b" for sub in _GH_WRITE_SUBCOMMANDS),
    # `-X DELETE`, `-XDELETE` and `--method=POST` are all the same command.
    r"\bgh\s+api\b[^\n]*?(-X|--method)\s*=?\s*(POST|PATCH|PUT|DELETE)\b",
    r"\bgh\s+api\s+graphql\b[\s\S]*\bmutation\b",
    # A graphql body read from a file never contains the word `mutation` in the
    # command text, so watch the file-input shapes outright.
    r"\bgh\s+api\s+graphql\b[^\n]*(--input\b|=@)",
    # `gh api <endpoint> -f k=v` implies POST. Graphql is excluded because a
    # read-only query passes its text through -f too, and a graphql mutation is
    # caught above. `[^\n|]*` stops the match crossing a pipe, so a read-only
    # `gh api ... | grep -F x` is not mistaken for a write.
    r"\bgh\s+api\b(?![^\n|]*\bgraphql\b)[^\n|]*\s--?(f|F|field|raw-field|input)\b",
    r"\bcurl\b[^\n]*?(-X|--request)\s*=?\s*(POST|PATCH|PUT|DELETE)\b",
    r"\bgit\s+push\b[^\n]*\s(--force|--force-with-lease|-f|--delete)\b",
    r"\bnpm\s+publish\b",
    r"\buv\s+publish\b",
    r"\bcargo\s+publish\b",
    r"\btwine\s+upload\b",
)

# curl sends POST or PUT for these with no -X at all.
_CASE_SENSITIVE_PATTERNS = (
    r"\bcurl\b[^\n]*?\s"
    r"(-d|--data|--data-raw|--data-binary|--data-urlencode"
    r"|-F|--form|--form-string|-T|--upload-file)\b",
)

BASH_WRITE_PATTERNS = tuple(
    [re.compile(p, re.IGNORECASE) for p in _CASE_INSENSITIVE_PATTERNS]
    + [re.compile(p) for p in _CASE_SENSITIVE_PATTERNS]
)


def read_stdin_json() -> dict:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def is_loop_thread(thread_dir: Path) -> bool:
    if (thread_dir / "cycles").is_dir():
        return True
    for name in ("spec.md", "plan.md"):
        f = thread_dir / name
        if f.is_file():
            try:
                if LOOP_MARKER in f.read_text(encoding="utf-8", errors="ignore"):
                    return True
            except Exception:
                pass
    return False


# `<<EOF`, `<<-EOF`, `<<'EOF'`, `<<"EOF"`. The delimiter must start with a
# letter or underscore, so a left-shift such as `1 << 2` is not mistaken for one.
_HEREDOC_START = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_]\w*)\1")


def strip_heredoc_bodies(text: str) -> str:
    """Remove heredoc bodies before matching.

    A heredoc body is data, not commands: it is the commit message, the issue
    body, the file being written. Those routinely name the very commands this
    gate watches, and matching inside one blocks ordinary work. The trade is
    that piping a body straight into a shell bypasses the gate; that sits with
    the escape hatches already recorded in the thread spec.
    """
    lines = text.split("\n")
    kept = []
    i = 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        match = _HEREDOC_START.search(line)
        if not match:
            continue
        delimiter = match.group(2)
        while i < len(lines) and lines[i].strip() != delimiter:
            i += 1
        if i < len(lines):
            kept.append(lines[i])
            i += 1
    return "\n".join(kept)


def is_write_command(command: str) -> bool:
    """True when a shell command writes to a live external system."""
    if not isinstance(command, str):
        return False
    # A long command is routinely split across lines with a trailing backslash.
    # The patterns are single-line, so fold the continuations back first.
    folded = re.sub(r"\\\s*\n\s*", " ", strip_heredoc_bodies(command))
    return any(p.search(folded) for p in BASH_WRITE_PATTERNS)


def find_repo_root(start: Path) -> Path:
    """Nearest ancestor holding a kamma/ directory, else `start` itself.

    `quick-on` may be run from a subdirectory. Keying the marker off the raw cwd
    would write it under a hash the gate never looks up, leaving an orphan in the
    cache and no exemption at all.
    """
    try:
        current = start.resolve()
    except Exception:
        return start
    for candidate in (current, *current.parents):
        if (candidate / "kamma").is_dir():
            return candidate
    return current


def quick_marker_path(repo: Path, session_id: str) -> Path:
    """Marker for an active /kamma:quick run, keyed by repo *and* session.

    Scoping to the session matters: two agents routinely share one working tree,
    and a repo-wide marker would let one session's quick run switch the gate off
    for the other, or clear an exemption it did not set.
    """
    key = hashlib.sha256(f"{repo}:{session_id}".encode()).hexdigest()[:32]
    return Path.home() / ".cache" / "kamma" / f"quick-{key}"


def marker_is_live(marker: Path) -> bool:
    try:
        if not marker.is_file():
            return False
        return (time.time() - marker.stat().st_mtime) < QUICK_MARKER_TTL_SECONDS
    except Exception:
        return False


def quick_mode_active(repo: Path, session_id: str) -> bool:
    if session_id and marker_is_live(quick_marker_path(repo, session_id)):
        return True
    # Fallback for a host that does not expose a session id to the shell. Such a
    # marker is repo-wide, so it is deliberately the second choice.
    return marker_is_live(quick_marker_path(repo, SHARED_SESSION_KEY))


def shell_session_id() -> str:
    return os.environ.get("CLAUDE_CODE_SESSION_ID", "") or SHARED_SESSION_KEY


def quick_on() -> None:
    try:
        marker = quick_marker_path(find_repo_root(Path.cwd()), shell_session_id())
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("quick\n", encoding="utf-8")
    except Exception:
        return


def quick_off() -> None:
    try:
        repo = find_repo_root(Path.cwd())
        quick_marker_path(repo, shell_session_id()).unlink(missing_ok=True)
    except Exception:
        return


def spec_gate() -> None:
    payload = read_stdin_json()
    cwd = payload.get("cwd")
    if not cwd:
        return
    repo = Path(cwd)
    if not repo.is_dir():
        return

    kamma_dir = repo / "kamma"
    threads_dir = kamma_dir / "threads"
    if not kamma_dir.is_dir() or not threads_dir.is_dir():
        return

    try:
        resolved_repo = repo.resolve()
        resolved_kamma = kamma_dir.resolve()
    except Exception:
        return

    # /kamma:quick is the no-spec path by design. It is never gated.
    if quick_mode_active(resolved_repo, payload.get("session_id") or ""):
        return

    tool_name = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return

    if tool_name == "Bash":
        if not is_write_command(tool_input.get("command") or ""):
            return
    else:
        target = tool_input.get("file_path") or tool_input.get("notebook_path")
        if not target:
            # Can't determine what's being edited — fail open rather than crash.
            return
        try:
            resolved_target = Path(target)
            if not resolved_target.is_absolute():
                resolved_target = repo / resolved_target
            resolved_target = resolved_target.resolve()
        except Exception:
            return

        if (
            resolved_target != resolved_repo
            and resolved_repo not in resolved_target.parents
        ):
            # Target isn't inside this repo at all — the gate governs this repo's
            # kamma threads, not unrelated files elsewhere on disk.
            return
        if (
            resolved_target == resolved_kamma
            or resolved_kamma in resolved_target.parents
        ):
            return

    try:
        thread_dirs = [d for d in threads_dir.iterdir() if d.is_dir()]
    except Exception:
        return

    if not thread_dirs:
        deny(
            "Kamma spec gate: this repo uses kamma but has no thread in "
            "kamma/threads/. Starting work with no thread is not allowed. Run "
            "/kamma:1-plan to create a thread, or /kamma:quick for a small "
            "self-contained change. Edits inside kamma/ are always allowed."
        )

    incomplete = []
    for d in thread_dirs:
        missing = [f for f in ("spec.md", "plan.md") if not (d / f).is_file()]
        if missing:
            incomplete.append((d.name, missing))

    if not incomplete:
        return

    name, missing = incomplete[0]
    deny(
        f"Kamma spec gate: thread 'kamma/threads/{name}' is missing "
        f"{', '.join(missing)}. Write the missing file(s) under kamma/threads/{name}/, "
        f"or delete the thread directory if it was abandoned, to unblock editing. "
        f"Edits inside kamma/ are always allowed."
    )


def has_unticked_tasks(text: str) -> bool:
    return bool(re.search(r"^\s*-\s*\[[ ~]\]", text, re.MULTILINE))


def has_ticked_tasks(text: str) -> bool:
    return bool(re.search(r"^\s*-\s*\[x\]", text, re.MULTILINE | re.IGNORECASE))


def marker_path(session_id: str, thread_name: str) -> Path:
    key = hashlib.sha256(f"{session_id}:{thread_name}".encode()).hexdigest()[:32]
    return Path.home() / ".cache" / "kamma" / f"stop-nag-{key}"


def stop_gate() -> None:
    payload = read_stdin_json()
    cwd = payload.get("cwd")
    session_id = payload.get("session_id")
    if not cwd or not session_id:
        return
    repo = Path(cwd)
    threads_dir = repo / "kamma" / "threads"
    if not threads_dir.is_dir():
        return

    try:
        thread_dirs = [d for d in threads_dir.iterdir() if d.is_dir()]
    except Exception:
        return

    newly_flagged = []
    for d in thread_dirs:
        if is_loop_thread(d):
            continue
        if (d / "review.md").is_file():
            continue
        plan = d / "plan.md"
        if not plan.is_file():
            continue
        try:
            text = plan.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if not has_ticked_tasks(text):
            continue
        if has_unticked_tasks(text):
            continue

        mp = marker_path(session_id, d.name)
        if mp.exists():
            continue
        newly_flagged.append((d.name, mp))

    if not newly_flagged:
        return

    for _, mp in newly_flagged:
        try:
            mp.parent.mkdir(parents=True, exist_ok=True)
            mp.write_text("nagged\n", encoding="utf-8")
        except Exception:
            pass

    names = ", ".join(name for name, _ in newly_flagged)
    print(
        f"Kamma completion gate: thread(s) {names} are fully checked off but have no "
        f"review.md. Run /kamma:3-review before finishing.",
        file=sys.stderr,
    )
    sys.exit(2)


def main() -> None:
    try:
        cmd = sys.argv[1] if len(sys.argv) > 1 else ""
        if cmd == "spec-gate":
            spec_gate()
        elif cmd == "stop-gate":
            stop_gate()
        elif cmd == "quick-on":
            quick_on()
        elif cmd == "quick-off":
            quick_off()
    except SystemExit:
        raise
    except Exception:
        return


if __name__ == "__main__":
    main()
