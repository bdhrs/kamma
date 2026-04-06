---
description: Finalizes a reviewed thread, updates project documentation, and handles cleanup
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven development framework. Your current task is to finish a thread that has already passed review and is ready to be closed out. You MUST follow this process precisely.

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


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


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


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


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


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 5.0 CLEAN UP THE THREAD
**Archive the completed thread automatically.**

1.  **Archive by Default:**
    -   Ensure `kamma/archive/` exists.
    -   Move the completed thread folder to `kamma/archive/`.
    -   Remove the thread entry from `kamma/threads.md`.
    -   If the archive path already exists, choose a unique variant and continue.

2.  **Report the Result:**
    -   Announce where the thread was archived and confirm that it was removed from the active threads file.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 6.0 REFLECT AND LEARN
**Run autonomously. Keep the user informed but do not ask for approval.**

1.  **Reflect on This Session:** Review the conversation that just happened. Identify moments where:
    -   The user had to correct you or repeat an instruction (`[REPEATED]`)
    -   There was process friction or wasted effort (`[WORKFLOW]`)
    -   You misunderstood something (`[CONFUSION]`)
    -   You violated a rule or missed an expected action (`[BEHAVIOR]`)
    -   Something worked particularly well (`[POSITIVE]`)

2.  **Skip if Nothing Notable:** If there is nothing worth recording, skip the rest of this section entirely.

3.  **Append to Lessons File:** Append each observation as a one-liner to `kamma/lessons.md` (create the file if it does not exist). Format:
    ```
    - YYYY-MM-DD [TAG] Short description of what happened
    ```
    Do not add headers, preamble, or "no lessons" entries. Just append the lines.

4.  **Propose Improvements:** Read the full `kamma/lessons.md`. For any lesson — even a single occurrence — that suggests a concrete, lasting improvement to the project's `CLAUDE.md` or `AGENTS.md`, apply the change directly and tell the user what you added and why. Keep additions minimal: one or two sentences per rule.

5.  **If No Improvements Apply:** Say nothing and move on.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.
