---
description: Reviews a thread and gets it ready to finish
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven development framework. Your current task is to review a thread that has already been implemented and is ready for a fresh check. You MUST follow this process precisely.

CRITICAL: Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

TO-DO LIST: Keep a to-do list for this entire command. Add the current section's work before you start it, update the list as you go, and use it to track progress until the command is complete.
At the end of every section in this file, tick off completed to-do items before you move on.

---

## 1.1 SETUP CHECK
**Verify that the Kamma environment is properly set up.**

1.  **Check for Required Files:** You MUST verify the existence of the following files in the `kamma` directory:
    -   `kamma/tech.md`
    -   `kamma/workflow.md`
    -   `kamma/project.md`
    -   `kamma/threads.md`

2.  **Handle Missing Files:**
    -   If any of these files are missing, say what is missing, look for another sensible way to continue, and keep going if you still can.
    -   Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment."
    -   Continue if there is still a reasonable path forward.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 2.0 CHOOSE A THREAD
**Identify and select the thread to review.**

1.  **Check for User Input:** First, check if the user provided a thread name as an argument (for example, `/kamma:3-review <thread_description>`).

2.  **Parse Threads File:** Read and parse `kamma/threads.md`. Split content by the `---` separator to identify each thread section. For each section, extract the status (`[ ]`, `[~]`, `[x]`), the thread description (from the `##` heading), and the link to the thread folder.
    -   **CRITICAL:** If no thread sections are found, announce: "The threads file is empty or malformed. No threads are available to review." Then look for another sensible source of thread information, and if none exists, explain that clearly and move on.

3.  **Select Thread:**
    -   **If a thread name was provided:**
        1.  Perform an exact, case-insensitive match against thread descriptions.
        2.  If a unique match is found, confirm with the user.
        3.  If no match or ambiguous, inform the user and suggest the next review-ready thread.
    -   **If no thread name was provided:**
        1.  Find the first thread marked `[~]`.
        2.  Announce: "Automatically selecting the in-progress thread for review: '<thread_description>'."
        3.  If no in-progress threads exist, say that there is no active thread ready for review, suggest the next sensible action, and continue as far as you reasonably can.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 3.0 START THE REVIEW
**Begin the review immediately.**

1.  **State the Goal:** Announce that this command is meant to give the selected thread a fresh review and then continue straight into the review.

2.  **Independence Note:** If the current reviewer appears to be the same agent or tool that did the implementation, note briefly that the review is less independent, but continue without stopping for approval.

3.  **No Reviewer-Selection Stop:** Do not add any reviewer-selection gate before the review starts.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 4.0 LOAD THREAD CONTEXT
**Build enough context before writing findings.**

1.  **Identify Thread Folder:** Get the `<thread_id>` from the threads file link.

2.  **Read Required Files:**
    -   `kamma/threads/<thread_id>/spec.md`
    -   `kamma/threads/<thread_id>/plan.md`
    -   `kamma/workflow.md`
    -   `kamma/project.md`
    -   `kamma/tech.md`

3.  **Inspect Implementation Evidence:**
    -   Review the current git diff and recent commits relevant to the thread.
    -   Review changed files related to the thread.
    -   Review recent test or lint outputs if available.

4.  **Summarize What Changed:** Summarize the thread in a compact structure covering:
    -   Thread objective
    -   Planned scope
    -   Implemented scope
    -   Files changed
    -   Tests run
    -   Known risks or assumptions

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 5.0 HOW TO REVIEW IT
**Use more than a quick diff scan.**

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
    -   UX or user-behavior review
    -   Manual scenario testing
    -   Documentation review

4.  **Scope Rule:** Only apply additional review modes that are relevant to the actual thread.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 6.0 HOW TO WRITE FINDINGS
**Findings come before summary comments.**

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


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 7.0 FIX WHAT NEEDS FIXING
**Review is not done until valid findings are addressed.**

1.  **Implementation Requirement:** If blocking or major findings are identified, they MUST be implemented before the thread can be considered complete.

2.  **Minor Findings:** Minor issues should also be addressed unless the user explicitly defers them.

3.  **Re-Verification:** After changes are implemented, rerun the relevant verification steps and update the review conclusion.

4.  **Completion Rule:** Do NOT declare the thread review-complete while unresolved blocking findings remain.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 8.0 WRITE `review.md`
**Save the review result as a file.**

1.  **Write `review.md`:** Once the review is complete (all blocking/major findings resolved or no findings), write a summary file to `kamma/threads/<thread_id>/review.md` containing:
    -   Review date
    -   Reviewer identity (agent/tool name)
    -   Review methods used
    -   Findings summary (count by severity, or "No findings")
    -   Verdict: `PASSED` or `BLOCKED`

2.  **Do NOT write `review.md` if blocking findings remain unresolved.** The absence of this file signals that the thread has not cleared review.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 9.0 NEXT STEP
**Only move to the finish step after review is clear.**

1.  **If Findings Were Resolved Successfully:** Instruct the user to run `/kamma:4-finalize` to complete the thread.

2.  **If Review Is Clear:** State that the thread is review-complete and ready for `/kamma:4-finalize`.

3.  **If Review Is Blocked:** Clearly state what must happen before review can continue.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.
