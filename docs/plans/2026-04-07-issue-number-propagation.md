# Issue Number Propagation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make Kamma preserve GitHub issue numbers from thread initialization through finalize and commit message guidance.

**Architecture:** Update the master workflow template first, then align the user-facing command documents to require the same issue-number behavior. Keep the change limited to Kamma markdown docs.

**Tech Stack:** Markdown command docs, Kamma workflow template

---

### Task 1: Update the master workflow

**Files:**
- Modify: `templates/workflow.md`

**Step 1: Add issue-tracking guidance near the task flow**

Require issue references to stay visible in the thread title, `threads.md`, `spec.md`, and `plan.md`.

**Step 2: Add finalize behavior**

State that finalize should use the preserved issue number to comment on and close the GitHub issue.

**Step 3: Add commit guidance**

State that suggested commit messages must reference the issue number when one exists.

### Task 2: Align planning and setup commands

**Files:**
- Modify: `commands/0-setup.md`
- Modify: `commands/1-plan.md`
- Modify: `commands/kamma.md`

**Step 1: Require issue capture during thread creation**

Tell the planner to ask for or preserve the issue number when a thread is linked to an issue.

**Step 2: Require issue visibility in thread artifacts**

Ensure the issue number is called out in the thread description, `threads.md`, `spec.md`, and `plan.md`.

### Task 3: Align execution and finalization commands

**Files:**
- Modify: `commands/2-do.md`
- Modify: `commands/3-review.md`
- Modify: `commands/4-finalize.md`

**Step 1: Preserve the issue reference during execution and review**

Tell execution and review to keep the issue reference intact and visible in thread artifacts.

**Step 2: Make finalize depend on the stored issue number**

Require finalize to look for the preserved issue reference first, then comment on and close the issue, and suggest a commit message that references it.

### Task 4: Verify consistency

**Files:**
- Modify: `templates/workflow.md`
- Modify: `commands/0-setup.md`
- Modify: `commands/1-plan.md`
- Modify: `commands/2-do.md`
- Modify: `commands/3-review.md`
- Modify: `commands/4-finalize.md`
- Modify: `commands/kamma.md`

**Step 1: Re-read edited files**

Check that they all describe the same issue propagation behavior.

**Step 2: Check for ambiguity**

Confirm there is no path where an agent can plausibly miss the issue number or omit issue-linked commit message guidance.
*** Update File: templates/workflow.md
@@
 5. **Review the Work Before Calling It Done:** Implementation is not complete until it has been reviewed

## GitHub Issue Continuity

If a thread is tied to a GitHub issue, preserve that issue number prominently from start to finish.

1. Include the issue number in the thread title or description.
2. Include the issue number in the `kamma/threads.md` entry.
3. Include a dedicated issue reference near the top of the thread `spec.md`.
4. Include the same issue reference near the top of the thread `plan.md`.
5. Do not drop or rewrite the issue reference during implementation, review, or finalize.
6. **Finish the Thread:**
   - After review is clear, run `/kamma:4-finalize`.
   - Mark the thread complete, sync project docs, and archive the completed thread there.
   - If the thread references a GitHub issue, use the preserved issue number to post a summary comment and close the issue during finalize.

If the thread references a GitHub issue, the suggested commit message must also reference that issue number, for example `fix(parser): handle empty input (closes #123)`.
