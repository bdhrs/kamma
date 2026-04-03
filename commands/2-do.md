---
description: Executes the tasks defined in the specified thread's plan
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven development framework. Your current task is to implement a thread. You MUST follow this process precisely.

CRITICAL: You must validate the success of every tool call. If any tool call fails, you MUST stop immediately, tell the user what failed, and wait for further instructions.

---

## 1.1 SETUP CHECK
**Verify that the Kamma environment is properly set up.**

1.  **Check for Required Files:** You MUST verify the existence of the following files in the `kamma` directory:
    -   `kamma/context.md`
    -   `kamma/workflow.md`
    -   `kamma/project.md`

2.  **Handle Missing Files:**
    -   If ANY of these files are missing, you MUST halt the operation immediately.
    -   Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment."
    -   Do NOT proceed.

---

## 2.0 CHOOSE A THREAD
**Identify and select the thread to work on.**

1.  **Check for User Input:** First, check if the user provided a thread name as an argument (for example, `/kamma:2-do <thread_description>`).

2.  **Parse Threads File:** Read and parse the threads file at `kamma/threads.md`. Split content by the `---` separator to identify each thread section. For each section, extract the status (`[ ]`, `[~]`, `[x]`), the thread description (from the `##` heading), and the link to the thread folder.
    -   **CRITICAL:** If no thread sections are found, announce: "The threads file is empty or malformed. No threads to work on." and halt.

3.  **Select Thread:**
    -   **If a thread name was provided:**
        1.  Perform an exact, case-insensitive match against thread descriptions.
        2.  If a unique match is found, confirm with the user.
        3.  If there is no match or it is ambiguous, inform the user and suggest the next available thread.
    -   **If no thread name was provided:**
        1.  Find the first thread NOT marked as `[x]`.
        2.  Announce: "Automatically selecting the next incomplete thread: '<thread_description>'."
        3.  If no incomplete threads are found, announce that all threads are complete and halt.

---

## 3.0 DO THE WORK
**Execute the selected thread.**

1.  **Announce Action:** Announce which thread you are starting.

2.  **Update Status to 'In Progress':**
    -   Update the thread's status in `kamma/threads.md` from `[ ]` to `[~]`.

3.  **Load the Thread Files:**
    a. **Identify Thread Folder:** Get the `<thread_id>` from the threads file link.
    b. **Read Files:**
        - `kamma/threads/<thread_id>/plan.md`
        - `kamma/threads/<thread_id>/spec.md`
        - `kamma/workflow.md`
    c. **Error Handling:** If you fail to read any of these files, stop and inform the user.

4.  **Execute Tasks and Update the Thread Plan:**
    a. **Announce:** State that you will work through the thread's `plan.md` by following `workflow.md`.
    b. **Iterate Through Tasks:** Loop through each task in `plan.md` one by one.
    c. **For Each Task:**
        i. **Defer to Workflow:** `workflow.md` is the single source of truth for the full task flow. Follow its instructions for implementation, testing, and committing.

5.  **Stop When It Is Ready for Review:**
    -   After all implementation tasks are completed and local verification is done, DO NOT mark the thread fully complete yet.
    -   Announce that the thread is ready for review.
    -   Instruct the user to run `/kamma:3-review`, ideally in a different tool or a fresh session when possible.
    -   Explain that the thread should only move to final completion after review findings, if any, have been implemented and verified.
