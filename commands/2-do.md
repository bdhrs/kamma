---
description: Executes the tasks defined in the specified thread's plan
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven development framework. Your current task is to implement a thread. You MUST follow this process precisely.

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

2.  **Handle Missing Files:**
    -   If any of these files are missing, say what is missing, look for another sensible way to continue, and keep going if you still can.
    -   Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment."
    -   Continue if there is still a reasonable path forward.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 2.0 CHOOSE A THREAD
**Identify and select the thread to work on.**

1.  **Check for User Input:** First, check if the user provided a thread name as an argument (for example, `/kamma:2-do <thread_description>`).

2.  **Scan Thread Directories:** List all directories in `kamma/threads/`. For each directory, read `spec.md` for the thread description and `plan.md` to determine progress (check for unchecked `[ ]` or in-progress `[~]` tasks).
    -   **CRITICAL:** If no thread directories are found, announce: "No active threads found in `kamma/threads/`. Create one with `/kamma:1-plan`." Then move on.

3.  **Select Thread:**
    -   **If a thread name was provided:**
        1.  Perform a case-insensitive match against thread directory names and spec descriptions.
        2.  If a unique match is found, confirm with the user.
        3.  If there is no match or it is ambiguous, inform the user and list available threads.
    -   **If no thread name was provided:**
        1.  Find the first thread with incomplete tasks in its `plan.md`.
        2.  Announce: "Automatically selecting the next incomplete thread: '<thread_description>'."
        3.  If no incomplete threads are found, say that all threads appear complete, suggest the next sensible action, and continue as far as you reasonably can.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 3.0 DO THE WORK
**Execute the selected thread.**

1.  **Announce Action:** Announce which thread you are starting.

2.  **Load the Thread Files:**
    a. **Identify Thread Folder:** Use the `<thread_id>` from the selected thread directory.
    b. **Read Files:**
        - `kamma/threads/<thread_id>/plan.md`
        - `kamma/threads/<thread_id>/spec.md`
        - `kamma/workflow.md`
    c. **Preserve Issue Visibility:** If the thread references a GitHub issue, keep that issue number visible and unchanged in the thread description, `spec.md`, and `plan.md` throughout implementation so review and finalize can rely on it.
    d. **Error Handling:** If you fail to read any of these files, say what failed, try another sensible way to recover the missing context, and keep going if you still can.

4.  **Execute Tasks and Update the Thread Plan:**
    a. **Announce:** State that you will work through the thread's `plan.md` by following `workflow.md`.
    b. **Iterate Through Tasks:** Loop through each task in `plan.md` one by one.
    c. **For Each Task:**
        i. **Defer to Workflow:** `workflow.md` is the single source of truth for the full task flow. Follow its instructions for implementation and testing.

5.  **Hand Off for Review:**
    -   After all implementation tasks are completed and local verification is done, DO NOT mark the thread fully complete yet.
    -   Ask the user to apply any manual changes or test the result themselves, and wait for them to confirm the work is done.
    -   Once confirmed, suggest running `/kamma:3-review` in a fresh session using a different model than the one currently in use (e.g. if on Sonnet, suggest Opus; if on Opus, suggest Sonnet) for an independent review.
    -   Explain that the thread should only move to final completion after review findings, if any, have been implemented and verified.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.
