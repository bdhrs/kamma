---
description: Scaffolds the project and sets up the Kamma environment
---

## 1.0 PURPOSE
You are an AI agent. Your job is to help set up a project with the Kamma workflow. Follow these instructions in order. Don't guess.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way to make progress, reassess, and keep going. Tell the user about important failures, but keep working unless the task truly cannot move forward.

TO-DO LIST: Keep a running to-do list for this command. Add work before you start it, tick items off as you finish them. You don't need a reminder every section — just keep the list current.

---

## 1.1 CHECK WHETHER SETUP IS ALREADY IN PROGRESS

1. **Read State File:** Check for `kamma/setup_state.json`.
   - If it doesn't exist, this is a new setup. Go to Step 1.2.
   - If it exists, read its content.

2. **Resume Based on State:**
   Let `STEP` = the value of `last_successful_step`.

   - `"2.1_project_guide"` → "Resuming: `project.md` is done. Next: `tech.md`." Go to **Section 2.2**.
   - `"2.2_tech"` → "Resuming: `project.md` and `tech.md` are done. Next: `kamma/workflow.md`." Go to **Section 2.3**.
   - `"2.3_workflow"` → "Resuming: docs are ready. Next: first thread." Go to **Section 3.0**.
   - `"3.3_initial_thread_generated"` → "Already initialized. Create a thread with `/kamma:1-plan` or start work with `/kamma:2-do`." Stop here.
   - Unrecognized → say the state is unclear, make the safest assumption, and continue.

---

## 1.2 BEFORE SETUP

Give a quick overview:

> "Welcome to Kamma. I'll help you set up the project in four steps:
> 1. **Project Discovery:** Check the current directory — new or existing project?
> 2. **Project Definition:** Define what it's for, who it's for, and the basic context.
> 3. **Workflow Setup:** Create `kamma/workflow.md` from the standard template.
> 4. **First Thread:** Create the first thread and plan so work can start.
>
> Let's get started!"

---

## 2.0 SET UP THE PROJECT

### 2.0.1 Figure Out What Kind of Project This Is

1. **Detect project maturity:**
   - **Existing project indicators:**
     - Version control: `.git`, `.svn`, `.hg`
     - If `.git` exists, run `git status --porcelain`. Non-empty output = existing project with uncommitted changes.
     - Dependency manifests: `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `pyproject.toml`
     - Source directories: `src/`, `app/`, `lib/` containing code files
     - If ANY of the above are found → existing project.
   - **New project:** ONLY if NONE of the above are found AND the directory is empty or has only generic docs without code.

2. **Choose the right flow:**

   **If existing project:**
   - Announce that an existing project was detected.
   - If `git status --porcelain` showed uncommitted changes: "WARNING: You have uncommitted changes. Please commit or stash them before proceeding — Kamma will be making changes."
   - **Analyze the codebase:**
     1. Announce you'll analyze the project.
     2. Start with `README.md` if it exists.
     3. Extend to other relevant files.
   - **Pick files carefully:**
     1. Check `.gitignore` and respect its patterns.
     2. List relevant files efficiently: `git ls-files --exclude-standard -co | xargs -n 1 dirname | sort -u`.
     3. Prioritize small, high-value files: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, etc.
     4. Files over 1MB: read only the first and last 20 lines.
   - **Work out the context:**
     1. Base analysis only on discovered files and directory structure — don't ask for more.
     2. Identify tools, systems, and platforms.
     3. Infer structure from the file tree (top 2 levels).
     4. Summarize the project goal in one sentence.
   - After the scan, go to **Section 2.1**.

   **If new project:**
   - Announce that a new project will be initialized.
   - Continue to the next step.

3. **Initialize Git (new projects only):**
   If no `.git` directory exists, run `git init` and tell the user.

4. **Ask about the project goal (new projects only):**
   Ask: "What is the goal of this project?" Wait for the response.
   - Run `mkdir -p kamma`.
   - Create `kamma/setup_state.json` with `{"last_successful_step": ""}`.
   - Write the response into `kamma/project.md` under `# Initial Concept`.

5. Continue to the next section.

