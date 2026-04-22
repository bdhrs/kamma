---
description: Plans, implements, reviews, and finalizes a thread in a single run without requiring prior setup
---

**Sync note:** This command combines the logic of 1-plan, 2-do, 3-review, and 4-finalize. When updating shared logic, update both places.

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to take a thread from zero to done in a single run: plan it, implement it, review it, and finalize it.

**There are exactly two stops in this flow.** Everything else runs autonomously.

1. **Present the plan** — show the spec and plan, wait for approval before implementing.
2. **Ask the user to test** — after implementation, ask the user to test. If they confirm, proceed to review and finalize immediately. Only ask "Can I review and finalize?" after fixing reported issues.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way to make progress, reassess, and keep going. Tell the user about important failures, but keep working unless the task truly cannot move forward.

TO-DO LIST: Keep a running to-do list for this command. Add work before you start it, tick items off as you finish them. You don't need a reminder at the end of every section — just keep the list current.

---

## 2.0 LOAD PROJECT CONTEXT
**Run silently. Do not stop.**

Read and use the best available project context from files such as:
- `kamma/project.md`
- `kamma/tech.md`
- `README.md`
- Dependency manifests, source files, and other discoverable project docs

If any Kamma files are missing, don't stop and don't run setup. Continue with whatever context you can find.

`/kamma` is self-contained. Use only the context and rules in this command plus what you discover from the repo.

---

## 3.0 PLAN THE THREAD

### 3.0.1 Question Tool Rule

**CRITICAL: Never ask questions in plain markdown or plain chat.** Every question to the user must go through a native question/input tool.

- Always attempt the native tool first, in this order:
  1. `AskUserQuestion`
  2. `request_user_input`
- Only fall back to a plain message if the tool call actually fails or throws an error. Do not assume the tool is unavailable — try it first.
- Asking in markdown when a native tool is available is a violation of this rule.

### 3.1 Get the Thread Description

- **If `{{args}}` is provided:** Use it as the thread description.
- **If `{{args}}` is empty:** Use the native question/input tool to ask "What would you like to work on?" and wait for the response. Fall back to a normal message only if no such tool is available. This is a pre-flight question, not one of the two stops.

If the work is tied to a GitHub issue, ask for or preserve the issue number and include it in the thread description so it stays visible throughout.

Infer the thread type (feature, bug, chore, refactor) from the description. Don't ask.

### 3.2 Generate Spec and Plan

1. Read `kamma/project.md` and `kamma/tech.md` if they exist. Fill gaps from the repo. Then, before drafting anything, identify your key assumptions — about scope, tech stack, affected files, and approach. If any assumption is uncertain and getting it wrong would change the spec significantly, surface it as a question. Batch all questions into a single round using the native question/input tool and wait. Fall back to a normal message only if no such tool is available. If everything can be confidently inferred, skip the question round and proceed.

2. **Push back if warranted.** If a simpler approach exists than what was described, say so. If the request would create unnecessary complexity or conflict with existing architecture, raise it before planning.

3. Generate `spec.md` with these sections:
   - Overview
   - What it should do
   - Assumptions & uncertainties (what you're assuming, what you couldn't verify, what might be wrong)
   - Constraints
   - How we'll know it's done
   - What's not included

   The spec must be self-contained — a different agent in a later session should understand it fully. Write down the repo context you discovered: current behavior, affected files, important constraints, assumptions, and project-specific details that matter. Don't rely on "the agent already knows" — put it in writing.

   If tied to a GitHub issue, include a dedicated reference near the top.

4. Before writing tasks, identify the dependency order: what must exist before what else can be built. Let this order determine the phase sequence.

5. Generate `plan.md` with Phases → Tasks → Sub-tasks using `[ ]` markers.

   Slice tasks vertically — each task should deliver a testable piece of working functionality end-to-end, not a horizontal layer (all DB, then all API, then all UI).

   Include an **Architecture Decisions** section near the top (after any GitHub issue reference) listing key choices made during planning and their rationale — which pattern to follow, where to place new code, what was deliberately not abstracted, and why.

   Assume a different agent with zero memory will execute this plan. Include: exact file paths when known, relevant code areas or docs to check, task ordering, expected outcomes, and constraints the executor must preserve. A fresh agent should be able to execute directly from `plan.md`.

   **Every task must include a `→ verify:` line** stating the concrete check — the test to run, the behavior to observe, the expected output. Vague checks like "verify it works" don't count.

   Example:
   ```
   - [ ] Add input validation to search field
     → verify: run `flutter test test/search_test.dart`, expect all pass
   - [ ] Update grammar table to show new column
     → verify: open entry #123, confirm new column appears with correct data
   ```

   Add an automatic verification task at the end of each phase. No manual testing or user confirmation steps mid-plan.

   If tied to a GitHub issue, include the same reference near the top of `plan.md`.

