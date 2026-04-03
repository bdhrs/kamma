---
description: Displays the current progress of the project
---

## 1.0 PURPOSE
You are an AI agent. Your job is to show the current status of the threads file.

CRITICAL: Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

---

## 1.1 SETUP CHECK
**Verify that the Kamma environment is properly set up.**

1.  **Check for Required Files:** Verify existence of:
    -   `kamma/context.md`
    -   `kamma/workflow.md`
    -   `kamma/project.md`

2.  **Handle Missing Files:**
    -   If any are missing, say what is missing, look for another sensible way to continue, and keep going if you still can.
    -   Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment."

---

## 2.0 SHOW CURRENT STATUS
**Follow this sequence to show the current status.**

### 2.1 Read the Project Plan
1.  **Locate and Read:** Read the content of `kamma/threads.md`.
2.  **Locate and Read:** List the threads using `ls kamma/threads`. For each thread, read its `kamma/threads/<thread_id>/plan.md`.

### 2.2 Parse and Summarize the Plan
1.  **Parse Content:**
    -   Identify phases or sections.
    -   Identify individual tasks and their current status.
2.  **Generate Summary:** Create a concise summary including:
    -   Total number of phases.
    -   Total number of tasks.
    -   Number of tasks completed, in progress, and pending.

### 2.3 Present the Status
1.  **Output Summary:** Present in a clear, readable format including:
    -   **Current Date/Time**
    -   **Overall Status:** A short plain-English summary
    -   **Current Thread and Task:** The specific thread and task currently in progress
    -   **Next Action Needed:** The next pending task
    -   **Blockers:** Any items marked as blockers
    -   **Phases (total)**
    -   **Tasks (total)**
    -   **Progress:** tasks_completed/tasks_total (percentage%)
