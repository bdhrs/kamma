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
- Files like `kamma/workflow.md`, or `kamma/project.md` are present
- The user runs any `/kamma:*` command

## Core Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
2. **Spec-Driven Development:** Understand the spec before implementing
3. **Thread Progress:** Update task status markers (`[ ]` → `[~]` → `[x]`)
4. **Review the Work Before Calling It Done:** Threads are not done when implementation ends

**Spec gate — files on disk before any code.** `spec.md` and `plan.md` must already exist on disk for the thread before you edit a single line of code. If either is missing, run `/kamma:1-plan` to create them first (or, for a tiny change, ask the user whether to skip the ceremony — never decide silently). Implementing first and backfilling the thread files afterwards is dishonest and is not allowed, even for a 3-line change.

**Minimal-first gate — draft the smallest change first.** When writing `spec.md`, draft the smallest change that satisfies the request — no extra helpers, refactors, generalization, or "while we're at it" machinery. If a simpler approach exists, say so before writing the spec and propose the minimal version. Defer extras to a follow-up unless the user asks for them now. Climb the laziness ladder and stop at the first rung that meets the need: (1) does it need to exist at all? — if not, drop it; (2) does the standard library or a language built-in do it? — use it; (3) is there a native platform feature? — use it; (4) is there an already-installed dependency? — reuse it; (5) can it be one line? — keep it one line; (6) only then write the minimum that works. Never trade away correctness, error handling, validation, or security to reach a lower rung.

**Smoke gate — run the full suite before handoff.** Before asking the user to test, run the project's full test suite (or a broad smoke check covering the affected areas) once — not just each task's `→ verify:` line. Per-task checks miss pre-existing or cross-task bugs. If it fails, fix and re-run before handoff.

**Drift gate — keep `spec.md` and `plan.md` in sync with reality, always.** The instant implementation diverges from `spec.md` or `plan.md` — a wrong assumption, a different approach, a different set of files, reordered or dropped tasks — update the relevant file immediately, before continuing. The same applies to any follow-up change the user requests mid-thread: record it right away, not at wrap-up. Never leave `plan.md` with `[x]` tasks that no longer match what was built.

## Project Structure Understanding

When working on a Kamma project, familiarize yourself with:

```
kamma/
├── project.md              # Project vision and goals
├── tech.md                 # Technology choices and constraints
├── workflow.md             # How work moves forward
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
- `/kamma:loop` - Create a new standing loop thread for repeated work
- `/kamma:2-do` - Work through the current thread or one loop cycle
- `/kamma:3-review` - Review the active thread or loop cycle
- `/kamma:4-finalize` - Complete a thread or finished loop and handle cleanup
- `/kamma:5-status` - Show project progress
- `/kamma:improve` - Sweep lessons across all repos and consolidate recurring mistakes into kamma framework improvements (run from anywhere; writes only to the kamma repo)
- `/kamma` - Plan, implement, review, and finalize a thread in a single run (no prior setup required)
- `/kamma:quick` - Same single run for a small change, with full review/commit/reflect rigor but no spec, plan, or thread directory

## Loop Threads

Standing loop threads (`/kamma:loop`) follow a repeating cycle: **Report → Analyze → Approval (HARD STOP) → Implement → Validate**. Unlike finite threads, loop plans stay stable while work advances through cycles recorded in the `cycles/` directory. Loops also maintain a curated `learnings.md` file to carry knowledge between cycles. Always respect the mandatory approval gate before source edits in a loop.

## Context Loading

Before starting any implementation work, always load:
1. `kamma/workflow.md` - For the project's step-by-step flow
2. `kamma/tech.md` - For tools, constraints, and resources
3. The active thread's `spec.md` - For requirements
4. The active thread's `plan.md` - For current task status

## Error Handling

If something goes wrong:
1. Tell the user what failed in plain language
2. Try a sensible fallback or alternate path
3. Keep going whenever there is still a reasonable way to make progress
