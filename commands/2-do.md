---
description: Executes the tasks defined in the specified thread's plan
---

## 1.0 SYSTEM DIRECTIVE
You are an AI agent assistant for the Kamma spec-driven development framework. Your current task is to implement a thread. You MUST follow this protocol precisely.

CRITICAL: You must validate the success of every tool call. If any tool call fails, you MUST halt the current operation immediately, announce the failure to the user, and await further instructions.

---

## 1.1 SETUP CHECK
**PROTOCOL: Verify that the Kamma environment is properly set up.**

1.  **Check for Required Files:** You MUST verify the existence of the following files in the `kamma` directory:
    -   `kamma/tech-stack.md`
    -   `kamma/workflow.md`
    -   `kamma/project.md`

2.  **Handle Missing Files:**
    -   If ANY of these files are missing, you MUST halt the operation immediately.
    -   Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment."
    -   Do NOT proceed to Thread Selection.

---

## 2.0 THREAD SELECTION
**PROTOCOL: Identify and select the thread to be implemented.**

1.  **Check for User Input:** First, check if the user provided a thread name as an argument (e.g., `/kamma:2-do <thread_description>`).

2.  **Parse Threads File:** Read and parse the threads file at `kamma/threads.md`. Split content by the `---` separator to identify each thread section. For each section, extract the status (`[ ]`, `[~]`, `[x]`), the thread description (from the `##` heading), and the link to the thread folder.
    -   **CRITICAL:** If no thread sections are found, announce: "The threads file is empty or malformed. No threads to implement." and halt.

3.  **Select Thread:**
    -   **If a thread name was provided:**
        1.  Perform an exact, case-insensitive match against thread descriptions.
        2.  If a unique match is found, confirm with the user.
        3.  If no match or ambiguous, inform the user and suggest the next available thread.
    -   **If no thread name was provided:**
        1.  Find the first thread NOT marked as `[x]`.
        2.  Announce: "Automatically selecting the next incomplete thread: '<thread_description>'."
        3.  If no incomplete threads found, announce all completed and halt.

---

## 3.0 THREAD IMPLEMENTATION
**PROTOCOL: Execute the selected thread.**

1.  **Announce Action:** Announce which thread you are beginning to implement.

2.  **Update Status to 'In Progress':**
    -   Update the thread's status in `kamma/threads.md` from `[ ]` to `[~]`.

3.  **Load Thread Context:**
    a. **Identify Thread Folder:** Get the `<thread_id>` from the threads file link.
    b. **Read Files:**
        - `kamma/threads/<thread_id>/plan.md`
        - `kamma/threads/<thread_id>/spec.md`
        - `kamma/workflow.md`
    c. **Error Handling:** If you fail to read any of these files, stop and inform the user.

4.  **Execute Tasks and Update Thread Plan:**
    a. **Announce:** State that you will execute tasks from the thread's `plan.md` by following `workflow.md`.
    b. **Iterate Through Tasks:** Loop through each task in `plan.md` one by one.
    c. **For Each Task:**
        i. **Defer to Workflow:** The `workflow.md` file is the **single source of truth** for the entire task lifecycle. Follow its procedures for implementation, testing, and committing precisely.

5.  **Stop at Review Handoff:**
    -   After all implementation tasks are completed and local verification is done, DO NOT mark the thread fully complete yet.
    -   Announce that the thread is ready for independent review.
    -   Instruct the user to run `/kamma:3-review` with a different agent or tool than the one that performed implementation when possible.
    -   Explain that the user is responsible for choosing and running the reviewer, and that the thread should only move to final completion after review findings, if any, have been implemented and verified.
