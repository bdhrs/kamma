---
name: kamma
description: Spec-driven work skill for projects using Kamma. Use this skill when you detect a `kamma/` directory in the project, when working on tasks defined in a `plan.md` file, or when the user asks about threads, specs, or plans. Automatically follows the Kamma way of working.
---

# Kamma Work Skill

This skill helps you work effectively in projects that use Kamma, a spec-driven way of working.

## When This Skill Activates

Automatically apply this skill when:
- A `kamma/` directory exists in the project root
- The user mentions "threads", "kamma", "spec", or "plan" in the context of project work
- Files like `kamma/threads.md`, `kamma/workflow.md`, or `kamma/project.md` are present
- The user runs any `/kamma:*` command

## Core Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
2. **Spec-Driven Development:** Understand the spec before implementing
3. **Thread Progress:** Update task status markers (`[ ]` → `[~]` → `[x]`)
4. **Review the Work Before Calling It Done:** Threads are not done when implementation ends

## Project Structure Understanding

When working on a Kamma project, familiarize yourself with:

```
kamma/
├── project.md              # Project vision and goals
├── context.md              # Technology choices and constraints
├── workflow.md             # How work moves forward
├── threads.md              # Master list of all threads
└── threads/                # Individual thread folders
    └── <thread_id>/
        ├── spec.md         # Feature specification
        ├── plan.md         # Implementation plan with tasks
        └── review.md       # Review outcome (written by /kamma:3-review)
```

## Task Execution Protocol

Read and follow `kamma/workflow.md` for the full task flow. It is the single source of truth for how tasks are selected, implemented, reviewed, and finalized.

## Available Commands

- `/kamma:0-setup` - Initialize Kamma in a project
- `/kamma:1-plan` - Create a new feature/bug thread
- `/kamma:2-do` - Work through the current thread until it is ready for review
- `/kamma:3-review` - Review the active thread
- `/kamma:4-finalize` - Complete a reviewed thread and handle cleanup
- `/kamma:5-status` - Show project progress

## Context Loading

Before starting any implementation work, always load:
1. `kamma/workflow.md` - For the project's step-by-step flow
2. `kamma/context.md` - For tools, constraints, and resources
3. The active thread's `spec.md` - For requirements
4. The active thread's `plan.md` - For current task status

## Error Handling

If something goes wrong:
1. Do not proceed without user confirmation
2. Announce the failure clearly
3. Wait for user instructions
