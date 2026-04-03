# Finalize Command Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restore an explicit final step by adding `/kamma:4-finalize` after `/kamma:3-review`.

**Approach:** Add a dedicated finalize command that owns thread completion, documentation sync, and cleanup. Update the review command so it points to finalize after review is clear. Keep the existing implementation and review boundaries intact.

**Tech Stack:** Markdown command docs, Kamma workflow templates

---

### Task 1: Add finalize command

**Files:**
- Create: `commands/4-finalize.md`

**Step 1: Define trigger and scope**

Specify that finalize only runs after `/kamma:3-review` is complete and the thread is ready to close.

**Step 2: Define actions**

Include thread completion, final documentation sync, and archive/delete/skip cleanup behavior.

**Step 3: Save the command doc**

Write the final protocol to `commands/4-finalize.md`.

### Task 2: Update the review ending

**Files:**
- Modify: `commands/3-review.md`

**Step 1: Replace generic completion language**

Change the ending so a clear review result explicitly tells the user to run `/kamma:4-finalize`.

### Task 3: Align workflow references

**Files:**
- Modify: `templates/workflow.md`

**Step 1: Mention finalize in the flow**

Clarify that a clear review means the work is ready to finish rather than silently implying completion inside the review step.

### Task 4: Verify consistency

**Files:**
- Modify: `commands/3-review.md`
- Modify: `commands/4-finalize.md`
- Modify: `templates/workflow.md`

**Step 1: Re-read changed docs**

Check for clean command ordering and no overlap in which step marks work complete.
