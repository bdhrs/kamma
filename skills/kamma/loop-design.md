# Kamma Loop Design

A "loop" thread is a standing thread designed for repeated feedback loops or issue processing, rather than a finite feature implementation.

## The Loop Workflow

1. **Reporting:** Each session starts with the user reporting an issue, bug, or providing findings/outputs from a previous real test.
2. **Analysis:** An advanced model analyzes the report and suggests a focused implementation plan.
3. **Approval (Hard Stop):** Once the plan is drafted, there is a hard stop to wait for the user to approve the plan.
4. **Execution Switch:** After approval, the user switches to an execution model (often a faster tier) to perform the actual implementation.
5. **Implementation & Verification:** The execution model implements the approved plan and runs all necessary tests.
6. **Broad Testing:** The execution model is encouraged to run other old, relevant tests in the codebase during this stage to ensure no regressions.
7. **Next Cycle:** The cycle completes. The next session starts again at Step 1 with the user reporting a new issue or providing new test outputs for the advanced model to analyze.

## Loop Thread File Structure

A loop thread lives under `kamma/threads/<thread_id>/` and uses the following files:

```
kamma/threads/<thread_id>/
  spec.md        Standing scope — what domain this loop governs, analysis standards, execution constraints
  plan.md        Standing protocol — the per-cycle process (one issue at a time), not a finite task list
  handoff.md     Session continuity — which cycle completed last, what to read to rejoin context
  cycles/        Per-cycle records (one file per analysis + implementation session)
    001.md        First cycle: reported issue, analysis, approved plan, implementation summary, test results
    002.md        Second cycle
    ...
```

### spec.md (Standing Scope)

Describes the persistent domain, not a single issue. Covers:
- The area the loop governs (e.g., "Pāḷi analyzer export bug fixes")
- Analysis standards (what the analysis phase must check before proposing a plan)
- Execution constraints (test requirements, code boundaries, never-change rules)

Unlike a normal thread, `spec.md` stays stable across cycles. It is edited only when the scope itself changes.

### plan.md (Standing Protocol)

Establishes the per-cycle workflow, not a one-time task list:
- "Read `handoff.md` to rejoin context"
- "Read `spec.md` for scope and constraints"
- "Analyze the reported issue and draft a focused implementation plan in `cycles/NNN.md`"
- "Hard stop for user approval before any code changes"
- "Implement only the approved plan, verify locally, run broad regression tests"
- "Update `handoff.md` with completed cycle number and next step"

There is no finite end; the plan remains open until the user explicitly closes the loop.

### handoff.md (Session Continuity)

Minimal state so any agent can rejoin. At minimum records:
- Last completed cycle number
- Path to the last cycle file for full context
- Next step (e.g., "Awaiting new issue report for analysis phase")

Example:
```
Cycles completed: 001 through 008
Last cycle: cycles/008.md — resolved Findings #71-74
Next step: Awaiting new issue report. Read spec.md for scope, then proceed to analysis phase.
```

### cycles/ Directory

One file per cycle (session), named sequentially: `001.md`, `002.md`, etc. Each contains:
- **Issue reported** — what the user brought in this cycle
- **Analysis** — the model's assessment and proposed plan
- **Approval status** — user's decision (approved / rejected with feedback / pivoted)
- **Implementation summary** — what was changed and why
- **Test results** — verification output, regression test results

Each cycle file is the authoritative record of that session and is read by the next session's analysis phase to maintain continuity.

## Working with Loops

- **Planning (`/kamma:1-plan`):** If the user mentions creating a "loop", tailor your questions to set up the standing scope. Write `spec.md` for the domain and `plan.md` for the per-cycle protocol. Create the `cycles/` directory and initialize `handoff.md`.
- **Executing (`/kamma:2-do`):** Read `handoff.md` and the last cycle file to rejoin context. Read `spec.md` for standing constraints. Execute only the approved active cycle. Respect the hard stop before code changes. After implementation and testing, write the new cycle record and update `handoff.md`.
- **Review & Finalize (`/kamma:3-review`, `/kamma:4-finalize`):** Operate normally when the user eventually decides to close the standing loop. Archive the full cycles/ history into the final review.
