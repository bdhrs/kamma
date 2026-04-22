---
description: Plans a thread and generates thread-specific spec documents
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to create a new thread — generate its spec and plan, and place them in the right folder.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way to make progress, reassess, and keep going. Tell the user about important failures, but keep working unless the task truly cannot move forward.

TO-DO LIST: Keep a running to-do list for this command. Add work before you start it, tick items off as you finish them. You don't need a reminder every section — just keep the list current.

## 1.1 SETUP CHECK
**Verify that the Kamma environment is set up.**

1. Check for these files:
   - `kamma/tech.md`
   - `kamma/workflow.md`
   - `kamma/project.md`

2. If any are missing, say what's missing and try to continue. Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment." Keep going if there's still a reasonable path.

---

## 2.0 CREATE A NEW THREAD

### 2.0.1 Question Tool Rule

1. If the environment exposes a native question/input tool, you must use it instead of asking in plain markdown or plain chat.
2. Prefer these native tools in this order when available:
   - `AskUserQuestion`
   - `request_user_input`
3. Only fall back to a normal conversational message if no native question/input tool exists in the environment, or the tool call fails.
4. Keep the wording and answer options required below, but deliver them through the tool whenever possible.

### 2.1 Get the Thread Description

1. Read and understand the `kamma/` directory files.
2. **Get the description:**
   - **If `{{args}}` has one:** Use it.
   - **If `{{args}}` is empty:** Use the native question/input tool to ask: "Please provide a brief description of the thread (feature, bug fix, chore, etc.) you want to start." Wait for the response. Fall back to a normal message only if no such tool is available.
3. If the work is tied to a GitHub issue, ask for or preserve the issue number and include it in the thread description.
4. Infer the thread type from the description. Don't ask.

### 2.2 Write `spec.md`

1. **Ask only what you need to.** Use `project.md`, `tech.md`, and the codebase to answer as much as you can. Treat handoff to a different agent as the normal case. Only ask when the answer genuinely can't be inferred. If a critical detail is missing and the repo doesn't answer it, ask instead of guessing. Batch all unknowns into a single round using the native question/input tool and wait. Fall back to a normal message only if no such tool is available.
   - Present 2–3 plausible options (A, B, C) per question. Last option must be "Type your own answer".
   - **Features:** Focus on intent and edge cases — how it should behave, who it's for, what success looks like.
   - **Bugs, chores, etc.:** Focus on reproduction, scope, or how you'll know it's fixed.

2. **Push back if warranted.** If a simpler approach exists, say so. If the request would create unnecessary complexity or conflict with existing architecture, raise it before writing the spec.

3. Draft `spec.md` with these sections:
   - Overview
   - What it should do
   - Assumptions & uncertainties (what you're assuming, what you couldn't verify, what might be wrong)
   - Constraints (if any)
   - How we'll know it's done
   - What's not included

   The spec must be self-contained — a different agent in a later session should understand it fully. Write down current behavior, affected files, constraints, assumptions, and project-specific terminology that matters. Don't rely on conversational memory.

   If tied to a GitHub issue, include a dedicated reference near the top.

4. Present the draft for review:
   > "I've drafted the spec. Please review:"
   >
   > ```markdown
   > [spec.md content]
   > ```
   >
   > "Does this look right? Let me know if anything needs changing."

   Revise until confirmed.

### 2.3 Write `plan.md`

1. Announce: "Now I'll create `plan.md` based on the spec."

2. Read the confirmed spec and `kamma/workflow.md`. Generate `plan.md` with Phases → Tasks → Sub-tasks using `[ ]` markers.

   Assume a different agent with zero context will execute this. Include: exact files to inspect or edit, relevant docs, task ordering, expected outcomes, and constraints to preserve. Don't leave important context implicit.

   **Every task must include a `→ verify:` line** with the specific check — the test to run, the behavior to observe, the expected output. Vague checks don't count.

   Example:
   ```
   - [ ] Add input validation to search field
     → verify: run `flutter test test/search_test.dart`, expect all pass
   - [ ] Update grammar table to show new column
     → verify: open entry #123, confirm new column appears with correct data
   ```

   The plan structure must follow `kamma/workflow.md`. Add an automatic verification task at the end of each phase — no manual user approval gates mid-plan.

   If tied to a GitHub issue, include the same reference near the top.

3. **Simplicity check.** Before presenting, review the plan for overengineering. Could this be done with fewer phases, fewer files, or simpler logic? If you wrote 20 tasks and it could be 8, rewrite it. Would a senior engineer say this is overcomplicated? If yes, simplify.

4. Present the draft:
   > "Here's the plan. Please review:"
   >
   > ```markdown
   > [plan.md content]
   > ```
   >
   > "Does this look right? Let me know if anything needs changing."

   Revise until confirmed.

### 2.4 Create the Thread Files

1. Check existing thread directories in `kamma/threads/`. If the proposed name collides, pick a different one.
2. Generate thread ID: `YYYYMMDD_shortname`.
3. Create `kamma/threads/<thread_id>/`.
4. Write the confirmed `spec.md` and `plan.md` to the directory.
5. If `kamma/threads.md` exists, delete it — legacy file.
6. Announce:
   > "New thread '<thread_id>' created. Start work with `/kamma:2-do`."
