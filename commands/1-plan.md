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

**CRITICAL: Never ask questions in plain markdown or plain chat.** Every question to the user must go through a native question/input tool.

1. Always attempt the native tool first, in this order:
   - `AskUserQuestion`
   - `request_user_input`
2. Only fall back to a plain message if the tool call actually fails or throws an error. Do not assume the tool is unavailable — try it first.
3. Asking in markdown when a native tool is available is a violation of this rule.

### 2.1 Get the Thread Description

1. Read and understand the `kamma/` directory files.
2. **Get the description:**
   - **If `{{args}}` has one:** Use it.
   - **If `{{args}}` is empty:** Use the native question/input tool to ask: "Please provide a brief description of the thread (feature, bug fix, chore, etc.) you want to start." Wait for the response. Fall back to a normal message only if no such tool is available.
3. If the work is tied to a GitHub issue, ask for or preserve the issue number and include it in the thread description.
4. Infer the thread type from the description. Don't ask.

### 2.2 Write `spec.md`

1. **Surface assumptions before drafting.** Use `project.md`, `tech.md`, and the codebase to infer as much as you can. Then, before writing anything, identify your key assumptions — about scope, tech stack, affected files, and approach. If any assumption is uncertain and getting it wrong would change the spec significantly, surface it as a question. Batch all questions into a single round using the native question/input tool and wait. Fall back to a normal message only if no such tool is available. If everything can be confidently inferred, skip the question round and proceed.
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

2. Before writing tasks, identify the dependency order: what must exist before what else can be built. Let this order determine the phase sequence.

3. Read the confirmed spec and `kamma/workflow.md`. Generate `plan.md` with Phases → Tasks → Sub-tasks using `[ ]` markers.

   Slice tasks vertically — each task should deliver a testable piece of working functionality end-to-end, not a horizontal layer (all DB, then all API, then all UI).

   Include an **Architecture Decisions** section near the top (after any GitHub issue reference) listing key choices made during planning and their rationale — which pattern to follow, where to place new code, what was deliberately not abstracted, and why.

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

4. **Simplicity check.** Before presenting, review the plan for overengineering. Could this be done with fewer phases, fewer files, or simpler logic? If you wrote 20 tasks and it could be 8, rewrite it. Would a senior engineer say this is overcomplicated? If yes, simplify. If a task touches more than ~5 files or has more than 3 acceptance criteria, split it.

5. Present the draft:
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
