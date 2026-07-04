---
description: Plans a standing loop thread for repeated cycles of work
---

## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to create a new **loop thread** — a standing thread for repeated cycles of report → analyze → approve → implement → validate.

CRITICAL: Check the result of every tool call. If a tool call fails, don't stop. Try another way to make progress, reassess, and keep going. Tell the user about important failures, but keep working unless the task truly cannot move forward.

TO-DO LIST: Keep a running to-do list for this command. Add work before you start it, tick items off as you finish them. You don't need a reminder every section — just keep the list current.

## 1.1 SETUP CHECK
**Verify that the Kamma environment is set up.**

1. Check for these files:
   - `kamma/tech.md`
   - `kamma/workflow.md`
   - `kamma/project.md`

2. If any are missing, say what's missing and try to continue. Announce: "Kamma is not set up. Please run `/kamma:0-setup` to set up the environment." Keep going if there's still a reasonable path.

---

## 2.0 CREATE A NEW LOOP THREAD

### 2.0.1 Question Tool Rule

**CRITICAL: Never ask questions in plain markdown or plain chat.** Every question to the user must go through a native question/input tool (e.g., `AskUserQuestion`, `request_user_input`). Only fall back to a plain message if the tool call fails.

### 2.1 Get the Loop Description

1. **Get the description:**
   - **If `{{args}}` has one:** Use it.
   - **If `{{args}}` is empty:** Use the native question/input tool to ask: "Please provide a brief description of the work loop (e.g., 'Exporter analysis', 'Bug triage', 'Log monitoring') you want to start." Wait for the response.
2. If the work is tied to a GitHub issue, ask for or preserve the issue number.

### 2.2 Write `spec.md`

1. **Surface assumptions and define the loop domain.** Use the native question/input tool to ask the following questions (batch them):
   - **Domain:** What specific domain or system does this loop govern?
   - **In-Scope:** What kinds of issues or tasks are in-scope for this loop?
   - **Out-of-Scope:** What should this loop explicitly IGNORE?
   - **Validation:** What are the recurring validation standards for every cycle?
   - **Completion:** Under what condition is this standing loop considered "finished"?
   - **Model Tiers (Optional):** "Use model splitting (Fast/Pro) for cycle execution?" (Options: Yes, No).

2. Draft `spec.md` with these sections:
   - `> **Thread type:** Loop (standing thread)` (Required marker)
   - Overview
   - Loop Domain
   - In-Scope vs Out-of-Scope
   - Validation Standards
   - Completion Condition
   - Assumptions & uncertainties
   - Constraints
   - How we'll know it's done (overall)

   If tied to a GitHub issue, include a dedicated reference near the top.

3. Present the draft for review and revise until confirmed.

### 2.3 Write `plan.md` (Protocol)

1. Announce: "Now I'll create the protocol-style `plan.md` for this loop."

2. Generate `plan.md` with the following structure (do not use `[ ]` task markers for the protocol):
   - `> **Thread type:** Loop (standing thread)` (Required marker)
   - **Architecture Decisions** (Rationales for the loop structure)
   - **Per-Cycle Protocol:**
     1. **Report:** Identify the next issue or task in the domain.
     2. **Analyze:** Assess the issue, propose a fix, and define validation.
     3. **Approval (HARD STOP):** Present the analysis and WAIT for explicit user approval before any source/test edits.
     4. **Implement:** Apply the approved fix only.
     5. **Validate:** Run the defined validation.
     6. **Record:** Write the cycle record to `cycles/NNNN_slug.md`.
     7. **Handoff:** Update `handoff.md` with current state.
     8. **Learn:** Curate `learnings.md` (distill new lessons, prune stale ones).
   - **Read Contract:** A cycle reads only `spec.md`, `plan.md`, `handoff.md`, and `learnings.md`. Full cycle records are read only on demand.

3. Present the draft for review and revise until confirmed.

### 2.4 Create the Thread Files

1. Generate thread ID: `YYYYMMDD_shortname`.
2. Create `kamma/threads/<thread_id>/`.
3. Write `spec.md`, `plan.md`, `handoff.md` (initial state), and `learnings.md` (seeded with headers).
4. Create `kamma/threads/<thread_id>/cycles/` and add a `.gitkeep`.
5. Announce: "Loop thread '<thread_id>' created. Start the first cycle with `/kamma:2-do <thread_id>`."

---

## 3.0 SYNC NOTE
Keep these commands aligned with loop-aware logic: `2-do`, `3-review`, `4-finalize`, `handoff`.