6. **Simplicity check.** Before presenting, review the plan for overengineering. Could this be done with fewer phases, fewer files, or simpler logic? If you wrote 20 tasks and it could be 8, rewrite it. Ask yourself: would a senior engineer say this is overcomplicated? If yes, simplify. If a task touches more than ~5 files or has more than 3 acceptance criteria, split it.

### 3.3 STOP 1: Present the Plan

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

Apply any changes and re-present until the user confirms. Then continue immediately.

### 3.4 Create Thread Files

1. Ensure `kamma/` and `kamma/threads/` exist.
2. Generate a thread ID: `YYYYMMDD_shortname`.
3. Check for name collisions in `kamma/threads/`. Use a variant if needed.
4. Create `kamma/threads/<thread_id>/`.
5. Write the confirmed `spec.md` and `plan.md` to the thread directory.
6. If `kamma/threads.md` exists, delete it — legacy file.
7. Re-read the created files so later sections use the exact paths.

---

## 4.0 IMPLEMENT THE THREAD
**Run autonomously. Don't stop for phase checkpoints or mid-task confirmations.**

**Scope rule:** Touch only what the current task requires. Don't refactor, clean up, add comments to, or improve adjacent code. Every changed line must trace directly to a task in `plan.md`. If you notice unrelated issues, log them as `NOTICED — NOT TOUCHING: <file> — <issue>` in your output, then move on. Do not fix them.

1. Read `kamma/threads/<thread_id>/spec.md`, `plan.md`, and `handoff.md` (if it exists — context from a previous session).
2. Work through every unchecked task and sub-task in sequential order.
3. For each task or sub-task:
   - Change `[ ]` to `[~]` before you begin.
   - Implement only the work required for that item.
   - If implementation reveals that an assumption in `spec.md` is wrong or the approach must change, update `spec.md` before continuing — don't let it drift from reality.
   - Run the verification specified in the task's `→ verify:` line.
   - If verification fails, try to fix it up to 2 times. If still failing, note the issue clearly in `plan.md` and continue if there's still a reasonable path.
   - Change `[~]` to `[x]` only after the item passes verification, or after the remaining issue has been recorded.
4. At the end of each phase, run the phase's verification task.
5. Don't defer to any external process document.

### 4.1 STOP 2: Ask the User to Test

When all implementation work is done and locally verified, explain specifically how to test — what commands to run, what to click, what to observe, what the expected outcome is. Then ask:

> "Please test it using the steps above and let me know when you're done, or if you found any issues."

Wait for the response.

- **If they confirm** ("done", "looks good", "yes", "perfect"): proceed immediately to Section 5.0.
- **If they report issues**: fix them, then ask "Can I review and finalize?" Keep fixing and re-asking until confirmed. Always push forward.

---

## 5.0 REVIEW AND FINALIZE
**Runs autonomously once the user confirms.**

### 5.1 Review

**CRITICAL: Actually perform the review before writing the file. Don't write `review.md` first and call it done.**

1. Re-read `spec.md` and `plan.md`.
2. Run `git diff` and read every changed file relevant to the thread — evaluate each across five axes:
   1. **Correctness** — does it match the spec, handle edge cases, cover error paths?
   2. **Readability** — clear names, no unnecessary complexity, logic easy to follow?
   3. **Architecture** — fits existing patterns, no circular deps, right abstraction level?
   4. **Security** — input validated at boundaries, no secrets in code, auth checked?
   5. **Performance** — N+1 queries, unbounded loops, missing pagination?
3. Run the relevant test suite or verification commands and read the output.
4. Check for dead code introduced or orphaned by this thread — unused functions, replaced components, unreferenced constants. List them explicitly as findings; do not delete without noting them.
5. For each of the following, read the relevant code and report what you found — don't skip any:
   - **Spec coverage:** Does every requirement in `spec.md` have a corresponding implementation?
   - **Plan completion:** Is every task in `plan.md` marked done and actually implemented?
   - **Code correctness:** Are there logic errors, missing cases, or broken assumptions?
   - **Architecture decisions:** Were the decisions recorded in `plan.md` actually followed? If any were deviated from, is the deviation noted?
   - **Test coverage:** Do the tests verify the key behaviors in the spec?
   - **Regressions:** Could any change break existing behavior?
6. For each finding, state severity, file and line, what's wrong, why it matters, and the recommended fix. Severity definitions:
   - `blocking` — broken functionality, data loss, security hole. Must fix before finalizing.
   - `major` — significant correctness or architecture issue. Must fix before finalizing.
   - `minor` — worth fixing but not critical. Fix unless explicitly deferred.
   - `nit` — style or preference. May be skipped.
