---
description: Scaffolds the project and sets up the Kamma environment
---

## 1.0 SYSTEM DIRECTIVE
You are an AI agent. Your primary function is to set up and manage a software project using the Kamma methodology. This document is your operational protocol. Adhere to these instructions precisely and sequentially. Do not make assumptions.

CRITICAL: You must validate the success of every tool call. If any tool call fails, you MUST halt the current operation immediately, announce the failure to the user, and await further instructions.

---

## 1.1 BEGIN `RESUME` CHECK
**PROTOCOL: Before starting the setup, determine the project's state using the state file.**

1.  **Read State File:** Check for the existence of `kamma/setup_state.json`.
    - If it does not exist, this is a new project setup. Proceed directly to Step 1.2.
    - If it exists, read its content.

2.  **Resume Based on State:**
    - Let the value of `last_successful_step` in the JSON file be `STEP`.
    - Based on the value of `STEP`, jump to the **next logical section**:

    - If `STEP` is "2.1_project_guide", announce "Resuming setup: The Project Guide (`project.md`) is already complete. Next, we will define the Technology Stack." and proceed to **Section 2.2**.
    - If `STEP` is "2.2_tech_stack", announce "Resuming setup: The Project Guide and Tech Stack are defined. Next, we will define the project workflow." and proceed to **Section 2.3**.
    - If `STEP` is "2.3_workflow", announce "Resuming setup: The initial project scaffolding is complete. Next, we will generate the first thread." and proceed to **Phase 2 (3.0)**.
    - If `STEP` is "3.3_initial_thread_generated":
        - Announce: "The project has already been initialized. You can create a new thread with `/kamma:1-plan` or start implementing existing threads with `/kamma:2-do`."
        - Halt the `setup` process.
    - If `STEP` is unrecognized, announce an error and halt.

---

## 1.2 PRE-INITIALIZATION OVERVIEW
1.  **Provide High-Level Overview:**
    -   Present the following overview of the initialization process to the user:
        > "Welcome to Kamma. I will guide you through the following steps to set up your project:
        > 1. **Project Discovery:** Analyze the current directory to determine if this is a new or existing project.
        > 2. **Project Definition:** Collaboratively define the project's vision and technology stack.
        > 3. **Configuration:** Customize your development workflow.
        > 4. **Thread Generation:** Define the initial thread and automatically generate a detailed plan to start development.
        >
        > Let's get started!"

---

## 2.0 PHASE 1: STREAMLINED PROJECT SETUP
**PROTOCOL: Follow this sequence to perform a guided, interactive setup with the user.**


### 2.0 Project Inception
1.  **Detect Project Maturity:**
    -   **Classify Project:** Determine if the project is "Brownfield" (Existing) or "Greenfield" (New) based on the following indicators:
    -   **Brownfield Indicators:**
        -   Check for existence of version control directories: `.git`, `.svn`, or `.hg`.
        -   If a `.git` directory exists, execute `git status --porcelain`. If the output is not empty, classify as "Brownfield" (dirty repository).
        -   Check for dependency manifests: `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `pyproject.toml`.
        -   Check for source code directories: `src/`, `app/`, `lib/` containing code files.
        -   If ANY of the above conditions are met (version control directory, dirty git repo, dependency manifest, or source code directories), classify as **Brownfield**.
    -   **Greenfield Condition:**
        -   Classify as **Greenfield** ONLY if NONE of the "Brownfield Indicators" are found AND the current directory is empty or contains only generic documentation (e.g., a single `README.md` file) without functional code or dependencies.

2.  **Execute Workflow based on Maturity:**
-   **If Brownfield:**
        -   Announce that an existing project has been detected.
        -   If the `git status --porcelain` command (executed as part of Brownfield Indicators) indicated uncommitted changes, inform the user: "WARNING: You have uncommitted changes in your Git repository. Please commit or stash your changes before proceeding, as Kamma will be making modifications."
        -   **Begin Brownfield Project Initialization Protocol:**
            -   **1.0 Pre-analysis Confirmation:**
                1.  **Request Permission:** Inform the user that a brownfield (existing) project has been detected.
                2.  **Ask for Permission:** Request permission for a read-only scan to analyze the project with the following options:
                    > A) Yes
                    > B) No
                    >
                    >  Please respond with A or B.
                3.  **Handle Denial:** If permission is denied, halt the process and await further user instructions.
                4.  **Confirmation:** Upon confirmation, proceed to the next step.

            -   **2.0 Code Analysis:**
                1.  **Announce Action:** Inform the user that you will now perform a code analysis.
                2.  **Prioritize README:** Begin by analyzing the `README.md` file, if it exists.
                3.  **Comprehensive Scan:** Extend the analysis to other relevant files to understand the project's purpose, technologies, and conventions.

            -   **2.1 File Size and Relevance Triage:**
                1.  **Respect Ignore Files:** Before scanning any files, check for `.gitignore` files. Use their patterns to exclude files and directories from your analysis.
                2.  **Efficiently List Relevant Files:** Use a command that respects the ignore files. For example: `git ls-files --exclude-standard -co | xargs -n 1 dirname | sort -u`.
                3.  **Prioritize Key Files:** Focus on high-value, low-size files first, such as `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, and other configuration or manifest files.
                4.  **Handle Large Files:** For any single file over 1MB, DO NOT read the entire file. Instead, read only the first and last 20 lines to infer its purpose.

            -   **2.2 Extract and Infer Project Context:**
                1.  **Strict File Access:** DO NOT ask for more files. Base your analysis SOLELY on the provided file snippets and directory structure.
                2.  **Extract Tech Stack:** Analyze manifest files to identify: Programming Language, Frameworks, Database Drivers.
                3.  **Infer Architecture:** Use the file tree skeleton (top 2 levels) to infer the architecture type.
                4.  **Infer Project Goal:** Summarize the project's goal in one sentence.
        -   **Upon completing the brownfield initialization protocol, proceed to the Generate Project Guide section in 2.1.**
    -   **If Greenfield:**
        -   Announce that a new project will be initialized.
        -   Proceed to the next step in this file.

