---
description: Scaffolds the project and sets up the Kamma environment
---

## 1.0 PURPOSE
You are an AI agent. Your job is to help set up a project with the Kamma workflow. Follow these instructions in order. Do not guess.

CRITICAL: Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

TO-DO LIST: Keep a to-do list for this entire command. Add the current section's work before you start it, update the list as you go, and use it to track progress until the command is complete.
At the end of every section in this file, tick off completed to-do items before you move on.

---

## 1.1 CHECK WHETHER SETUP IS ALREADY IN PROGRESS
**Before starting setup, check the state file to see where things left off.**

1.  **Read State File:** Check for the existence of `kamma/setup_state.json`.
    - If it does not exist, this is a new project setup. Proceed directly to Step 1.2.
    - If it exists, read its content.

2.  **Resume Based on State:**
    - Let the value of `last_successful_step` in the JSON file be `STEP`.
    - Based on the value of `STEP`, jump to the next section.

    - If `STEP` is "2.1_project_guide", announce "Resuming setup: `project.md` is already done. Next, we will define `tech.md`." and proceed to **Section 2.2**.
    - If `STEP` is "2.2_tech", announce "Resuming setup: `project.md` and `tech.md` are already done. Next, we will create `kamma/workflow.md` for this project." and proceed to **Section 2.3**.
    - If `STEP` is "2.3_workflow", announce "Resuming setup: `project.md`, `tech.md`, and `kamma/workflow.md` are ready. Next, we will generate the first thread." and proceed to **Phase 2 (3.0)**.
    - If `STEP` is "3.3_initial_thread_generated":
        - Announce: "The project has already been initialized. You can create a new thread with `/kamma:1-plan` or start working on an existing thread with `/kamma:2-do`."
        - End setup here and tell the user what they can do next.
    - If `STEP` is unrecognized, say that the state is unclear, make the safest reasonable assumption you can, and continue from there.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 1.2 BEFORE SETUP
1.  **Give a Quick Overview:**
    -   Present the following overview of the setup process to the user:
        > "Welcome to Kamma. I will help you set up the project in four steps:
        > 1. **Project Discovery:** Check the current directory and figure out whether this is a new or existing project.
        > 2. **Project Definition:** Define what the project is for, who it is for, and the basic context.
        > 3. **Workflow Setup:** Create `kamma/workflow.md` from the standard Kamma workflow.
        > 4. **First Thread:** Create the first thread and a detailed plan so work can start.
        >
        > Let's get started!"

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 2.0 SET UP THE PROJECT
**Follow this sequence to perform a guided setup with the user.**

### 2.0.1 Figure Out What Kind of Project This Is
1.  **Detect Project Maturity:**
    -   **Classify Project:** Determine if the project is an existing project or a new one based on the following indicators.
    -   **Existing Project Indicators:**
        -   Check for existence of version control directories: `.git`, `.svn`, or `.hg`.
        -   If a `.git` directory exists, execute `git status --porcelain`. If the output is not empty, classify as an existing project with uncommitted changes.
        -   Check for dependency manifests: `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `pyproject.toml`.
        -   Check for source code directories: `src/`, `app/`, `lib/` containing code files.
        -   If ANY of the above conditions are met, classify as an existing project.
    -   **New Project Condition:**
        -   Classify as a new project ONLY if NONE of the above indicators are found AND the current directory is empty or contains only generic documentation (for example, a single `README.md` file) without functional code or dependencies.

2.  **Choose the Right Flow:**
    -   **If Existing Project:**
        -   Announce that an existing project has been detected.
        -   If the `git status --porcelain` command showed uncommitted changes, tell the user: "WARNING: You have uncommitted changes in your Git repository. Please commit or stash them before proceeding, because Kamma will be making changes."
        -   **Begin Existing Project Setup:**
            -   **2.0 Analyze the Codebase:**
                1.  **Announce Action:** Inform the user that you will now analyze the project.
                2.  **Prioritize README:** Begin by analyzing the `README.md` file, if it exists.
                3.  **Broader Scan:** Extend the analysis to other relevant files to understand the project's purpose, technologies, and conventions.

            -   **2.1 Pick Files Carefully:**
                1.  **Respect Ignore Files:** Before scanning any files, check for `.gitignore` files. Use their patterns to exclude files and directories from your analysis.
                2.  **Efficiently List Relevant Files:** Use a command that respects the ignore files. For example: `git ls-files --exclude-standard -co | xargs -n 1 dirname | sort -u`.
                3.  **Prioritize Key Files:** Focus on high-value, low-size files first, such as `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, and other configuration or manifest files.
                4.  **Handle Large Files:** For any single file over 1MB, DO NOT read the entire file. Instead, read only the first and last 20 lines to infer its purpose.

            -   **2.2 Work Out the Project Context:**
                1.  **Strict File Access:** DO NOT ask for more files. Base your analysis ONLY on the provided file snippets and directory structure.
                2.  **Extract Tools & Platforms:** Identify tools, systems, or platforms in use.
                3.  **Infer Structure:** Use the file tree skeleton (top 2 levels) to infer the project's organization.
                4.  **Infer Project Goal:** Summarize the project's goal in one sentence.
        -   **After finishing the existing-project scan, proceed to Section 2.1.**
    -   **If New Project:**
        -   Announce that a new project will be initialized.
        -   Proceed to the next step in this file.