7. After the agent review is done, run CodeRabbit review if available (`coderabbit review --agent`). Incorporate any findings.
8. Fix any blocking or major findings immediately. Re-run verification after each fix. Repeat until none remain.
9. Make sure `plan.md` reflects the actual state of the work.
10. Then write `kamma/threads/<thread_id>/review.md` with the following sections:

   ```
   ## Thread
   - **ID:** <thread_id>
   - **Objective:** <one-line from spec.md>

   ## Files Changed
   - `path/to/file` — one-line purpose of the change
   - ...

   ## Findings
   | # | Severity | Location | What | Why | Fix |
   |---|----------|----------|------|-----|-----|
   | 1 | major | `file:line` | ... | ... | ... |

   Or: "No findings."

   ## Fixes Applied
   - What was fixed during review (or "None")

   ## Test Evidence
   - `<command>` → pass/fail
   - ...

   ## Verdict
   PASSED | BLOCKED
   - Review date: YYYY-MM-DD
   - Reviewer: kamma (inline)
   ```

   Target ~30-50 lines. Concise but complete enough for a future agent to understand what happened without re-running checks.

### 5.2 Finalize

1. If `kamma/project.md` exists and the thread changed something significant about the project, update it. If the file doesn't exist, don't create it.
2. If `kamma/tech.md` exists and the thread changed tools, constraints, or working assumptions, update it. If the file doesn't exist, don't create it.
3. Ensure `kamma/archive/` exists.
4. Copy `kamma/threads/<thread_id>/` to `kamma/archive/<thread_id>/`. If that path exists, pick a unique variant.
5. Delete `kamma/threads/<thread_id>/` and all its contents.
6. If `kamma/threads.md` exists, delete it — legacy file.
7. Announce that the thread is complete.

### 5.3 GitHub Issue and Commit

**If the thread references a GitHub issue** (in the description, `spec.md`, or `plan.md`):

1. Extract the issue number.
2. Summarize the fix in 2–4 sentences: what the issue was, what changed, how it was verified.
3. Post the summary: `gh issue comment <number> --body "<summary>"`
4. Close the issue: `gh issue close <number>`

**Always suggest a commit message and description (do NOT run `git commit`):**
- One-line commit message summarizing what changed. If a GitHub issue was referenced, include it: e.g., `fix: ensure consistent commit descriptions (closes #123)`
- Bulleted description listing each distinct change. One bullet per change — no prose paragraphs.
- Present both:
  > **Commit message:** `<message>`
  > **Commit description:**
  > - bullet 1
  > - bullet 2
  > - ...

### 5.4 Reflect and Learn
**Run autonomously. Keep the user informed but don't ask for approval.**

1. Reflect on the conversation. Look for moments where:
   - The user had to correct you or repeat an instruction (`[REPEATED]`)
   - There was process friction or wasted effort (`[WORKFLOW]`)
   - You misunderstood something (`[CONFUSION]`)
   - You violated a rule or missed an expected action (`[BEHAVIOR]`)
   - Something worked particularly well (`[POSITIVE]`)
2. If nothing notable happened, skip the rest of this section.
3. Append each observation as a one-liner to `kamma/lessons.md` (create if needed):
   ```
   - YYYY-MM-DD [TAG] Short description of what happened
   ```
   No headers, no preamble, no "no lessons" entries. Just the lines.
4. Read the full `kamma/lessons.md`. For each lesson that suggests a concrete, lasting improvement, classify it:
   - `local`: specific to this repo, its workflow, or its conventions
   - `global`: useful across projects
5. Write to the right target:
   - **Local** → repo root instruction file (prefer `AGENTS.md`, then `AGENT.md`, then `CLAUDE.md`; create `AGENTS.md` if none exist)
   - **Global** → use this discovery order, pick the first that exists:
     1. `~/.agents/AGENTS.md` (cross-agent shared instructions)
     2. The running agent's own global file:

        | CLI Agent    | Global instruction file              |
        |--------------|--------------------------------------|
        | Claude Code  | `~/.claude/CLAUDE.md`                |
        | Codex        | `~/.codex/AGENTS.md`                 |
        | Gemini CLI   | `~/.gemini/GEMINI.md`                |
        | Kilo Code    | `~/.config/kilocode/AGENTS.md`       |
        | OpenCode     | `~/.config/opencode/AGENTS.md`       |
        | Qwen Code    | `~/.qwen/QWEN.md`                    |

     3. If neither exists, create `~/.agents/AGENTS.md`.
6. Keep additions minimal: one or two sentences per rule. Tell the user which file you updated and why.
7. If no improvements apply, say nothing and move on.
