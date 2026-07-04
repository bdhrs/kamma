---
description: Finalizes a reviewed thread, updates project documentation, and handles cleanup
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to finish a thread that has passed review and is ready to close out. Follow this process precisely.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way to make progress, reassess, and keep going. Tell the user about important failures, but keep working unless the task truly cannot move forward.

**COMPLETION GATE — finalize runs to the end once started.** Sections 3.0 through 6.0 are all mandatory steps, not a menu: doing the project-docs update but skipping the archive, GitHub, or reflect/lessons steps is an *incomplete* finalize. Marking a `plan.md` "Finalize" checkbox — or writing a wrap-up summary that calls the thread done — is **not** the same as executing these sections; the box may only be ticked after every section below has actually run. If a section legitimately doesn't apply (e.g. no GitHub issue is referenced), say so explicitly and move on — never skip a section silently.

TO-DO LIST: Keep a running to-do list for this command. Add work before you start it, tick items off as you finish them. You don't need a reminder every section — just keep the list current.

Verify `kamma/project.md`, `kamma/tech.md`, and `kamma/workflow.md` exist. If any are missing, say what's missing, announce that Kamma is not set up (`/kamma:0-setup`), and continue if there's still a reasonable path.

---
## 2.0 CHOOSE A THREAD

1. Check if the user provided a thread name as an argument.

2. List all directories in `kamma/threads/`. For each, read `spec.md` for the description and check for `review.md` with a `PASSED` verdict.
   - If no threads exist: "No active threads found. Nothing to finalize." Then stop.

3. **Select:**
   - **If a name was provided:** Case-insensitive match against directory names and spec descriptions. Confirm if unique. If ambiguous, list the options.
   - **If no name:** Pick the first thread with a `PASSED` review. Announce: "Automatically selecting the review-passed thread: '<description>'." If none have passed, say so and suggest `/kamma:3-review`.

4. **Loop Threads:**
   If the `spec.md` or `plan.md` contains the marker `> **Thread type:** Loop (standing thread)` OR a `cycles/` directory exists:
   - **Do not archive per cycle:** A loop thread is only finalized when the user explicitly declares it complete according to its `spec.md`.
   - If the user HAS declared it complete, proceed with finalize, but in the **Reflect and Learn** step (6.0), promote ONLY workflow-general or repo-general lessons from `learnings.md` into `kamma/lessons.md`. Task-specific lessons stay with the archived loop.

---

## 3.0 FINISH THE THREAD

1. Verify that `kamma/threads/<thread_id>/review.md` exists and has a `PASSED` verdict. If not, explain that review hasn't cleared, point to `/kamma:3-review`, and continue only with non-blocking cleanup.

2. Read the detailed content from `review.md` — specifically the Files Changed, Findings, Fixes Applied, and Test Evidence sections. Use this context (along with `spec.md`) to build the wrap-up summary instead of re-running checks or relying only on the spec.

3. Announce that the thread is complete.

4. Summarize: thread objective, files changed, findings and fixes (from review.md), test evidence, and final verdict.

---

## 4.0 UPDATE PROJECT DOCS

1. Read `kamma/threads/<thread_id>/spec.md`, `kamma/project.md`, and `kamma/tech.md`.

2. If the thread significantly changes the project description, propose changes to `kamma/project.md` and get user confirmation before applying.

3. If the thread changed tools, constraints, or working assumptions, propose changes to `kamma/tech.md` and get confirmation.

4. Summarize what was updated, or say no updates were needed.

---

## 5.0 CLEAN UP THE THREAD

1. Ensure `kamma/archive/` exists.
2. Copy `kamma/threads/<thread_id>/` to `kamma/archive/<thread_id>/`. If that path exists, pick a unique variant.
3. Delete `kamma/threads/<thread_id>/` and its contents.
4. If `kamma/threads.md` exists, delete it — legacy file.
5. Report where the thread was archived.

---

## 5.5 GITHUB ISSUE
**Skip entirely if no issue is referenced.**

**If the thread references a GitHub issue** (in the description, `spec.md`, `plan.md`, or archived copies):

1. Summarize the fix in 2–4 sentences.
2. Post: `gh issue comment <number> --body "<summary>"`
3. Close: `gh issue close <number>`

**Always suggest a commit message and description (do NOT run `git commit`):**
- One concise commit message line in imperative mood, lowercase first word, under 72 characters. If a GitHub issue was referenced, include it: e.g., `fix: <description> (closes #<number>)`
- Bulleted description explaining what changed and why. One bullet per change, each a single long line — however long, never manually wrapped or split across lines. One clause only — no "and"-chains, no semicolons, no parentheticals. Go down the page, not across it.
- Bulleted list of only the files changed as part of this thread's work — not every file in the working tree. Cross-check `git status --short` / `git diff --name-only` against the thread's `plan.md` tasks and exclude unrelated changes. Sort alphabetically by full path (folder, then subfolder, then file).
- Present all three:
  > **Commit message:** `<message>`
  > **Commit description:**
  > - bullet 1
  > - bullet 2
  > - ...
  >
  > **Files changed:**
  > - `path/to/file1`
  > - `path/to/file2`
  > - ...

---

## 6.0 REFLECT AND LEARN
**Run autonomously. Keep the user informed but don't ask for approval.**

1. Reflect on this session. Look for moments where:
   - The user had to correct you or repeat an instruction (`[REPEATED]`)
   - There was process friction or wasted effort (`[WORKFLOW]`)
   - You misunderstood something (`[CONFUSION]`)
   - You violated a rule or missed an expected action (`[BEHAVIOR]`)
   - Something worked particularly well (`[POSITIVE]`)

2. If nothing notable, skip the rest.

3. Append each observation to `kamma/lessons.md` (create if needed):
   ```
   - YYYY-MM-DD [TAG] Short description of what happened
   ```
   No headers, no preamble. Just the lines.

4. Read the full `kamma/lessons.md`. For each lesson that suggests a lasting improvement, classify:
   - `local`: specific to this repo
   - `global`: useful across projects

5. Write to the right target:
   - **Local** → repo root instruction file (`AGENTS.md` > `AGENT.md` > `CLAUDE.md`; create `AGENTS.md` if none exist)
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

6. Keep additions minimal. Tell the user which file and why.

7. If no improvements apply, say nothing.

8. Recurring or cross-repo patterns (the same lesson piling up across threads or projects) are not for this step — they are consolidated into the kamma framework itself by `/kamma:improve`. Leave them in `lessons.md` for that pass.
