---
description: Run ruff and pyright on a target file and fix all errors
---

## 1.0 PURPOSE
You are an AI agent. Your job is to run linting and type checking on a target file and fix all reported errors and warnings.

**CRITICAL:** Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

TO-DO LIST: Keep a to-do list for this entire command. Add the current section's work before you start it, update the list as you go, and use it to track progress until the command is complete.
At the end of every section in this file, tick off completed to-do items before you move on.

---

## 2.0 IDENTIFY TARGET FILE

### 2.1 Check for User Input

1.  **If Arguments Provided:** If `{{args}}` contains a file path, use it as the target file.
2.  **If No Arguments:** If no argument is given, ask the user:
    > "Which file should I fix?"
    STOP and wait for their answer before proceeding.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 3.0 RUN DIAGNOSTICS

### 3.1 Execute Linters

1.  **Run Ruff:** Execute `uv run ruff check <file>` and capture the output.
2.  **Run Pyright:** Execute `uv run pyright <file>` and capture the output.

### 3.2 Check Results

1.  **If Both Clean:** If both tools report zero issues, inform the user and stop — nothing to do.
2.  **If Issues Found:** If issues are reported, proceed to fix them.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 4.0 FIX ALL ISSUES

### 4.1 Read the File

1.  **Read Target:** Read the entire target file.

### 4.2 Fix Each Diagnostic

1.  **Work Through Issues:** Iterate through every ruff and pyright diagnostic and fix each one directly in the file.
2.  **Do Not Suppress:** Do NOT silence linters with `# noqa` or `# type: ignore` unless the warning is a known false positive that genuinely cannot be fixed in code.
3.  **If Suppression Required:** If you must suppress a warning, add a comment explaining why.
4.  **Do Not Over-Extend:** Do not refactor, add features, or add docstrings/comments beyond what the linters require.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 5.0 VERIFY CLEAN

### 5.1 Re-run Diagnostics

1.  **Run Ruff Again:** Execute `uv run ruff check <file>` again.
2.  **Run Pyright Again:** execute `uv run pyright <file>` again.

### 5.2 Repeat if Needed

1.  **If New Issues Surface:** If new issues surface during verification, fix those as well.
2.  **Repeat Until Clean:** Repeat this verification step until both tools report clean.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 6.0 REPORT

### 6.1 Summarize Changes

1.  **Write Summary:** Summarize what was changed and why in a short bullet list.
2.  **Present to User:** Present the summary to the user.

---

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.