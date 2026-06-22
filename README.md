# Kamma

A lightweight plan-do-review-finalize process for your CLI agents.

## Supported Tools

Claude Code, Antigravity (IDE + `agy` CLI), OpenCode, Kilo Code, Codex CLI, Qwen Code

> **Gemini CLI** was removed — Google is sunsetting it for consumer tiers (free,
> Google AI Pro/Ultra) on 18 June 2026 in favour of Antigravity; Standard and
> Enterprise subscriptions continue past that date. Install
> [Antigravity](https://antigravity.google) (or the `agy` CLI) and Kamma syncs to it
> automatically.

## Quick Install

**Mac/Linux:**
```bash
curl -sSL https://raw.githubusercontent.com/bdhrs/kamma/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/bdhrs/kamma/main/install.ps1 | iex
```

Downloads the latest version to `~/kamma` and syncs to all installed AI tools. Re-run any time to update.

Requires [uv](https://docs.astral.sh/uv/). The script will offer to install it if missing.

## Manual Install

```bash
git clone https://github.com/bdhrs/kamma.git
cd kamma
```

Then sync:

```bash
# With just
just sync

# Reinstall the local kammika CLI after changes
just kammika-rebuild

# With bash
./sync.sh
```

`just kammika-rebuild` reinstalls the local `kammika` package while allowing `uv` to reuse cached dependencies.

The sync tool detects which AI CLIs are installed on your machine and copies the prompts to each one. Unsupported or missing tools are skipped.

## Commands

| Command | Description |
|---------|-------------|
| `/kamma` | Plan, do, review, and finalize a thread in a single run |
| `/kamma:quick` | Same single run for a small change — no spec or plan files |
  | `/kamma:0-setup` | Scaffold a project with project.md, tech.md, workflow.md |
| `/kamma:1-plan` | Create a new thread (feature, bug fix, chore) with spec + plan |
| `/kamma:2-do` | Work through the selected thread until it is ready to review |
| `/kamma:3-review` | Review finished work, ideally in a fresh tool or session |
| `/kamma:4-finalize` | Finish a reviewed thread, update docs, and clean up |
| `/kamma:5-status` | Show where things stand across all threads |
| `/kamma:improve` | Consolidate recurring lessons across repos into kamma framework improvements |


## Workflow

### Standard

1. `/kamma:0-setup` — initialize Kamma in your project
2. `/kamma:1-plan` — create a thread spec and implementation plan
3. `/kamma:2-do` — implement until ready for review
4. `/kamma:3-review` — review, ideally in a fresh session or different tool
5. `/kamma:4-finalize` — mark complete, update docs, clean up

### /kamma

`/kamma` runs the full cycle in a single session. It stops twice: to confirm the plan, and to ask you to test. If testing passes, it reviews and finalizes automatically.

### /kamma:quick

`/kamma:quick` is the lightweight sibling for small, self-contained changes. It runs the same single session with the same two stops, review, detailed commit message, and reflect step — but skips the `spec.md`/`plan.md` files and thread directory. Reach for it when the change fits in your head; use `/kamma` when it needs a durable spec or spans multiple phases.

### Antigravity

Antigravity is served two ways, and a single `just sync` installs both (detected when
`~/.gemini/antigravity` or `~/.gemini/antigravity-cli` exists):

- **Skills** → `~/.gemini/skills/`. Read by both the Antigravity IDE and the `agy` CLI
  (whose `/` menu lists skills). `kamma/` is the full single-run cycle; each step is its
  own skill (`kamma-1-plan/`, `kamma-2-do/`, …), so they show up as `/kamma`,
  `/kamma-1-plan`, `/kamma-3-review`, … and auto-activate semantically.
- **Workflows** → `~/.gemini/antigravity/global_workflows/`. The same `/kamma-*` slash
  commands for the IDE (the `agy` CLI uses skills, not workflows).

All paths live under `~/.gemini` on macOS, Linux, and Windows (`%USERPROFILE%\.gemini`).

## Development

If you are contributing to Kamma, please install the pre-commit hooks to ensure code quality:

```bash
uv tool install pre-commit
pre-commit install
```

The hooks run Ruff (lint + format) and Pyright on staged Python files. Both tools
are pinned in `kammika`'s dev dependencies and run via `uv run --project kammika`,
so the same versions are used everywhere.

---

*Kamma* is a Pāḷi word for action, work, doing.

Inspired by [Conductor](https://github.com/fcoury/conductor).
