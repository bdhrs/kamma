---
description: Displays the current progress of the project
---

## 1.0 PURPOSE
You are an AI agent. Your job is to show the current status of the project's active threads.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way to make progress, reassess, and keep going.

Verify `kamma/project.md`, `kamma/tech.md`, and `kamma/workflow.md` exist. If any are missing, say what's missing and suggest `/kamma:0-setup`.

---

## 2.0 SHOW CURRENT STATUS

### 2.1 Read the Project Plan
List all thread directories in `kamma/threads/`. For each, read `plan.md` and `spec.md` to determine status.

### 2.2 Parse and Summarize
1. Identify phases, tasks, and their status.
2. Count: total phases, total tasks, completed, in progress, pending.

### 2.3 Present the Status
Output a clear summary:
- **Current Date/Time**
- **Overall Status:** Short plain-English summary
- **Current Thread and Task:** What's in progress
- **Next Action Needed:** The next pending task
- **Blockers:** Anything flagged
- **Phases (total)**
- **Tasks (total)**
- **Progress:** completed/total (percentage%)