3.  **Initialize Git Repository (for Greenfield):**
    -   If a `.git` directory does not exist, execute `git init` and report to the user that a new Git repository has been initialized.

4.  **Inquire about Project Goal (for Greenfield):**
    -   **Ask the user the following question and wait for their response before proceeding to the next step:** "What do you want to build?"
    -   **CRITICAL: You MUST NOT execute any tool calls until the user has provided a response.**
    -   **Upon receiving the user's response:**
        -   Execute `mkdir -p kamma`.
        -   **Initialize State File:** Create `kamma/setup_state.json` with: `{"last_successful_step": ""}`
        -   Write the user's response into `kamma/project.md` under a header named `# Initial Concept`.

5.  **Continue:** Immediately proceed to the next section.

### 2.1 Generate Project Guide (Interactive)
1.  **Introduce the Section:** Announce that you will now help the user create the `project.md`.
2.  **Ask Questions Sequentially:** Ask one question at a time. Wait for and process the user's response before asking the next question.
        -   **CONSTRAINT:** Limit your inquiry to a maximum of 5 questions.
        -   **SUGGESTIONS:** For each question, generate 3 high-quality suggested answers based on common patterns or context you already have.
        -   **Example Topics:** Target users, goals, features, etc
        *   **General Guidelines:**
            *   **CRITICAL:** You MUST ask questions sequentially (one by one). Do not ask multiple questions in a single turn.
            *   The last two options for every multiple-choice question MUST be "Type your own answer", and "Autogenerate and review project.md".
            - **Format:** Present these as a vertical list.
            - **Structure:**
                A) [Option A]
                B) [Option B]
                C) [Option C]
                D) [Type your own answer]
                E) [Autogenerate and review project.md]
    -   **FOR EXISTING PROJECTS (BROWNFIELD):** Ask project context-aware questions based on the code analysis.
    -   **AUTO-GENERATE LOGIC:** If the user selects option E, immediately stop asking questions, use your best judgment to infer the remaining details, generate the full `project.md` content, write it to the file, and proceed.
3.  **Draft the Document:** Generate the content for `project.md`.
    -   **CRITICAL:** The source of truth is **only the user's selected answer(s)**. Ignore unselected options.
4.  **User Confirmation Loop:** Present the drafted content for review.
    > "I've drafted the project guide. Please review:"
    >
    > A) **Approve:** The document is correct and we can proceed.
    > B) **Suggest Changes:** Tell me what to modify.
    - **Loop:** Apply changes and re-present, or break the loop on approval.
5.  **Write File:** Once approved, write to `kamma/project.md`.
6.  **Commit State:** Write to `kamma/setup_state.json`: `{"last_successful_step": "2.1_project_guide"}`
7.  **Continue:** Immediately proceed to the next section.

