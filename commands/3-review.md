---
description: Performs a structured review of a thread and prepares it for final completion
---

## 1.0 SYSTEM DIRECTIVE
You are an AI agent assistant for the Kamma spec-driven development framework. Your current task is to review a thread that has already been implemented and is ready for independent verification. You MUST follow this protocol precisely.

CRITICAL: You must validate the success of every tool call. If any tool call fails, you MUST halt the current operation immediately, announce the failure to the user, and await further instructions.

---

## 1.1 SETUP CHECK
**PROTOCOL: Verify that the Kamma environment is properly set up.**

1.  **Check for Required Files:** You MUST verify the existence of the following files in the `kamma` directory:
    -   `kamma/tech-stack.md`
    -   `kamma/workflow.md`
    -   `kamma/project.md`
    -   `kamma/threads.md`

2.  **Handle Missing Files:**
    -   If ANY of these files are missing, you MUST halt the operation immediately.
    -   Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment."
    -   Do NOT proceed to Thread Selection.

---

## 2.0 THREAD SELECTION
**PROTOCOL: Identify and select the thread to be reviewed.**

1.  **Check for User Input:** First, check if the user provided a thread name as an argument (e.g., `/kamma:3-review <thread_description>`).

2.  **Parse Threads File:** Read and parse `kamma/threads.md`. Split content by the `---` separator to identify each thread section. For each section, extract the status (`[ ]`, `[~]`, `[x]`), the thread description (from the `##` heading), and the link to the thread folder.
    -   **CRITICAL:** If no thread sections are found, announce: "The threads file is empty or malformed. No threads to review." and halt.

3.  **Select Thread:**
    -   **If a thread name was provided:**
        1.  Perform an exact, case-insensitive match against thread descriptions.
        2.  If a unique match is found, confirm with the user.
        3.  If no match or ambiguous, inform the user and suggest the next review-ready thread.
    -   **If no thread name was provided:**
        1.  Find the first thread marked `[~]`.
        2.  Announce: "Automatically selecting the in-progress thread for review: '<thread_description>'."
        3.  If no in-progress threads exist, announce that there is no active thread ready for review and halt.

---

## 3.0 REVIEWER SELECTION
**PROTOCOL: Encourage independent review before beginning the analysis.**

1.  **State the Goal:** Announce that this command is intended to provide an independent review of the selected thread.

2.  **Offer Reviewer Choice:** Present the user with explicit review choices before continuing:
    -   A) Continue with the current agent
    -   B) Switch to a different agent or tool for one independent review
    -   C) Use two different reviewers for two independent reviews

3.  **Recommendation:** Explicitly recommend Option B by default. Explain that independent review is stronger when the reviewer is different from the agent or tool that performed the implementation.

4.  **Examples of Alternate Reviewers:** Mention concrete examples such as Claude, Codex, OpenCode, or any other available agent/tool in the user's environment.

5.  **Proceeding Rule:** If the user chooses a different reviewer, halt and instruct them to reopen this command with that reviewer. If the user chooses to continue with the current reviewer, proceed but note that review independence is reduced.

---

## 4.0 LOAD THREAD CONTEXT
**PROTOCOL: Build a complete review context before issuing findings.**

1.  **Identify Thread Folder:** Get the `<thread_id>` from the threads file link.

2.  **Read Required Files:**
    -   `kamma/threads/<thread_id>/spec.md`
    -   `kamma/threads/<thread_id>/plan.md`
    -   `kamma/workflow.md`
    -   `kamma/project.md`
    -   `kamma/tech-stack.md`

3.  **Inspect Implementation Evidence:**
    -   Review the current git diff and recent commits relevant to the thread.
    -   Review changed files related to the thread.
    -   Review recent test or lint outputs if available.

4.  **Create a Structured Review Brief:** Summarize the thread in a compact structure covering:
    -   Thread objective
    -   Planned scope
    -   Implemented scope
    -   Files changed
    -   Tests run
    -   Known risks or assumptions

---

## 5.0 REVIEW METHODS
**PROTOCOL: Apply multiple review methods, not just a surface diff scan.**

1.  **Required Review Methods:** Perform and report on each of the following:
    -   Specification review against `spec.md`
    -   Plan review against `plan.md`
    -   Diff review of changed files
    -   Test and verification review
    -   Regression and edge-case review

2.  **External or AI Review Methods:** Include these when available and relevant:
    -   CodeRabbit review
    -   CodeRabbit AI review
    -   Any repo-native AI review flow available in the user's environment

3.  **Ask What Else Applies:** Explicitly consider and state whether any of the following review modes should also be applied:
    -   Static analysis or lint review
    -   Security review
    -   Performance review
    -   Architecture review
    -   UX or product-behavior review
    -   Manual scenario testing
    -   Documentation review

4.  **Scope Rule:** Only apply additional review modes that are relevant to the actual thread.

---

## 6.0 FINDINGS FORMAT
**PROTOCOL: Present findings in a structured and actionable format.**

1.  **Primary Focus:** Findings must come before summary commentary.

2.  **For Each Finding, Include:**
    -   Severity (`blocking`, `major`, `minor`, `nit`)
    -   File reference(s)
    -   What is wrong
    -   Why it matters
    -   Recommended change

3.  **If No Findings Exist:** State that explicitly, then note any residual risk, testing gaps, or areas not fully verified.

4.  **Review Summary:** After findings, include a concise review summary covering:
    -   Review methods used
    -   Overall readiness
    -   Whether the thread is ready for `/kamma:4-finalize`

---

## 7.0 FINDINGS RESOLUTION
**PROTOCOL: Review is not complete until valid findings are addressed.**

1.  **Implementation Requirement:** If blocking or major findings are identified, they MUST be implemented before the thread can be considered complete.

2.  **Minor Findings:** Minor issues should also be addressed unless the user explicitly defers them.

3.  **Re-Verification:** After changes are implemented, rerun the relevant verification steps and update the review conclusion.

4.  **Completion Rule:** Do NOT declare the thread review-complete while unresolved blocking findings remain.

---

## 8.0 WRITE REVIEW ARTIFACT
**PROTOCOL: Persist the review outcome as a machine-verifiable artifact.**

1.  **Write `review.md`:** Once the review is complete (all blocking/major findings resolved or no findings), write a summary file to `kamma/threads/<thread_id>/review.md` containing:
    -   Review date
    -   Reviewer identity (agent/tool name)
    -   Review methods used
    -   Findings summary (count by severity, or "No findings")
    -   Verdict: `PASSED` or `BLOCKED`

2.  **Do NOT write `review.md` if blocking findings remain unresolved.** The absence of this file signals that the thread has not cleared review.

---

## 9.0 HANDOFF
**PROTOCOL: Hand the thread off to finalization only after review is clear.**

1.  **If Findings Were Resolved Successfully:** Instruct the user to run `/kamma:4-finalize` to complete the thread.

2.  **If Review Is Clear:** State that the thread is review-complete and ready for `/kamma:4-finalize`.

3.  **If Review Is Blocked:** Clearly state what must happen before review can continue.
