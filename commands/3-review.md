---
description: Reviews a thread and gets it ready to finish
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to review a thread that has been implemented and is ready for a fresh check. Follow this process precisely.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way to make progress, reassess, and keep going. Tell the user about important failures, but keep working unless the task truly cannot move forward.

TO-DO LIST: Keep a running to-do list for this command. Add work before you start it, tick items off as you finish them. You don't need a reminder every section — just keep the list current.

Verify `kamma/project.md`, `kamma/tech.md`, and `kamma/workflow.md` exist. If any are missing, say what's missing, announce that Kamma is not set up (`/kamma:0-setup`), and continue if there's still a reasonable path.

---

## 2.0 CHOOSE A THREAD

1. Check if the user provided a thread name as an argument.

2. List all directories in `kamma/threads/`. For each, read `spec.md` for the description, `plan.md` for progress, and `review.md` if it exists to check whether review already passed.
   - If no threads exist: "No active threads found. Nothing to review." Then stop.

3. **Select:**
   - **If a name was provided:** Case-insensitive match against directory names and spec descriptions. Confirm if unique. If ambiguous, list the options.
   - **If no name:** Prefer the first thread with `[~]` tasks. If none, pick the first active thread without a `PASSED` review. Announce which fallback you used. If every thread already passed, say so and suggest the next step.

---

## 3.0 START THE REVIEW

1. Announce that you're reviewing the selected thread and continue straight into it.
2. If you appear to be the same agent that did the implementation, note briefly that the review is less independent, but don't stop.
3. No reviewer-selection gate — just start.

---

## 4.0 LOAD THREAD CONTEXT

1. Read:
   - `kamma/threads/<thread_id>/spec.md`
   - `kamma/threads/<thread_id>/plan.md`
   - `kamma/workflow.md`
   - `kamma/project.md`
   - `kamma/tech.md`
   - Verify any GitHub issue reference is visible and consistent.

2. Inspect the implementation:
   - Review the git diff and recent commits relevant to the thread.
   - Review changed files — evaluate each across five axes:
     1. **Correctness** — does it match the spec, handle edge cases, cover error paths?
     2. **Readability** — clear names, no unnecessary complexity, logic easy to follow?
     3. **Architecture** — fits existing patterns, no circular deps, right abstraction level?
     4. **Security** — input validated at boundaries, no secrets in code, auth checked?
     5. **Performance** — N+1 queries, unbounded loops, missing pagination?
   - Review test or lint outputs if available.
   - Check for dead code introduced or orphaned by this thread — unused functions, replaced components, unreferenced constants. List them explicitly as findings; do not delete without noting them.

3. Summarize what changed:
   - Thread objective
   - Planned vs. implemented scope
   - Files changed
   - Tests run
   - Known risks or assumptions

---

## 5.0 HOW TO REVIEW

**Go deeper than a quick diff scan.**

1. **Required methods** — perform and report on each:
   - Spec review against `spec.md`
   - Plan review against `plan.md` — including whether architecture decisions were followed. If any were deviated from, is the deviation noted?
   - Diff review of changed files
   - Test and verification review
   - Regression and edge-case review

2. **After the agent review is done**, run CodeRabbit review if available (`coderabbit review --agent`). Include any repo-native AI review flow that applies.

3. **Consider whether these also apply** — state your reasoning:
   - Static analysis or lint
   - Security
   - Performance
   - Architecture
   - UX or user behavior
   - Manual scenario testing
   - Documentation

4. Only apply additional modes that are actually relevant to this thread.

---

## 6.0 WRITE FINDINGS

**Findings first, then summary.**

Severity definitions:
- `blocking` — broken functionality, data loss, security hole. Must fix before finalizing.
- `major` — significant correctness or architecture issue. Must fix before finalizing.
- `minor` — worth fixing but not critical. Fix unless explicitly deferred.
- `nit` — style or preference. May be skipped.

1. For each finding:
   - Severity: `blocking`, `major`, `minor`, `nit`
   - File reference(s)
   - What's wrong
   - Why it matters
   - Recommended fix

2. If no findings: say so explicitly. Note any residual risk, testing gaps, or areas not fully verified.

3. After findings, write a concise summary:
   - Review methods used
   - Overall readiness
   - Whether the thread is ready for `/kamma:4-finalize`

---

## 7.0 FIX WHAT NEEDS FIXING

1. Blocking and major findings must be fixed before the thread can be considered complete.
2. Minor issues should also be fixed unless the user explicitly defers them.
3. After fixes, rerun the relevant verification and update the review conclusion.
4. Don't declare review-complete while unresolved blocking findings remain.

---

## 8.0 WRITE `review.md`

Once the review is complete (all blocking/major resolved, or no findings), write `kamma/threads/<thread_id>/review.md` with the following sections:

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
- Reviewer: <identity>
```

Target ~30-50 lines. Keep it concise but complete enough for a future agent to understand what happened without re-running checks.

Don't write `review.md` if blocking findings remain. The absence of the file signals review hasn't cleared.

---

## 9.0 NEXT STEP

- **Findings resolved:** Tell the user to run `/kamma:4-finalize`.
- **Review clear:** State the thread is ready for `/kamma:4-finalize`.
- **Review blocked:** State clearly what must happen first.
