# Kamma

A lightweight plan-do-review process for your CLI agents.

## Supported Tools

Claude Code, Gemini CLI, Antigravity, OpenCode, Kilo Code, Codex CLI

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

# With bash
./sync.sh
```

The sync tool detects which AI CLIs are installed on your machine and copies the prompts to each one. Unsupported or missing tools are skipped.

## Commands

| Command | Description |
|---------|-------------|
| `/kamma:0-setup` | Scaffold a project with project.md, tech.md, workflow.md |
| `/kamma:1-plan` | Create a new thread (feature, bug fix, chore) with spec + plan |
| `/kamma:2-do` | Work through the selected thread until it is ready to review |
| `/kamma:3-review` | Review finished work, ideally in a fresh tool or session |
| `/kamma:4-finalize` | Finish a reviewed thread, update docs, and clean up |
| `/kamma:5-status` | Show where things stand across all threads |
| `/kamma:one-shot` | Plan, implement, review, and finalize a thread in a single run |

## Workflow

### Standard

1. `/kamma:0-setup` — initialize Kamma in your project
2. `/kamma:1-plan` — create a thread spec and implementation plan
3. `/kamma:2-do` — implement until ready for review
4. `/kamma:3-review` — review, ideally in a fresh session or different tool
5. `/kamma:4-finalize` — mark complete, update docs, clean up

### One-shot

`/kamma:one-shot` runs the full cycle in a single session. It stops twice: to confirm the plan, and to ask you to test. If testing passes, it reviews and finalizes automatically.

---

*Kamma* is a Pāḷi word for action, work, doing.

Inspired by [Conductor](https://github.com/fcoury/conductor).
