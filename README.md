# Kamma

Lightweight, cross-tool planning and tracking for AI coding CLIs.

*Kamma* a Pali word for action, work, doing.

## Commands

| Command | Description |
|---------|-------------|
| `/kamma:0-setup` | Scaffold a project with project.md, tech.md, workflow.md |
| `/kamma:1-plan` | Create a new thread (feature, bug fix, chore) with spec + plan |
| `/kamma:2-do` | Work through the selected thread until it is ready to review |
| `/kamma:3-review` | Review finished work, ideally in a fresh tool or session |
| `/kamma:4-finalize` | Finish a reviewed thread, update docs, and clean up |
| `/kamma:5-status` | Show where things stand across all threads |

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

# 5. Review it, ideally in a fresh session or tool
/kamma:3-review

# 6. Finalize — mark complete, sync docs, cleanup
/kamma:4-finalize
```

## Usage

### Workflow

Each thread usually goes like this:

1. `/kamma:1-plan` creates the thread spec and implementation plan.
2. `/kamma:2-do` works through the thread and stops when the work is ready for review.
3. `/kamma:3-review` reviews the work, ideally in a different tool or session.
4. `/kamma:4-finalize` marks the thread complete, updates docs, and lets you archive, delete, or keep the thread.

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
    ├── tech.md             # Tools, resources, constraints, and working assumptions
    ├── workflow.md         # How work moves forward
    ├── threads.md          # Master index of all threads
    └── threads/
        └── <thread_id>/
            ├── spec.md     # What to build
            └── plan.md     # How to build it
```

Inspired by [Conductor](https://github.com/fcoury/conductor).