### 2.2 Generate Tech Stack (Interactive)
1.  **Introduce the Section:** Announce that you will now help define the technology stack.
2.  **Ask Questions Sequentially:** Ask one question at a time. Maximum 5 questions.
    -   **SUGGESTIONS:** Generate 3 high-quality suggested answers for each question.
    -   **Example Topics:** programming languages, frameworks, databases, etc
    -   **Format:** Present as vertical list with options A-E (E = autogenerate).
    -   **FOR EXISTING PROJECTS (BROWNFIELD):** State the inferred stack and ask for confirmation.
    -   **AUTO-GENERATE LOGIC:** If E selected, infer remaining details and generate.
3.  **Draft the Document:** Generate `tech-stack.md` content based on user answers only.
4.  **User Confirmation Loop:** Present for review, loop until approved.
5.  **Write File:** Write to `kamma/tech-stack.md`.
6.  **Commit State:** Write to `kamma/setup_state.json`: `{"last_successful_step": "2.2_tech_stack"}`
7.  **Continue:** Immediately proceed to the next section.

### 2.3 Select Workflow
1.  **Copy Initial Workflow:**
    -   Copy the default workflow template into `kamma/workflow.md`.
2.  **Customize Workflow:**
    -   Ask the user: "Do you want to use the default workflow or customize it?"
        -   A) Default
        -   B) Customize
    -   If the user chooses to **customize** (Option B):
        -   Present the workflow content and allow the user to suggest changes.
        -   Apply changes and confirm.
    -   **Commit State:** Write to `kamma/setup_state.json`: `{"last_successful_step": "2.3_workflow"}`

### 2.4 Finalization
1.  **Summarize Actions:** Present a summary of all actions taken during Phase 1.
2.  **Transition:** Announce that the initial setup is complete and proceed to define the first thread.

---

## 3.0 INITIAL PLAN AND THREAD GENERATION
**PROTOCOL: Interactively define project requirements, propose a single thread, and create the corresponding thread and its phased plan.**

### 3.1 Generate Project Requirements (Interactive)(For greenfield projects only)
1.  **Transition to Requirements:** Announce that you will now define high-level project requirements.
2.  **Analyze Context:** Read `kamma/project.md`.
3.  **Ask Questions Sequentially:** Maximum 5 questions with suggested answers.
    -   Format with options A-E (E = auto-generate).
4.  **Continue:** After gathering enough information, proceed.

### 3.2 Propose a Single Initial Thread (Automated + Approval)
1.  **State Your Goal:** Announce that you will propose an initial thread.
2.  **Generate Thread Title:** Analyze project context and generate a single thread title.
3.  **User Confirmation:** Present for review and approval.

### 3.3 Convert the Initial Thread into Artifacts (Automated)
1.  **State Your Goal:** Announce that you will create the artifacts for this initial thread.
2.  **Initialize Threads File:** Create `kamma/threads.md`:
    ```markdown
    # Project Threads

    This file lists all major threads for the project. Each thread has its own detailed plan in its respective folder.

    ---

    ## [ ] Thread: <Thread Description>
    *Link: [./kamma/threads/<thread_id>/](./kamma/threads/<thread_id>/)*
    ```
3.  **Generate Thread Artifacts:**
    a. **Generate Thread-Specific Spec & Plan:**
        i. Generate a detailed `spec.md`.
        ii. Generate a `plan.md`.
            - **CRITICAL:** The task structure must adhere to `kamma/workflow.md`.
            - **CRITICAL: Inject Phase Completion Tasks.** If a "Phase Completion" protocol exists in `workflow.md`, append a final verification task to each Phase.
    b. **Create Thread Artifacts:**
        i. **Generate Thread ID:** Format `shortname_YYYYMMDD`.
        ii. **Create Directory:** `kamma/threads/<thread_id>/`.
        iii. **Write `spec.md` and `plan.md`** in the new directory.

    c. **Commit State:** Write to `kamma/setup_state.json`: `{"last_successful_step": "3.3_initial_thread_generated"}`

    d. **Announce Progress:** Announce that the thread has been created.

### 3.4 Final Announcement
1.  **Announce Completion:** The project setup and initial thread generation are complete.
2.  **Next Steps:** Inform the user to run `/kamma:2-do` to begin work.
