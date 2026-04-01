---
name: kamma
description: Spec-driven development skill for projects using Kamma. Use this skill when you detect a `kamma/` directory in the project, when working on tasks defined in a `plan.md` file, or when the user asks about threads, specs, or plans. Automatically follows task completion and the spec-driven methodology.
---

# Kamma Development Skill

This skill enables working effectively on projects managed by the Kamma framework — a spec-driven, structured development methodology.

## When This Skill Activates

Automatically apply this skill when:
- A `kamma/` directory exists in the project root
- The user mentions "threads", "kamma", "spec", or "plan" in the context of development
- Files like `kamma/threads.md`, `kamma/workflow.md`, or `kamma/project.md` are present
- The user runs any `/kamma:*` command

## Core Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
2. **Spec-Driven Development:** Understand the spec before implementing
3. **Thread Progress:** Update task status markers (`[ ]` → `[~]` → `[x]`)
4. **Independent Review Before Completion:** Threads are not done when implementation ends

## Project Structure Understanding

When working on a Kamma project, familiarize yourself with:

```
kamma/
├── project.md              # Project vision and goals
├── tech-stack.md           # Technology choices and constraints
├── workflow.md             # Development methodology and procedures
├── threads.md              # Master list of all threads
└── threads/                # Individual thread folders
    └── <thread_id>/
        ├── spec.md         # Feature specification
        ├── plan.md         # Implementation plan with tasks
        └── review.md       # Review outcome (written by /kamma:3-review)
```

## Task Execution Protocol

Read and follow `kamma/workflow.md` for the full task lifecycle. It is the single source of truth for how tasks are selected, implemented, reviewed, and finalized.

## Available Commands

- `/kamma:0-setup` - Initialize Kamma in a project
- `/kamma:1-plan` - Create a new feature/bug thread
- `/kamma:2-do` - Execute tasks from the current thread until review handoff
- `/kamma:3-review` - Perform structured review of the active thread
- `/kamma:4-finalize` - Complete a reviewed thread and handle cleanup
- `/kamma:5-status` - Show project progress

## Context Loading

Before starting any implementation work, always load:
1. `kamma/workflow.md` - For task lifecycle procedures
2. `kamma/tech-stack.md` - For technology constraints
3. The active thread's `spec.md` - For requirements
4. The active thread's `plan.md` - For current task status

## Error Handling

If something goes wrong:
1. Do not proceed without user confirmation
2. Announce the failure clearly
3. Wait for user instructions
