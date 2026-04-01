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
├── copy.sh               # Copy to all CLIs
└── README.md
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

### Copy

```bash
./copy.sh
```

This converts and copies prompts to all supported AI CLIs.

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
