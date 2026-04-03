---
description: Plans, implements, reviews, and finalizes a thread in a single run without requiring prior setup
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to take a thread from zero to done in a single run: plan it, implement it, review it, and finalize it.

**There are exactly two stops in this flow.** Everything else runs autonomously without asking the user.

1. **Present the plan** — show the spec and plan, wait for approval before implementing.
2. **Ask the user to test** — after implementation, ask the user to manually test. If they confirm it works, proceed to review and finalize immediately. Only ask "Can I review and finalize?" after fixing reported issues.

CRITICAL: Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

TO-DO LIST: Keep a to-do list for this entire command. Add the current section's work before you start it, update the list as you go, and use it to track progress until the command is complete.
At the end of every section in this file, tick off completed to-do items before you move on.

---

## 2.0 ENVIRONMENT BOOTSTRAP
**Run silently. Do not stop.**

Check for `kamma/project.md`, `kamma/tech.md`, `kamma/workflow.md`, and `kamma/threads.md`.

If any are missing, generate them immediately without asking:
- **`kamma/project.md`**: Infer goal, audience, and success criteria from the codebase (README, manifests, source).
- **`kamma/tech.md`**: Infer tools, platforms, and constraints from the codebase.
- **`kamma/workflow.md`**: Copy from `templates/workflow.md` if it exists, otherwise generate a minimal standard Kamma workflow.
- **`kamma/threads.md`**: Create with the standard header.

Create the `kamma/` directory if it does not exist. Continue immediately.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 3.0 PLAN THE THREAD
**Run silently. Do not stop except for the plan presentation.**

### 3.1 Get the Thread Description

- **If `{{args}}` is provided:** Use it as the thread description.
- **If `{{args}}` is empty:** Ask: "What would you like to work on?" Wait for the response. This is a pre-flight question, not one of the three stops.

Infer the thread type (feature, bug, chore, refactor) from the description. Do not ask.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 3.2 Generate Spec and Plan

1. Read `kamma/project.md`, `kamma/tech.md`, and `kamma/workflow.md`. Scan the codebase to fill in any gaps. Do not ask the user questions.
2. Generate `spec.md`: Overview, What it should do, Constraints, How we'll know it's done, What's not included.
3. Generate `plan.md`: Hierarchical Phases → Tasks → Sub-tasks with `[ ]` markers, following `kamma/workflow.md`. Inject a Phase Completion verification task at the end of each phase if the workflow defines one.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 3.3 — STOP 1: Present the Plan

Present the spec and plan together and wait for approval:

> "Here is the plan for this thread. Please review and confirm before I start."
>
> **Spec:**
> ```markdown
> [spec.md content]
> ```
>
> **Plan:**
> ```markdown
> [plan.md content]
> ```
>
> "Reply 'go' to start, or tell me what to change."

Apply any requested changes and re-present until the user confirms. Then immediately continue.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 3.4 Create Thread Files

- Check for name collisions in `kamma/threads/`. Use a variant if the name exists.
- Generate thread ID: `YYYYMMDD_shortname`.
- Create `kamma/threads/<thread_id>/` and write `spec.md` and `plan.md`.
- Append to `kamma/threads.md`:
  ```markdown

  ---

  ## [ ] Thread: <Thread Description>
  *Link: [./kamma/threads/<thread_id>/](./kamma/threads/<thread_id>/)*
  ```

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 4.0 IMPLEMENT THE THREAD
**Run autonomously. Do not stop for phase checkpoints or mid-task confirmations.**

1. Update the thread status in `kamma/threads.md` from `[ ]` to `[~]`.
2. Loop through every task in `plan.md`, following `kamma/workflow.md` as the source of truth for each task's flow (implement → test → commit → update plan).
3. At phase boundaries: run tests and commit a checkpoint. If tests fail, attempt to fix (max 2 attempts). If still failing, note it and continue — do not stop to ask.

### 4.1 — STOP 2: Ask the User to Test

When all tasks are done and the implementation is locally verified, explain specifically how to test the changes — what commands to run, what to click, what to observe, what the expected outcome is. Then ask:

> "Please test it using the steps above and let me know when you're done, or if you found any issues."

Wait for the user's response.

- **If they confirm it works** (e.g. "done", "looks good", "yes", "perfect"): proceed immediately to Section 5.0 without asking again.
- **If they report issues**: fix them, then ask: "Can I review and finalize the thread?" Keep fixing and re-asking until the user confirms. Never wait passively — always push forward.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 5.0 REVIEW AND FINALIZE
**Runs autonomously once the user confirms.**

### 5.2 Review

**CRITICAL: You must actually perform the review before writing the file. Do not write `review.md` first and call it done.**

1. Re-read `kamma/threads/<thread_id>/spec.md` and `plan.md`.
2. Run `git diff` and read every changed file.
3. Run the test suite and read the output.
4. For each of the following, read the relevant code and report what you found — do not skip any:
   - **Spec coverage:** Does every requirement in `spec.md` have a corresponding implementation?
   - **Plan completion:** Is every task in `plan.md` marked done and actually implemented?
   - **Code correctness:** Are there logic errors, missing cases, or broken assumptions in the changed files?
   - **Test coverage:** Do the tests verify the key behaviors described in the spec?
   - **Regressions:** Could any change break existing behavior?
5. For each finding, state: severity (`blocking`, `major`, `minor`, `nit`), file and line, what is wrong, why it matters, recommended fix.
6. Fix any blocking or major findings immediately. Re-run tests after each fix. Repeat until none remain.
7. Only then write `kamma/threads/<thread_id>/review.md`:
   - Review date
   - Reviewer: "kamma (inline)"
   - Findings summary (count by severity, or "No findings")
   - Verdict: `PASSED`


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 5.3 Finalize

1. Update thread status in `kamma/threads.md` from `[~]` to `[x]`.
2. Update `kamma/project.md` and `kamma/tech.md` if the thread changed anything significant. Apply sensible updates without asking unless the change is ambiguous.
3. Archive the thread folder to `kamma/archive/` and remove it from `kamma/threads.md`.
4. Announce that the thread is complete.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

