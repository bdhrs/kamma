---
description: Finalizes a reviewed thread, updates project documentation, and handles cleanup
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven development framework. Your current task is to finish a thread that has already passed review and is ready to be closed out. You MUST follow this process precisely.

CRITICAL: Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

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

## 2.0 CHOOSE A THREAD
**Identify and select the thread to finish.**

1.  **Check for User Input:** First, check if the user provided a thread name as an argument (for example, `/kamma:4-finalize <thread_description>`).

2.  **Parse Threads File:** Read and parse `kamma/threads.md`. Split content by the `---` separator to identify each thread section. For each section, extract the status (`[ ]`, `[~]`, `[x]`), the thread description (from the `##` heading), and the link to the thread folder.
    -   **CRITICAL:** If no thread sections are found, announce: "The threads file is empty or malformed. No threads are available to finalize." Then look for another sensible source of thread information, and if none exists, explain that clearly and move on.

3.  **Select Thread:**
    -   **If a thread name was provided:**
        1.  Perform an exact, case-insensitive match against thread descriptions.
        2.  If a unique match is found, confirm with the user.
        3.  If no match or ambiguous, inform the user and suggest the next review-cleared thread.
    -   **If no thread name was provided:**
        1.  Find the first thread marked `[~]`.
        2.  Announce: "Automatically selecting the in-progress thread to finish: '<thread_description>'."
        3.  If no in-progress threads exist, say that there is no active thread ready to finish, suggest the next sensible action, and continue as far as you reasonably can.

---

## 3.0 FINISH THE THREAD
**Only finish a thread that has already passed review.**

1.  **Make Sure Review Passed:** Verify that `kamma/threads/<thread_id>/review.md` exists and contains a `PASSED` verdict.
    -   If the file does not exist or the verdict is `BLOCKED`, explain that review has not cleared the thread yet, point the user to `/kamma:3-review`, and keep going only with any non-blocking cleanup or context you can still provide.

2.  **Finalize Thread Status:**
    -   Update the thread's status in `kamma/threads.md` from `[~]` to `[x]`.
    -   Announce that the thread is now complete.

3.  **Wrap-Up Summary:**
    -   Summarize the implementation, review outcome, and any final verification evidence that supports completion.

---

## 4.0 UPDATE PROJECT DOCS
**Update project-level docs based on the completed thread.**

1.  **Load Thread Specification:** Read `kamma/threads/<thread_id>/spec.md`.

2.  **Load Project Documents:** Read:
    -   `kamma/project.md`
    -   `kamma/tech.md`

3.  **Analyze and Update:**
    a.  **Update `kamma/project.md`:** If the completed thread significantly changes the project description, propose changes and get user confirmation before applying.
    b.  **Update `kamma/tech.md`:** If the thread changed the tools, who this is for, constraints, resources, or working assumptions, propose changes and get user confirmation before applying.

4.  **Final Report:** Summarize what was updated, or say that no updates were needed.

---

## 5.0 CLEAN UP THE THREAD
**Offer to archive or delete the completed thread.**

1.  **Ask for User Choice:**
    > "Thread '<thread_description>' is now complete. What would you like to do?
    > A.  **Archive:** Move to `kamma/archive/` and remove from the threads file.
    > B.  **Delete:** Permanently delete the thread folder and remove it from the threads file.
    > C.  **Skip:** Leave it in the threads file."

2.  **Handle User Response:**
    *   **If "A" (Archive):** Create `kamma/archive/` if needed, move the thread folder there, remove it from `kamma/threads.md`.
    *   **If "B" (Delete):** Ask for final confirmation, then delete the thread folder and remove it from `kamma/threads.md`.
    *   **If "C" (Skip):** Leave the completed thread as-is.
