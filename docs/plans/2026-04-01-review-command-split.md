# Review Command Split Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split implementation and review so `/kamma:2-do` ends by handing off to `/kamma:3-review`, which is intended to be run by a different agent or tool.

**Architecture:** Add a dedicated review command document, then update the implementation and shared workflow instructions so they consistently describe review as a separate mandatory stage before final completion. Keep the change limited to command and workflow documentation; no runtime code is involved.

**Tech Stack:** Markdown command docs, Kamma workflow templates

---

### Task 1: Add standalone review command

**Files:**
- Create: `commands/3-review.md`

**Step 1: Draft the review lifecycle**

Define the command as a structured thread review that loads thread context, offers reviewer selection, recommends using a different agent, includes CodeRabbit and CodeRabbit AI review methods, and requires findings to be implemented before completion.

**Step 2: Add explicit handoff guidance**

State that the command is designed for a different agent or tool than the implementation agent when possible, while still allowing the user to continue with the current reviewer if they choose.

**Step 3: Save the command doc**

Write the final protocol to `commands/3-review.md`.

### Task 2: Update implementation command handoff

**Files:**
- Modify: `commands/2-do.md`

**Step 1: Replace direct completion flow**

Change the finalization language so `/kamma:2-do` stops at “ready for review” instead of marking the thread complete immediately after implementation.

**Step 2: Add explicit user instruction**

Instruct the user to run `/kamma:3-review` with a different agent or tool before user evaluation and final completion.

### Task 3: Align shared workflow

**Files:**
- Modify: `templates/workflow.md`

**Step 1: Insert review into the standard task lifecycle**

Add a review stage after implementation and testing and before final completion.

**Step 2: Keep responsibilities clear**

Make it explicit that independent review can be performed in a separate session or tool and that accepted findings must be implemented before the work is considered done.

### Task 4: Verify consistency

**Files:**
- Modify: `commands/2-do.md`
- Modify: `commands/3-review.md`
- Modify: `templates/workflow.md`

**Step 1: Re-read the changed files**

Check for contradictions in terminology, completion state, and command ordering.

**Step 2: Confirm command references**

Ensure the docs consistently reference `/kamma:3-review` as the review gate and preserve the existing user-evaluation step after review.