3.  **Initialize Git Repository (for New Projects):**
    -   If a `.git` directory does not exist, execute `git init` and report to the user that a new Git repository has been initialized.

4.  **Ask About the Project Goal (for New Projects):**
    -   **Ask the user the following question using the environment's native question or input tool when available; otherwise ask it in a normal message, and wait for their response before proceeding:** "What is the goal of this project?"
    -   **CRITICAL: You MUST NOT execute any tool calls until the user has provided a response.**
    -   **Upon receiving the user's response:**
        -   Execute `mkdir -p kamma`.
        -   **Initialize State File:** Create `kamma/setup_state.json` with: `{"last_successful_step": ""}`
        -   Write the user's response into `kamma/project.md` under a header named `# Initial Concept`.

5.  **Continue:** Immediately proceed to the next section.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 2.1 Create `project.md`
1.  **Introduce the Section:** Announce that you will now help the user create `project.md`.
2.  **Ask Only What You Need To:** Only ask questions when the answer is not already clear from the codebase or context. For existing projects, the code itself answers most things — focus questions on intent, not facts you can read. Batch all remaining unknowns into a single round of questions and wait for the response before continuing. Use the environment's native question or input tools when available; otherwise send one normal message containing the full batch.
        -   **SUGGESTIONS:** For each question in the batch, generate 3 high-quality suggested answers based on common patterns or context you already have.
        -   **Example Topics:** what the project is for, who it is for, whether it is a one-off or ongoing, what it will produce, how you'll know it worked.
        *   **General Guidelines:**
            *   Ask all necessary unresolved questions together in a single batch.
            *   Present each question as its own block in the batch.
            *   The last two options for every multiple-choice question MUST be "Type your own answer", and "Autogenerate and review project.md".
            - **Format:** Present these as a vertical list.
            - **Structure:**
                A) [Option A]
                B) [Option B]
                C) [Option C]
                D) [Type your own answer]
                E) [Autogenerate and review project.md]
    -   **FOR EXISTING PROJECTS:** The codebase already answers most questions. Only ask about things you genuinely cannot infer.
    -   **AUTO-GENERATE LOGIC:** If the user selects option E, immediately stop asking questions, use your best judgment to infer the remaining details, generate the full `project.md` content, write it to the file, and proceed.
3.  **Draft the Document:** Generate the content for `project.md`. Include sections for: What it is and why, Who it is for, One-off or ongoing, What it will produce, and How you'll know it worked.
    -   **CRITICAL:** The source of truth is **only the user's selected answer(s)**. Ignore unselected options.
4.  **Review Loop:** Present the drafted content for review.
    > "I've drafted the project guide. Please review:"
    >
    > A) **Approve:** The document is correct and we can proceed.
    > B) **Suggest Changes:** Tell me what to modify.
    - **Loop:** Apply changes and re-present, or break the loop on approval.
