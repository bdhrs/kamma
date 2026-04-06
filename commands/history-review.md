---
description: Analyzes past sessions for recurring errors and patterns, then proposes improvements to agent configurations
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven development framework. Your current task is to analyze past sessions for recurring errors and patterns, then propose improvements to agent configurations. You MUST follow this process precisely.

CRITICAL: Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

TO-DO LIST: Keep a to-do list for this entire command. Add the current section's work before you start it, update the list as you go, and use it to track progress until the command is complete.
At the end of every section in this file, tick off completed to-do items before you move on.

---

## 1.1 SETUP CHECK
**Verify that the required environment files exist.**

1.  **Check for Workflow Issues File:** You MUST verify the existence of the workflow issues file at `~/agents/workflow-issues.md` (or `kamma/workflow-issues.md` if the user is in a Kamma project).
    -   If the file exists, read it to get the last analysis date.

2.  **Check for Sessions Directory:** Verify the existence of a sessions directory where session logs are stored:
    -   Check for `kamma/sessions/` or similar.
    -   If no sessions directory exists, announce that no session history is available and continue as far as you can.

3.  **Check for Memory Files:** Verify the existence of memory files:
    -   Check for `memory/MEMORY.md` or similar.
    -   If found, note them for analysis.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 2.0 COLLECT SESSION DATA
**Gather all recent session data for analysis.**

1.  **Determine Checkpoint Date:** From the workflow issues file, extract the last analysis date (or use a default of the last 30 days if no checkpoint exists).

2.  **Collect Recent Sessions:** For each project, identify and read all session files newer than the checkpoint date:
    -   Look for `kamma/sessions/*.md` files or equivalent.
    -   Aggregate all session content into a single analysis context.

3.  **Collect Memory Files:** Read any memory or feedback files:
    -   Read `memory/MEMORY.md` if it exists.
    -   Read any linked `feedback_*.md` files or similar.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 3.0 ANALYZE PATTERNS
**Extract recurring patterns and feedback from the collected data.**

1.  **Search for Recurring Errors:**
    -   Identify errors or mistakes that appear multiple times across sessions.
    -   Categorize by frequency and severity.

2.  **Identify Feedback Points:**
    -   Extract user feedback from session logs or feedback files.
    -   Note any explicit user corrections or dissatisfaction signals.

3.  **Analyze AI Behavior Patterns:**
    -   Identify patterns in AI behavior that are consistently good.
    -   Identify patterns in AI behavior that are consistently bad or problematic.

4.  **Count Occurrences:** For each identified pattern, count the number of occurrences.
    -   Mark patterns with count ≥ 2 as significant.
    -   Skip patterns with count = 1 unless they are critical.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 4.0 CLASSIFY AND PROPOSE
**Classify findings by scope and propose improvements.**

1.  **Classify Scope:** For each significant pattern (count ≥ 2), determine the appropriate scope:
    -   **`global`** — Applies to any project → Propose changes to `~/agents/AGENTS.md` or `kamma/AGENTS.md`.
    -   **`project`** — Specific to one project → Propose changes to `[project]/AGENTS.md` or the project's specific agent file.

2.  **Draft Improvements:** For each file where significant patterns are identified, draft specific improvement suggestions:
    -   Include the file path where the change should be made.
    -   Include the rationale for the change (pattern description, frequency, impact).
    -   Specific, actionable change recommendations.

3.  **Output Results:** Present a list of suggested improvements with:
    -   Target file path
    -   Rationale
    -   Proposed change

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 5.0 UPDATE WORKFLOW ISSUES
**Record the analysis for future reference.**

1.  **Update Checkpoint:** If a workflow issues file exists, update the last analysis date to the current date.

2.  **Document Findings:** If significant patterns were found, consider adding a summary to the workflow issues file for future reference.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.