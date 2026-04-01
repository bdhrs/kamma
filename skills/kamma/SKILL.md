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
        └── plan.md         # Implementation plan with tasks
```

## Task Execution Protocol

When implementing a task from a Kamma plan:

### 1. Select and Mark Task
- Find the next pending task (marked `[ ]`) in the thread's `plan.md`
- Update its status to in-progress: `[~]`

### 2. Follow Workflow
- Read and follow `kamma/workflow.md` for the task lifecycle
- Implement the task according to the spec

### 3. Hand Off to Review
1. Verify the implementation works correctly
2. Stop at review handoff rather than declaring the thread done
3. Run `/kamma:3-review`, ideally with a different agent or tool

### 4. Finalize After Review
1. Implement accepted review findings
2. Run `/kamma:4-finalize`
3. Mark thread complete: `[x]`

### 5. Phase Completion
When completing a phase:
1. Run relevant tests
2. Provide manual verification steps to user
3. Update `plan.md` with completion status

## Status Markers

- `[ ]` - Pending (not started)
- `[~]` - In Progress (currently working)
- `[x]` - Completed

## Available Commands

- `/kamma:0-setup` - Initialize Kamma in a project
- `/kamma:1-plan` - Create a new feature/bug thread
- `/kamma:2-do` - Execute tasks from the current thread until review handoff
- `/kamma:3-review` - Perform structured review of the active thread
- `/kamma:4-finalize` - Complete a reviewed thread and handle cleanup
- `/kamma:status` - Show project progress

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
