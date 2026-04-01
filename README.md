# Kamma

Lightweight, cross-tool workflow management for AI coding CLIs.

*Kamma* a Pāḷi word for action, work, doing.

## Commands

| Command | Description |
|---------|-------------|
| `/kamma:0-setup` | Scaffold a project with project.md, tech-stack.md, workflow.md |
| `/kamma:1-plan` | Create a new thread (feature, bug fix, chore) with spec + plan |
| `/kamma:2-do` | Execute tasks from the current thread's plan |
| `/kamma:status` | Show progress overview of all threads |

## Supported Tools

| Tool | Format | Invocation |
|------|--------|------------|
| Claude Code | TOML commands + plugin.json | `/kamma:0-setup` |
| Gemini CLI | TOML commands + gemini-extension.json | `/kamma:0-setup` |
| OpenCode | MD with frontmatter | `/kamma-0-setup` |
| Kilo CLI | Skills (SKILL.md) | Skill-based activation |
| Codex CLI | Plain MD prompts | `/prompts:kamma-0-setup` |

## Project Structure

```
kamma/
├── commands/               # Source prompts (single source of truth)
│   ├── 0-setup.md
│   ├── 1-plan.md
│   ├── 2-do.md
│   └── status.md
├── registration/           # Tool registration files
│   ├── claude-plugin.json
│   ├── gemini-extension.json
│   └── GEMINI.md
├── skills/
│   └── kamma/
│       └── SKILL.md        # Auto-activation skill
├── templates/
│   └── workflow.md         # Default workflow template
├── deploy.sh               # Copy to all CLIs
└── README.md
```

## Usage

### Edit prompts

Edit any file in `commands/`. This is the single source of truth.

### Copy

```bash
./deploy.sh
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