5.  **Write File:** Once approved, write to `kamma/project.md`.
6.  **Commit State:** Write to `kamma/setup_state.json`: `{"last_successful_step": "2.1_project_guide"}`
7.  **Continue:** Immediately proceed to the next section.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 2.2 Create `tech.md`
1.  **Introduce the Section:** Announce that you will now help define the project's tech notes.
2.  **Ask Only What You Need To:** Only ask about things you cannot infer from the codebase or prior answers. For existing projects, state what you've inferred and ask the user to confirm or correct it rather than asking from scratch. Batch all remaining unknowns into a single round of questions. Use the environment's native question or input tools when available; otherwise send one normal message containing the full batch and wait for the response.
    -   **SUGGESTIONS:** Generate 3 high-quality suggested answers for each question in the batch.
    -   **Example Topics:** tools and platforms being used, who this is for, any time or budget limits to be aware of, available resources, what the output looks like.
    -   **Format:** Present each question as its own vertical list with options A-E (E = autogenerate).
    -   **AUTO-GENERATE LOGIC:** If E selected, infer remaining details and generate.
3.  **Draft the Document:** Generate `tech.md` content based on user answers only. Include sections for: Tools & Platforms, Who This Is For, Constraints, Resources, and What the output looks like.
4.  **Review Loop:** Present for review, loop until approved.
5.  **Write File:** Write to `kamma/tech.md`.
6.  **Commit State:** Write to `kamma/setup_state.json`: `{"last_successful_step": "2.2_tech"}`
7.  **Continue:** Immediately proceed to the next section.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 2.3 Create `kamma/workflow.md`
1.  **Copy Initial Workflow:**
    -   Copy the default workflow template into `kamma/workflow.md`.
2.  **Explain What Was Created:**
    -   Announce that `kamma/workflow.md` is the project's workflow file and that setup created it from the bundled Kamma template.
    -   Do not offer workflow customization during setup.
3.  **Commit State:**
    -   Write to `kamma/setup_state.json`: `{"last_successful_step": "2.3_workflow"}`


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 2.4 Wrap Up Setup
1.  **Summarize Actions:** Present a summary of all actions taken during setup.
2.  **Transition:** Announce that the initial setup is complete and proceed to define the first thread.

---


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


## 3.0 CREATE THE FIRST THREAD
**Define the project requirements, propose a single thread, and create the thread folder and plan.**

### 3.1 Generate Project Requirements (For New Projects Only)
1.  **Transition to Requirements:** Announce that you will now define high-level project requirements.
2.  **Analyze Context:** Read `kamma/project.md`.
3.  **Ask Only What You Need To:** Only ask questions that cannot be answered from the codebase or project context. Ask all necessary questions in a single batch with suggested answers in A-E format for each question (E = auto-generate). Use the environment's native question or input tools when available; otherwise send one normal message containing the full batch and wait for the response.
4.  **Continue:** Once you have enough to proceed, do so.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 3.2 Propose a Single Initial Thread
1.  **State Your Goal:** Announce that you will propose an initial thread.
2.  **Generate Thread Title:** Analyze project context and generate a single thread title.
3.  **User Confirmation:** Present for review and approval.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 3.3 Create the Initial Thread Files
1.  **State Your Goal:** Announce that you will create the files for this initial thread.
2.  **Initialize Threads File:** Create `kamma/threads.md`:
    ```markdown
    # Project Threads

    This file lists all major threads for the project. Each thread has its own detailed plan in its respective folder.

    ---

    ## [ ] Thread: <Thread Description>
    *Link: [./kamma/threads/<thread_id>/](./kamma/threads/<thread_id>/)*
    ```
3.  **Generate Thread Files:**
    a. **Generate Thread-Specific Spec & Plan:**
        i. Generate a detailed `spec.md`.
        ii. Generate a `plan.md`.
            - **CRITICAL:** The task structure must adhere to `kamma/workflow.md`.
            - **CRITICAL: Inject Phase Completion Tasks.** If a "Phase Completion" protocol exists in `workflow.md`, append a final verification task to each Phase.
    b. **Create Thread Files:**
        i. **Generate Thread ID:** Format `YYYYMMDD_shortname`.
        ii. **Create Directory:** `kamma/threads/<thread_id>/`.
        iii. **Write `spec.md` and `plan.md`** in the new directory.

    c. **Commit State:** Write to `kamma/setup_state.json`: `{"last_successful_step": "3.3_initial_thread_generated"}`

    d. **Announce Progress:** Announce that the thread has been created.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.


### 3.4 Final Announcement
1.  **Announce Completion:** The project setup and initial thread generation are complete.
2.  **Next Steps:** Inform the user to run `/kamma:2-do` to begin work.


**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.
