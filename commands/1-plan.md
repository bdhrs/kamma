---
description: Plans a thread, generates thread-specific spec documents and updates the threads file
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to help the user create a new thread, generate the thread's `spec.md` and `plan.md`, and place them in the right folder.

CRITICAL: Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

TO-DO LIST: Keep a to-do list for this entire command. Add the current section's work before you start it, update the list as you go, and use it to track progress until the command is complete.
At the end of every section in this file, tick off completed to-do items before you move on.

## 1.1 SETUP CHECK
**Verify that the Kamma environment is set up correctly.**

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


## 2.0 CREATE A NEW THREAD
**Follow this sequence.**

### 2.1 Get the Thread Description and Work Out the Type

1.  **Load Project Files:** Read and understand the content of the `kamma` directory files.
2.  **Get Thread Description:**
    *   **If `{{args}}` contains a description:** Use the content of `{{args}}`.
    *   **If `{{args}}` is empty:** Ask the user:
        > "Please provide a brief description of the thread (feature, bug fix, chore, etc.) you want to start."
        Wait for the user's response and use it as the thread description.
3.  **Infer Thread Type:** Analyze the description to determine if it is a feature or something else (for example, a bug, chore, or refactor). Do NOT ask the user to classify it.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 2.2 Write `spec.md`

1.  **Ask Only What You Need To:** Use `project.md`, `tech.md`, and the codebase to answer as much as you can before asking anything. Only ask questions when the answer genuinely cannot be inferred. Ask one at a time and wait for the response.
    *   **General Guidelines:**
        *   Whenever possible, present 2-3 plausible options (A, B, C) for the user to choose from.
        *   The last option for every multiple-choice question MUST be "Type your own answer".

    *   **If FEATURE:** Focus questions on intent and edge cases the codebase cannot answer — how it should behave, who it is for, what success looks like.

    *   **If SOMETHING ELSE (Bug, Chore, etc.):** Focus on what you need to reproduce or scope the work — reproduction steps, specific scope, or how you'll know it's fixed.

3.  **Draft `spec.md`:** Once you have enough information, draft the thread's `spec.md`, including sections like Overview, What it should do, Constraints (if any), How we'll know it's done, and What's not included.

4.  **Check the Draft:** Present the drafted `spec.md` content to the user for review and approval.
    > "I've drafted the specification for this thread. Please review the following:"
    >
    > ```markdown
    > [Drafted spec.md content here]
    > ```
    >
    > "Does this look right? Let me know if anything needs changing."
    Wait for user feedback and revise the `spec.md` content until confirmed.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 2.3 Write `plan.md`

1.  **State Your Goal:** Once `spec.md` is approved, announce:
    > "Now I will create `plan.md` based on the specification."

2.  **Generate Plan:**
    *   Read the confirmed `spec.md` content for this thread.
    *   Read `kamma/workflow.md`.
    *   Generate a `plan.md` with a hierarchical list of Phases, Tasks, and Sub-tasks.
    *   **CRITICAL:** The plan structure MUST follow the workflow file.
    *   Include status markers `[ ]` for each task/sub-task.
    *   **CRITICAL: Inject Phase Completion Tasks.** If a "Phase Completion" protocol exists in `kamma/workflow.md`, append a final verification task to each Phase.

3.  **Check the Draft:** Present the drafted `plan.md` to the user for review and approval.
    > "I've drafted the implementation plan. Please review the following:"
    >
    > ```markdown
    > [Drafted plan.md content here]
    > ```
    >
    > "Does this plan look right? Let me know if anything needs changing."
    Wait for user feedback and revise until confirmed.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 2.4 Create the Thread Files and Update `threads.md`

1.  **Check for Existing Thread Name:** Before generating a new thread ID, list all existing thread directories in `kamma/threads/`. If the proposed short name matches an existing one, suggest a different name and keep going with the revised name.
2.  **Generate Thread ID:** Create a unique thread ID (for example, `YYYYMMDD_shortname`).
3.  **Create Directory:** Create a new directory: `kamma/threads/<thread_id>/`
4.  **Write Files:**
    *   Write the confirmed specification to `kamma/threads/<thread_id>/spec.md`.
    *   Write the confirmed plan to `kamma/threads/<thread_id>/plan.md`.
5.  **Update Threads File:**
    -   Append a new section to `kamma/threads.md`:
        ```markdown

        ---

        ## [ ] Thread: <Thread Description>
        *Link: [./kamma/threads/<thread_id>/](./kamma/threads/<thread_id>/)*
        ```
6.  **Announce Completion:**
    > "New thread '<thread_id>' has been created. You can now start work by running `/kamma:2-do`."


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

