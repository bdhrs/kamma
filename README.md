# Kamma

Lightweight, cross-tool planning and tracking for AI coding CLIs.

## Install

```bash
git clone https://github.com/bdhrs/kamma.git
cd kamma
```

Then sync Kamma to your installed AI tools:

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

`/kamma:one-shot` runs the full cycle in a single session. It stops three times: to confirm the plan, to ask you to test, and to confirm before finalizing.

## Supported Tools

Claude Code, Gemini CLI, Antigravity, OpenCode, Kilo Code, Codex CLI

---

*Kamma* is a Pāḷi word for action, work, doing.

Inspired by [Conductor](https://github.com/fcoury/conductor).
