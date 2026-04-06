---
description: End-of-session protocol - create session log and handoff
---

## 1.0 PURPOSE
You are an AI agent. Your job is to properly end your session by creating a session log and updating thread state for handoff.

**CRITICAL:** Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

TO-DO LIST: Keep a to-do list for this entire command. Add the current section's work before you start it, update the list as you go, and use it to track progress until the command is complete.
At the end of every section in this file, tick off completed to-do items before you move on.

---

## 1.1 TWO FILES — NEVER CONFUSE

- `kamma/threads/<thread>/handoff.md` — track state. Overwrite each session.
- `kamma/sessions/YYYY-MM-DD-HHMM-{agent}.md` — immutable session log. Always create a new file, never overwrite or append.

---

## 2.0 CREATE SESSION LOG

### 2.1 Get Date and Time

1.  **Get Current Date:** Execute a command to get today's date in `YYYY-MM-DD` format.
2.  **Get Current Time:** Execute a command to get current time in `HHMM` format (24-hour, no colon).

### 2.2 Determine Agent Name

1.  **Determine Agent Identifier:** Based on the AI system you are running as (e.g., "sonnet", "claude", "kilo", "qwen"). Use a short, lowercase identifier suitable for a filename.

### 2.3 Create Session Log File

1.  **Create NEW File:** Create `kamma/sessions/YYYY-MM-DD-HHMM-{agent}.md` using the date, time, and agent identifier gathered above.
    -   **Example:** If date is 2026-04-06, time is 1545, and agent is sonnet, create: `kamma/sessions/2026-04-06-1545-sonnet.md`
2.  **Always Create New:** Never read existing logs, never append. Always create a fresh file.

### 2.4 Write Session Summary

1.  **Write Summary:** Write a concise summary of what was accomplished during this session.
2.  **Write Issues Section:** Create an `## Issues & AI Feedback` section with tagged items:
    -   `[REPEATED]` — user had to re-state a rule
    -   `[WORKFLOW]` — process friction
    -   `[CONFUSION]` — misunderstanding
    -   `[BEHAVIOR]` — rule violation or missed action
    -   `[POSITIVE]` — something that worked well
3.  **If No Issues:** Write `- None this session` if there are no issues to report.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 3.0 TRACK HANDOFF (ONLY IF THREAD WORK HAPPENED)

### 3.1 Check if Thread Work Happened

1.  **Determine if Work Occurred:** If no track work happened this session, skip this entire section — do not read any track files.
2.  **If Work DID Happen:** If thread work DID happen, proceed to the next step.

### 3.2 Update Handoff File

1.  **Identify Current Thread:** Determine which thread was being worked on.
2.  **Overwrite Handoff:** Overwrite `kamma/threads/<thread>/handoff.md` with current state:
    -   What was done this session
    -   Current task being worked on
    -   Code state (what files were modified, changes made)
    -   Blockers (if any)
3.  **Update Plan Checkboxes:** In `kamma/threads/<thread>/plan.md`, update status markers:
    -   Mark completed tasks as `[x]`
    -   Mark in-progress tasks as `[~]`

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 4.0 LOOSE ENDS

### 4.1 Check for Unresolved Items

1.  **Identify Loose Ends:** If anything is unresolved outside of a track, append to `NOTES.md` in the project root.
2.  **If Nothing Unresolved:** Skip this step.

---

## 5.0 CONFIRM AND SAY GOOD NIGHT

1.  **Confirm Files Saved:** Verify all files have been saved correctly.
2.  **Say Good Night:** Confirm completion and say good night to the user.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.