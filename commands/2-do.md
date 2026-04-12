---
description: Executes the tasks defined in the specified thread's plan
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to implement a thread by executing its plan. Follow this process precisely.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way to make progress, reassess, and keep going. Tell the user about important failures, but keep working unless the task truly cannot move forward.

TO-DO LIST: Keep a running to-do list for this command. Add work before you start it, tick items off as you finish them. You don't need a reminder every section — just keep the list current.

Verify `kamma/project.md`, `kamma/tech.md`, and `kamma/workflow.md` exist. If any are missing, say what's missing, announce that Kamma is not set up (`/kamma:0-setup`), and continue if there's still a reasonable path.

---

## 2.0 CHOOSE A THREAD

1. Check if the user provided a thread name as an argument.

2. List all directories in `kamma/threads/`. For each, read `spec.md` for the description and `plan.md` to check progress (look for `[ ]` or `[~]` tasks).
   - If no threads exist: "No active threads found. Create one with `/kamma:1-plan`." Then stop.

3. **Select:**
   - **If a name was provided:** Case-insensitive match against directory names and spec descriptions. Confirm if unique. If ambiguous, list the options.
   - **If no name:** Pick the first thread with incomplete tasks. Announce: "Automatically selecting the next incomplete thread: '<description>'." If all threads are complete, say so and suggest the next step.

---

## 3.0 DO THE WORK

**Scope rule:** Touch only what the current task requires. Don't refactor, clean up, add comments to, or improve adjacent code. Every changed line must trace directly to a task in `plan.md`. If you notice unrelated issues, note them — don't fix them.

1. Announce which thread you're starting.

2. **Load thread files:**
   - `kamma/threads/<thread_id>/plan.md`
   - `kamma/threads/<thread_id>/spec.md`
   - `kamma/workflow.md`
   - If the thread references a GitHub issue, keep that number visible and unchanged throughout.
   - If any read fails, say what failed, try to recover, and keep going if you can.

3. **Execute tasks** through `plan.md` one by one, following `workflow.md`:
   - Change `[ ]` to `[~]` before starting a task.
   - Implement only what that task requires.
   - Run the verification in the task's `→ verify:` line.
   - If verification fails, try to fix it up to 2 times. If still failing, note the issue in `plan.md` and continue.
   - Change `[~]` to `[x]` only after passing verification or recording the issue.

4. At the end of each phase, run the phase's verification task.

5. **Hand off for review:**
   - After all tasks are done and locally verified, don't mark the thread fully complete yet.
   - Ask the user to test and wait for confirmation.
   - Once confirmed, suggest running `/kamma:3-review` in a fresh session using a different model (e.g., if on Sonnet, suggest Opus) for an independent review.
   - The thread should only move to completion after review findings are addressed.
