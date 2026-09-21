# Kamma — Agent Guide

Kamma is a lightweight plan-do-review-finalize process for CLI coding agents. This
repo *is* the framework: it ships the command prompts and a sync tool that installs
them into whichever AI CLIs are present (Claude Code, Antigravity, Codex, Qwen, etc.).

## Repo layout

- `commands/` — the source of truth for the prompts. `kamma.md` is the full single-run
  cycle and `quick` is the same run without spec or plan files; `0-setup`,
  `1-plan`, `loop`, `2-do`, `3-review`, `4-finalize`, `handoff`, and `improve`
  are the individual steps. `improve` is the cross-repo
  self-improvement loop: it reads every repo's `kamma/lessons.md` and consolidates
  recurring mistakes into the framework prompts.
- `scripts/sync.py` — detects installed CLIs and installs `commands/`,
  `registration/`, `skills/`, `templates/` and `hooks/` into each tool's config dir.
  It copies (never symlinks) and skips missing tools. It also *removes*: each
  target sweeps its own kamma files before writing, so a command deleted from
  `commands/` disappears on the next sync.
- `hooks/kamma_gate.py` — the Claude Code enforcement hooks. `sync.py` copies this
  in and merges two entries into Claude Code's `settings.json`. No other tool has
  an equivalent yet.
- `registration/` — per-tool registration files (`QWEN.md`, the
  `*-extension.json` / `*-plugin.json` manifests). These are tracked sources consumed
  by `sync.py` — don't confuse them with the root-level agent files.
- `skills/kamma/SKILL.md` — the skill packaging of the same workflow.
- `templates/workflow.md` — the workflow template `0-setup` writes into a project.
- `install.sh` / `install.ps1` — bootstrap installers.

## Working on the prompts

The commands are prompts, not code — edit the markdown in `commands/` directly. After
editing, propagate to installed tools:

```bash
just sync            # uv run python scripts/sync.py
```

There is no real test suite; verification is reading the prompts for consistency
(section numbering, cross-references, no broken instructions). **Always verify
that adding new sections or gated blocks doesn't break list numbering or internal
heading references.**

## Keeping the docs true to the code

Four files make claims about what the sync tool supports, and all four have drifted
before: `README.md` (supported-tools line and the command table), `AGENTS.md` (this
repo-layout list), `kamma/tech.md` (the config-root table) and
`skills/kamma/SKILL.md` (its command list). After changing `commands/` or
`get_targets()`, check every command in `commands/` appears in the README table and
in this file, and that the tech table matches `get_targets()` exactly. A tool or
command listed in a doc but absent from the code reads as real to everyone after you.

## Conventions

- `AGENTS.md` is the tracked master agent file. `CLAUDE.md`, `GEMINI.md`, and `QWEN.md`
  at the repo root are gitignored symlinks pointing here.
- This repo dogfoods Kamma; the working `kamma/` directory is gitignored.
- Don't commit, push, or run git unless explicitly asked.

## Before opening an issue or PR against this repo

Read `skills/kamma/SKILL.md` and the specific file(s) in `commands/` your bug touches,
in full, before proposing a fix — a symptom in one command is often caused by a step
skipped or misdocumented elsewhere, and a patch that only addresses the symptom can
bake a wrong assumption into the framework permanently. Check whether the root cause
is elsewhere first. Prefer opening an issue over a PR unless the fix is a one-line,
obviously-correct change — file the issue using the bug report template, which asks
for the root cause, not just the symptom.
