# Kamma — Agent Guide

Kamma is a lightweight plan-do-review-finalize process for CLI coding agents. This
repo *is* the framework: it ships the command prompts and a sync tool that installs
them into whichever AI CLIs are present (Claude Code, Antigravity, Codex, Qwen, etc.).

## Repo layout

- `commands/` — the source of truth for the prompts. `kamma.md` is the full single-run
  cycle; `0-setup`, `1-plan`, `2-do`, `3-review`, `4-finalize`, `5-status`,
  `handoff`, and `improve` are the individual steps. `improve` is the cross-repo
  self-improvement loop: it reads every repo's `kamma/lessons.md` and consolidates
  recurring mistakes into the framework prompts.
- `scripts/sync.py` — detects installed CLIs and copies `commands/` + `registration/`
  into each tool's config dir. It copies (never symlinks) and skips missing tools.
- `registration/` — per-tool registration files (`QWEN.md`, the
  `*-extension.json` / `*-plugin.json` manifests). These are tracked sources consumed
  by `sync.py` — don't confuse them with the root-level agent files.
- `skills/kamma/SKILL.md` — the skill packaging of the same workflow.
- `templates/workflow.md` — the workflow template `0-setup` writes into a project.
- `kammika/` — local `uv` tool package.
- `install.sh` / `install.ps1` — bootstrap installers.

## Working on the prompts

The commands are prompts, not code — edit the markdown in `commands/` directly. After
editing, propagate to installed tools:

```bash
just sync            # uv run python scripts/sync.py
just kammika-rebuild # reinstall the local kammika package
```

There is no real test suite; verification is reading the prompts for consistency
(section numbering, cross-references, no broken instructions). **Always verify
that adding new sections or gated blocks doesn't break list numbering or internal
heading references.**

## Conventions

- `AGENTS.md` is the tracked master agent file. `CLAUDE.md`, `GEMINI.md`, and `QWEN.md`
  at the repo root are gitignored symlinks pointing here.
- This repo dogfoods Kamma; the working `kamma/` directory is gitignored.
- Don't commit, push, or run git unless explicitly asked.