### 2.1 Create `project.md`

1. Announce you'll help create `project.md`.

2. **Ask only what you need to.** For existing projects, the code answers most questions — focus on intent, not facts you can read. Batch all unknowns into a single round with suggested answers and wait.
   - 3 suggested answers per question, based on context.
   - Topics: what it's for, who it's for, one-off or ongoing, what it produces, how you'll know it worked.
   - Last two options for every question: "Type your own answer" and "Autogenerate and review project.md".
   - Present as vertical lists (A, B, C, D, E).
   - **Auto-generate (E selected):** stop asking, infer the rest, generate and write `project.md`, proceed.

3. Draft `project.md` with: What it is and why, Who it's for, One-off or ongoing, What it will produce, How you'll know it worked.
   - Source of truth is only the user's selected answers. Ignore unselected options.

4. Present for review:
   > "I've drafted the project guide. Please review:"
   >
   > A) **Approve** — correct, proceed.
   > B) **Suggest Changes** — tell me what to modify.

   Loop until approved.

5. Write to `kamma/project.md`.
6. Update state: `{"last_successful_step": "2.1_project_guide"}`
7. Continue.

### 2.2 Create `tech.md`

1. Announce you'll define the project's tech notes.

2. **Ask only what you need to.** For existing projects, state what you've inferred and ask the user to confirm or correct. Batch unknowns into a single round with suggested answers.
   - 3 suggested answers per question.
   - Topics: tools and platforms, who this is for, time or budget limits, available resources, what the output looks like.
   - Format: vertical list A–E (E = autogenerate).
   - **Auto-generate (E selected):** infer and generate.

3. Draft `tech.md` with: Tools & Platforms, Who This Is For, Constraints, Resources, What the output looks like.
   - Source of truth: user's answers only.

4. Present for review. Loop until approved.

5. Write to `kamma/tech.md`.
6. Update state: `{"last_successful_step": "2.2_tech"}`
7. Continue.

### 2.3 Create `kamma/workflow.md`

1. Copy `templates/workflow.md` (relative to the Kamma package root) into `kamma/workflow.md`.
2. Announce that `kamma/workflow.md` was created from the standard template. Don't offer customization during setup.
3. Update state: `{"last_successful_step": "2.3_workflow"}`

### 2.4 Wrap Up Setup

1. Summarize all actions taken during setup.
2. Announce that initial setup is complete and proceed to define the first thread.

---

## 3.0 CREATE THE FIRST THREAD

### 3.1 Generate Project Requirements (New Projects Only)

1. Announce you'll define high-level project requirements.
2. Read `kamma/project.md`.
3. Ask only what can't be answered from context. Batch with suggested answers (A–E, E = auto-generate). Wait for the response.
4. Once you have enough, continue.

### 3.2 Propose a Single Initial Thread

1. Announce you'll propose an initial thread.
2. Analyze project context and generate a single thread title.
3. Present for review and approval.

### 3.3 Create the Initial Thread Files

1. Announce you'll create the thread files.

2. **Generate thread files:**
   a. Generate `spec.md` with these sections:
      - Overview
      - What it should do
      - Assumptions & uncertainties
      - Constraints
      - How we'll know it's done
      - What's not included
      - If tied to a GitHub issue, include a reference near the top.

   b. Generate `plan.md`:
      - Structure must follow `kamma/workflow.md`.
      - **Every task must include a `→ verify:` line** with the concrete check.
      - Add an automatic verification task at the end of each phase — no manual approval gates.
      - If tied to a GitHub issue, include the same reference near the top.

   c. **Simplicity check.** Before writing, review for overengineering. Could this be simpler? If yes, simplify.

   d. Create thread directory: `kamma/threads/<YYYYMMDD_shortname>/`.
   e. Write `spec.md` and `plan.md` to the directory.
   f. If `kamma/threads.md` exists, delete it — legacy file.
   g. Update state: `{"last_successful_step": "3.3_initial_thread_generated"}`
   h. Announce the thread has been created.

### 3.4 Final Announcement

1. The project setup and initial thread are complete.
2. Tell the user to run `/kamma:2-do` to begin work.
