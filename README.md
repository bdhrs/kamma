# Kamma

Lightweight, cross-tool workflow management for AI coding CLIs.

*Kamma* a Pāḷi word for action, work, doing.

## Commands

| Command | Description |
|---------|-------------|
| `/kamma:0-setup` | Scaffold a project with project.md, tech-stack.md, workflow.md |
| `/kamma:1-plan` | Create a new thread (feature, bug fix, chore) with spec + plan |
| `/kamma:2-do` | Implement the selected thread until it is ready for independent review |
| `/kamma:3-review` | Review an implemented thread with an independent agent or tool |
| `/kamma:4-finalize` | Mark a reviewed thread complete, sync docs, and handle cleanup |
| `/kamma:5-status` | Show progress overview of all threads |

## Supported Tools

| Tool | Format | Invocation |
|------|--------|------------|
| Claude Code | TOML commands + plugin.json | `/kamma:0-setup` |
| Gemini CLI | TOML commands + gemini-extension.json | `/kamma:0-setup` |
| Antigravity | Global workflows | `/kamma-0-setup` |
| OpenCode | MD with frontmatter | `/kamma-0-setup` |
| Kilo CLI | Skills (SKILL.md) | Skill-based activation |
| Codex CLI | Plain MD prompts | `$kamma-0-setup` |

## Project Structure

```
kamma/
├── commands/               # Source prompts (single source of truth)
│   ├── 0-setup.md
│   ├── 1-plan.md
│   ├── 2-do.md
│   ├── 3-review.md
│   ├── 4-finalize.md
│   └── 5-status.md
├── registration/           # Tool registration files
│   ├── claude-plugin.json
│   ├── gemini-extension.json
│   └── GEMINI.md
├── skills/
│   └── kamma/
│       └── SKILL.md        # Auto-activation skill
├── templates/
│   └── workflow.md         # Default workflow template
├── sync.sh                # Thin shell wrapper around the uv sync tool
├── pyproject.toml         # uv project metadata for the sync tool
├── scripts/
│   └── sync.py            # Sync implementation
└── README.md
```

## Quick Start

```bash
# 1. Sync Kamma to your installed AI tools
./sync.sh

# 2. In any project, initialize Kamma
/kamma:0-setup

# 3. Plan a feature — creates spec.md and plan.md
/kamma:1-plan "Add user authentication"

# 4. Implement the thread
/kamma:2-do

# 5. Review with a different agent (recommended)
/kamma:3-review

# 6. Finalize — mark complete, sync docs, cleanup
/kamma:4-finalize
```

## Usage

### Workflow

Kamma now follows a four-step execution flow for each thread:

1. `/kamma:1-plan` creates the thread spec and implementation plan.
2. `/kamma:2-do` implements the thread and stops at review handoff.
3. `/kamma:3-review` performs structured review, ideally with a different agent or tool.
4. `/kamma:4-finalize` marks the thread complete, syncs docs, and handles archive/delete cleanup.

### Edit prompts

Edit any file in `commands/`. This is the single source of truth.

### Sync

```bash
uv run python scripts/sync.py
```

Or use:

```bash
./sync.sh
```

This is just a thin wrapper around the same `uv` command.

The sync tool copies prompts to all supported AI CLIs that are already installed on your machine and skips the rest.

### Path Resolution

The sync tool checks the install roots that already exist on the machine and writes only to those locations.

- macOS and Linux home-based roots: `~/.claude`, `~/.gemini`, `~/.gemini/antigravity`, `~/.codex`, `~/.kilocode`
- OpenCode roots: legacy `~/.opencode` and the documented config root `~/.config/opencode`
- Windows home-based roots: `%USERPROFILE%\.claude`, `%USERPROFILE%\.gemini`, `%USERPROFILE%\.gemini\antigravity`, `%USERPROFILE%\.codex`, `%USERPROFILE%\.kilocode`
- Windows OpenCode roots: `%USERPROFILE%\.config\opencode` and `%APPDATA%\opencode` when present

If more than one valid root exists for the same tool, Kamma syncs all of them.

### What it creates in your project

When you run `/kamma:0-setup` in a project:

```
your-project/
└── kamma/
    ├── project.md          # What the project is
    ├── tech-stack.md       # Languages, frameworks, tools
    ├── workflow.md         # Task lifecycle rules
    ├── threads.md          # Master index of all threads
    └── threads/
        └── <thread_id>/
            ├── spec.md     # What to build
            └── plan.md     # How to build it
```

Inspired by [Conductor](https://github.com/fcoury/conductor).
