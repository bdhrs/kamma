---
description: Finalizes a reviewed thread, updates project documentation, and handles cleanup
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to finish a thread that has passed review and is ready to close out. Follow this process precisely.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way to make progress, reassess, and keep going. Tell the user about important failures, but keep working unless the task truly cannot move forward.

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

---

## 3.0 FINISH THE THREAD

1. Verify that `kamma/threads/<thread_id>/review.md` exists and has a `PASSED` verdict. If not, explain that review hasn't cleared, point to `/kamma:3-review`, and continue only with non-blocking cleanup.

2. Announce that the thread is complete.

3. Summarize the implementation, review outcome, and verification evidence.

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
- One-line commit message summarizing what changed. If a GitHub issue was referenced, include it: e.g., `fix: <description> (closes #<number>)`
- Bulleted description listing each distinct change. One bullet per change — no prose paragraphs.
- Present both:
  > **Commit message:** `<message>`
  > **Commit description:**
  > - bullet 1
  > - bullet 2
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
