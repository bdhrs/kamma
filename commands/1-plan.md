---
description: Plans a thread, generates thread-specific spec documents and updates the threads file
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to help the user create a new thread, generate the thread's `spec.md` and `plan.md`, and place them in the right folder.

CRITICAL: You must validate the success of every tool call. If any tool call fails, you MUST stop immediately, tell the user what failed, and wait for further instructions.

## 1.1 SETUP CHECK
**Verify that the Kamma environment is set up correctly.**

1.  **Check for Required Files:** You MUST verify the existence of the following files in the `kamma` directory:
    -   `kamma/context.md`
    -   `kamma/workflow.md`
    -   `kamma/project.md`

2.  **Handle Missing Files:**
    -   If ANY of these files are missing, you MUST stop immediately.
    -   Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment."
    -   Do NOT proceed.

---

## 2.0 CREATE A NEW THREAD
**Follow this sequence.**

### 2.1 Get the Thread Description and Work Out the Type

1.  **Load Project Context:** Read and understand the content of the `kamma` directory files.
2.  **Get Thread Description:**
    *   **If `{{args}}` contains a description:** Use the content of `{{args}}`.
    *   **If `{{args}}` is empty:** Ask the user:
        > "Please provide a brief description of the thread (feature, bug fix, chore, etc.) you want to start."
        Wait for the user's response and use it as the thread description.
3.  **Infer Thread Type:** Analyze the description to determine if it is a feature or something else (for example, a bug, chore, or refactor). Do NOT ask the user to classify it.

### 2.2 Write `spec.md`

1.  **State Your Goal:** Announce:
    > "I'll now ask a few questions so I can write a solid `spec.md` for this thread."

2.  **Ask a Few Questions:** Ask a series of questions to gather details for `spec.md`. Tailor the questions based on the thread type.
    *   **CRITICAL:** Ask these questions one at a time. Do not ask multiple questions in a single turn. Wait for the user's response after each question.
    *   **General Guidelines:**
        *   Refer to information in `project.md`, `context.md`, and related files so the questions fit the project.
        *   Provide a brief explanation and clear examples for each question.
        *   Whenever possible, present 2-3 plausible options (A, B, C) for the user to choose from.
        *   The last option for every multiple-choice question MUST be "Type your own answer".

    *   **If FEATURE:**
        *   **Ask 3-5 relevant questions** to clarify the feature request.
        *   Examples include how the feature should work, how it should be built, interactions, inputs/outputs, and edge cases.

    *   **If SOMETHING ELSE (Bug, Chore, etc.):**
        *   **Ask 2-3 relevant questions** to get the needed details.
        *   Examples include reproduction steps for bugs, specific scope for chores, or success criteria.

3.  **Draft `spec.md`:** Once you have enough information, draft the thread's `spec.md`, including sections like Overview, Functional Requirements, Non-Functional Requirements (if any), Acceptance Criteria, and Out of Scope.

4.  **Check the Draft:** Present the drafted `spec.md` content to the user for review and approval.
    > "I've drafted the specification for this thread. Please review the following:"
    >
    > ```markdown
    > [Drafted spec.md content here]
    > ```
    >
    > "Does this accurately capture the requirements? Please suggest any changes or confirm."
    Wait for user feedback and revise the `spec.md` content until confirmed.

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
    > "Does this plan look correct? Please suggest any changes or confirm."
    Wait for user feedback and revise until confirmed.

### 2.4 Create the Thread Files and Update `threads.md`

1.  **Check for Existing Thread Name:** Before generating a new thread ID, list all existing thread directories in `kamma/threads/`. If the proposed short name matches an existing one, stop and suggest choosing a different name.
2.  **Generate Thread ID:** Create a unique thread ID (for example, `shortname_YYYYMMDD`).
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
