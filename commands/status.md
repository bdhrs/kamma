---
description: Displays the current progress of the project
---

## 1.0 SYSTEM DIRECTIVE
You are an AI agent. Your primary function is to provide a status overview of the current threads file.

**CRITICAL:** Before proceeding, check if the project has been properly set up.
1.  **Verify Threads File:** Check if `kamma/threads.md` exists. If not, HALT and instruct: "The project has not been set up. Please run `/kamma:0-setup`."
2.  **Verify Thread Exists:** Check if `kamma/threads.md` is not empty. If empty, HALT and instruct the same.

CRITICAL: You must validate the success of every tool call. If any tool call fails, you MUST halt the current operation immediately, announce the failure to the user, and await further instructions.

---

## 1.1 SETUP CHECK
**PROTOCOL: Verify that the Kamma environment is properly set up.**

1.  **Check for Required Files:** Verify existence of:
    -   `kamma/tech-stack.md`
    -   `kamma/workflow.md`
    -   `kamma/project.md`

2.  **Handle Missing Files:**
    -   If ANY are missing, halt immediately.
    -   Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment."

---

## 2.0 STATUS OVERVIEW PROTOCOL
**PROTOCOL: Follow this sequence to provide a status overview.**

### 2.1 Read Project Plan
1.  **Locate and Read:** Read the content of `kamma/threads.md`.
2.  **Locate and Read:** List the threads using `ls kamma/threads`. For each thread, read its `kamma/threads/<thread_id>/plan.md`.

### 2.2 Parse and Summarize Plan
1.  **Parse Content:**
    -   Identify major project phases/sections.
    -   Identify individual tasks and their current status.
2.  **Generate Summary:** Create a concise summary including:
    -   Total number of major phases.
    -   Total number of tasks.
    -   Number of tasks completed, in progress, and pending.

### 2.3 Present Status Overview
1.  **Output Summary:** Present in a clear, readable format including:
    -   **Current Date/Time**
    -   **Project Status:** High-level summary (e.g., "Moving Well", "Behind Schedule", "Blocked").
    -   **Current Phase and Task:** The specific phase and task currently "IN PROGRESS".
    -   **Next Action Needed:** The next "PENDING" task.
    -   **Blockers:** Any items marked as blockers.
    -   **Phases (total)**
    -   **Tasks (total)**
    -   **Progress:** tasks_completed/tasks_total (percentage%)
