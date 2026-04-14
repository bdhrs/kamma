---
description: Saves session context to the active thread so the next agent can pick up where you left off
---

## 1.0 PURPOSE
You are an AI agent. Your job is to write a handoff file that preserves your current session context for the next agent that picks up this thread.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way.

---

## 2.0 FIND THE ACTIVE THREAD

1. Check if the user provided a thread name as an argument.

2. List all directories in `kamma/threads/`. For each, read `spec.md` for the description and `plan.md` to check progress (look for `[ ]` or `[~]` tasks).
   - If no threads exist: "No active threads found." Then stop.

3. **Select:**
   - **If a name was provided:** Case-insensitive match against directory names and spec descriptions. Confirm if unique. If ambiguous, list the options.
   - **If no name:** Pick the first thread with incomplete tasks. If all are complete, say so and stop.

---

## 3.0 WRITE THE HANDOFF

1. Write `kamma/threads/<thread_id>/handoff.md` with the context the next session needs. Cover whatever is relevant — there is no fixed template. Think about:
   - What you were working on and how far you got
   - Approaches you tried and why they failed
   - Non-obvious discoveries about the codebase
   - Specific errors or blockers encountered
   - What should be tried next
   - Anything that would save the next agent from repeating your work

2. If a `handoff.md` already exists, overwrite it — but preserve any still-relevant context from the previous handoff.

3. Announce that the handoff was written and which thread it belongs to.
