#!/usr/bin/env python3
"""Kamma Claude Code hooks: spec-gate (PreToolUse) and stop-gate (Stop).

Repo-agnostic: reads `cwd` from stdin and checks that directory for a kamma/
setup. Exits 0 silently wherever kamma is not in use. Never raises — a hook
that crashes must not turn into a blocked tool call.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

LOOP_MARKER = "> **Thread type:** Loop (standing thread)"


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
        thread_dirs = [d for d in threads_dir.iterdir() if d.is_dir()]
    except Exception:
        return
    if not thread_dirs:
        return

    tool_input = payload.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        # Can't determine what's being edited — fail open rather than crash.
        return
    try:
        resolved_target = Path(target)
        if not resolved_target.is_absolute():
            resolved_target = repo / resolved_target
        resolved_target = resolved_target.resolve()
        resolved_repo = repo.resolve()
        resolved_kamma = kamma_dir.resolve()
    except Exception:
        return

    if (
        resolved_target != resolved_repo
        and resolved_repo not in resolved_target.parents
    ):
        # Target isn't inside this repo at all — the gate governs this repo's
        # kamma threads, not unrelated files elsewhere on disk.
        return
    if resolved_target == resolved_kamma or resolved_kamma in resolved_target.parents:
        return

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
    except SystemExit:
        raise
    except Exception:
        return


if __name__ == "__main__":
    main()
