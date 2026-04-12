import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import typer

from kammika.agents import build_launch_command, describe_agent, get_agent_spec, supported_agent_keys
from kammika.config import KammikaConfig
from kammika.paths import config_path, kamma_dir, queue_path, target_repo_root
from kammika.ui import (
    console,
    error,
    info,
    muted,
    prompt_confirm,
    prompt_text,
    show_banner,
    success,
    warning,
    warm_panel,
)

IDLE_SLEEP_SECONDS = 3600

BRANCH_BANNER = """
▄▄                            ▄▄
██                            ██
████▄ ████▄  ▀▀█▄ ████▄ ▄████ ████▄
██ ██ ██ ▀▀ ▄█▀██ ██ ██ ██    ██ ██
████▀ ██    ▀█▄██ ██ ██ ▀████ ██ ██
"""

AGENT_BANNER = """
                         ██
 ▀▀█▄ ▄████ ▄█▀█▄ ████▄ ▀██▀▀
▄█▀██ ██ ██ ██▄█▀ ██ ██  ██
▀█▄██ ▀████ ▀█▄▄▄ ██ ██  ██
         ██
       ▀▀▀
"""

SLEEP_BANNER = """
      ▄▄
      ██
▄█▀▀▀ ██ ▄█▀█▄ ▄█▀█▄ ████▄
▀███▄ ██ ██▄█▀ ██▄█▀ ██ ██
▄▄▄█▀ ██ ▀█▄▄▄ ▀█▄▄▄ ████▀
                     ██
                     ▀▀
"""

DONE_BANNER = """
   ▄▄
   ██                                                   ██
▄████ ▄███▄ ████▄ ▄█▀█▄              ████▄ ▄█▀█▄ ██ ██ ▀██▀▀
██ ██ ██ ██ ██ ██ ██▄█▀              ██ ██ ██▄█▀  ███   ██
▀████ ▀███▀ ██ ██ ▀█▄▄▄   ██ ██ ██   ██ ██ ▀█▄▄▄ ██ ██  ██
"""

KAMMA_COMMAND_TEMPLATE = """
## 1.0 PURPOSE
You are an AI agent assistant for the Kamma spec-driven work framework. Your job is to take a thread from zero to done in a single run: plan it, implement it, review it, and finalize it.

**There are exactly two stops in this flow.** Everything else runs autonomously without asking the user.

1. **Present the plan** - show the spec and plan, wait for approval before implementing.
2. **Ask the user to test** - after implementation, ask the user to manually test. If they confirm it works, proceed to review and finalize immediately. Only ask "Can I review and finalize?" after fixing reported issues.

CRITICAL: Check the result of every tool call. If a tool call fails, do not stop. Try another sensible way to make progress, reassess, and keep going. Tell the user about important failures, but continue working unless the task truly cannot move forward by any reasonable path.

TO-DO LIST: Keep a to-do list for this entire command. Add the current section's work before you start it, update the list as you go, and use it to track progress until the command is complete.
At the end of every section in this file, tick off completed to-do items before you move on.

## 2.0 LOAD PROJECT CONTEXT
**Run silently. Do not stop.**

Try to read and use the best available project context from files such as:
- `kamma/project.md`
- `kamma/tech.md`
- `README.md`
- dependency manifests, source files, and other discoverable project docs

If any Kamma files are missing, do not stop and do not perform setup here. Continue with whatever context is discoverable from the repository.

`/kamma` is self-contained. Use only the context and rules in this command plus discoverable repo context.

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

## 3.0 PLAN THE THREAD
**Run silently. Do not stop except for the plan presentation.**

### 3.1 Get the Thread Description

- **If `{{args}}` is provided:** Use it as the thread description.
- **If `{{args}}` is empty:** Ask "What would you like to work on?" using the environment's native question or input tool when available; otherwise ask in a normal message. Wait for the response. This is a pre-flight question, not one of the two stops.

If the work is tied to a GitHub issue, ask for or preserve the issue number and include it directly in the thread description so it remains visible throughout the thread lifecycle.

Infer the thread type (feature, bug, chore, refactor) from the description. Do not ask.

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

### 3.2 Generate Spec and Plan

1. Read `kamma/project.md` and `kamma/tech.md` if they exist. Fill gaps from discoverable repo context. Treat loss of chat context and handoff to a different agent as the normal case, not an edge case. Only ask the user questions if absolutely necessary. If more information is still required, batch all necessary questions into a single round and use the environment's native question or input tools when available; otherwise ask them in one normal message and wait for the response. When a critical planning detail is missing and the repository does not answer it, ask instead of guessing.
2. Generate `spec.md` with sections for Overview, What it should do, Constraints, How we'll know it's done, and What's not included.
   - The spec must be self-contained and preserve the project context needed by a different agent in a later session.
   - Write down the relevant repo context you discovered, including current behavior, affected files or systems, important constraints, assumptions you are relying on, and any project-specific terminology or workflow details that matter to execution.
   - Do not rely on unstated chat context or "the agent already knows this" assumptions. Put the necessary context into the written spec.
   - If the thread is tied to a GitHub issue, include a dedicated issue reference near the top of `spec.md`.
3. Generate a self-contained `plan.md` with hierarchical Phases -> Tasks -> Sub-tasks using `[ ]` markers.
   - Assume the plan will be executed by a different agent with zero memory of this conversation.
   - Include the concrete context needed for execution: exact file paths to inspect or edit when known, the relevant code areas or docs to check, task ordering, verification steps, expected outcomes, and any assumptions or constraints that the executor must preserve.
   - Prefer explicit instructions over shorthand. A fresh agent should be able to execute the plan directly from `plan.md` without reconstructing missing context.
   - If the thread is tied to a GitHub issue, include the same issue reference near the top of `plan.md`.
4. The `plan.md` structure must be executable by this command on its own.
5. Make tasks concrete, sequential, and small enough to mark in progress and complete as the work proceeds.
6. Add an automatic verification task at the end of each phase. Do not add any phase-end manual testing or user confirmation step.

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

### 3.3 - STOP 1: Present the Plan

Present the spec and plan together and wait for approval:

> "Here is the plan for this thread. Please review and confirm before I start."
>
> **Spec:**
> ```markdown
> [spec.md content]
> ```
>
> **Plan:**
> ```markdown
> [plan.md content]
> ```
>
> "Reply 'go' to start, or tell me what to change."

Apply any requested changes and re-present until the user confirms. Then immediately continue.

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

### 3.4 Create Thread Files

1. Ensure `kamma/` and `kamma/threads/` exist.
2. Generate a thread ID in the format `YYYYMMDD_shortname`.
3. Check for name collisions in existing `kamma/threads/` directories. Use a variant if needed.
4. Create `kamma/threads/<thread_id>/`.
5. Write the confirmed `spec.md` to `kamma/threads/<thread_id>/spec.md`.
6. Write the confirmed `plan.md` to `kamma/threads/<thread_id>/plan.md`.
7. If `kamma/threads.md` exists, delete it — it is a legacy file that is no longer used.
8. Re-read the created thread files so later sections use the exact path that was written.

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

## 4.0 IMPLEMENT THE THREAD
**Run autonomously. Do not stop for phase checkpoints or mid-task confirmations.**

1. Read `kamma/threads/<thread_id>/spec.md` and `kamma/threads/<thread_id>/plan.md`.
3. Work through every unchecked task and sub-task in `plan.md` in sequential order.
4. For each task or sub-task:
   - Change `[ ]` to `[~]` before you begin.
   - Implement only the work required for that item.
   - Run the most relevant verification for that item.
   - If verification fails, attempt to fix it up to 2 times. If it still fails, note the remaining issue clearly in `plan.md` and continue if there is still a reasonable path forward.
   - Change `[~]` to `[x]` only after the item is implemented and locally verified, or after the remaining issue has been explicitly recorded.
5. At the end of each phase, run a broader automatic verification pass for that phase and complete the phase's verification task in `plan.md`.
6. Do not defer to any external process document at any point in this command.

### 4.1 - STOP 2: Ask the User to Test

When all planned implementation work is done and locally verified, explain specifically how to test the changes - what commands to run, what to click, what to observe, and what the expected outcome is. Then ask:

> "Please test it using the steps above and let me know when you're done, or if you found any issues."

Wait for the user's response.

- **If they confirm it works** (for example, "done", "looks good", "yes", "perfect"): proceed immediately to Section 5.0 without asking again.
- **If they report issues**: fix them, then ask: "Can I review and finalize the thread?" Keep fixing and re-asking until the user confirms. Never wait passively - always push forward.

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

## 5.0 REVIEW AND FINALIZE
**Runs autonomously once the user confirms.**

### 5.1 Review

**CRITICAL: You must actually perform the review before writing the file. Do not write `review.md` first and call it done.**

1. Re-read `kamma/threads/<thread_id>/spec.md` and `plan.md`.
2. Run `git diff` and read every changed file relevant to the thread.
3. Run the relevant test suite or verification commands and read the output.
4. For each of the following, read the relevant code and report what you found - do not skip any:
   - **Spec coverage:** Does every requirement in `spec.md` have a corresponding implementation?
   - **Plan completion:** Is every task in `plan.md` marked done and actually implemented?
   - **Code correctness:** Are there logic errors, missing cases, or broken assumptions in the changed files?
   - **Test coverage:** Do the tests verify the key behaviors described in the spec?
   - **Regressions:** Could any change break existing behavior?
5. For each finding, state severity (`blocking`, `major`, `minor`, `nit`), file and line, what is wrong, why it matters, and the recommended fix.
6. Fix any blocking or major findings immediately. Re-run relevant verification after each fix. Repeat until none remain.
7. Make sure `plan.md` reflects the actual state of the work before finishing the review.
8. Only then write `kamma/threads/<thread_id>/review.md` with:
   - Review date
   - Reviewer: `kamma (inline)`
   - Findings summary (count by severity, or `No findings`)
   - Verdict: `PASSED`

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

### 5.2 Finalize

1. If `kamma/project.md` exists and the thread changed anything significant about the project description, update it. If the file does not exist, do not stop and do not create it just for this command.
2. If `kamma/tech.md` exists and the thread changed tools, constraints, resources, or working assumptions, update it. If the file does not exist, do not stop and do not create it just for this command.
3. Ensure `kamma/archive/` exists.
4. Copy `kamma/threads/<thread_id>/` to `kamma/archive/<thread_id>/`. If that archive path already exists, choose a unique variant and continue.
5. Delete `kamma/threads/<thread_id>/` and all its contents.
6. If `kamma/threads.md` exists, delete it — it is a legacy file that is no longer used.
7. **Suggest commit message and description (do NOT run `git commit`):**
   - Draft a concise commit message (one line) that summarizes what changed.
   - Draft a commit description as a **single continuous line** (no line breaks) that explains what the issue was, what was changed, and how it was verified. This must be copy-paste friendly.
   - If a GitHub issue is referenced, include it in both: e.g., `fix: ensure consistent commit descriptions (closes #123)`
   - Present both to the user — do not execute the commit yourself:
     > **Commit message:** `<message>`
     > **Commit description:** `<single-line description>`
9. Announce that the thread is complete.

### 5.3 GitHub Issue

If the thread description, `spec.md`, or `plan.md` references a GitHub issue number (e.g., `#123`, `issue 123`, `fixes #123`):

1. Extract the issue number.
2. Summarize the fix in 2–4 sentences: what the issue was, what was changed, and how it was verified.
3. Use `gh issue comment <number> --body "<summary>"` to post the fix summary to the issue.
4. Use `gh issue close <number>` to close the issue.
5. Provide the user with a suggested commit message that references the same issue number, for example:
   > `fix: <short description> (closes #<number>)`

If no issue is referenced, skip this section entirely.

6. At the end of the finalize process, always suggest a commit name using the repository's commit syntax if one is evident. If no clear syntax is discoverable, provide a concise sensible commit name. When an issue number exists, the suggested commit name must include it.

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.

### 5.4 Reflect and Learn
**Run autonomously. Keep the user informed but do not ask for approval.**

1. Reflect on the conversation that just happened. Identify moments where:
   - The user had to correct you or repeat an instruction (`[REPEATED]`)
   - There was process friction or wasted effort (`[WORKFLOW]`)
   - You misunderstood something (`[CONFUSION]`)
   - You violated a rule or missed an expected action (`[BEHAVIOR]`)
   - Something worked particularly well (`[POSITIVE]`)
2. If there is nothing notable, skip the rest of this section.
3. Append each observation as a one-liner to `kamma/lessons.md` (create the file if it does not exist). Format:
   - YYYY-MM-DD [TAG] Short description of what happened
4. Read the full `kamma/lessons.md`. For each lesson that suggests a concrete, lasting improvement to agent instructions, classify it before editing any instruction file:
   - `local`: specific to this repository, its workflow, its codebase, or its maintainers' conventions
   - `global`: useful across projects and not tied to this repository
5. Write the instruction to the matching target:
   - For `local` lessons, update the repository instruction file at the repo root. Prefer an existing `AGENTS.md`, then `AGENT.md`, then `CLAUDE.md`. If none exist, create `AGENTS.md` at the repo root.
   - For `global` lessons, update the global instruction file at `~/.agents/AGENTS.md`. Create it if it does not exist.
6. Keep additions minimal: one or two sentences per rule. Tell the user which target you updated for each new rule and why you classified it as local or global.
7. If no improvements apply, say nothing and move on.

**To-Do List Reminder:** Before you leave this section, tick off completed items on your to-do list and update anything still in progress.
"""

RUN_BANNER = """

▄▄                             ▀▀  ▄▄
██ ▄█▀  ▀▀█▄ ███▄███▄ ███▄███▄ ██  ██ ▄█▀  ▀▀█▄
████   ▄█▀██ ██ ██ ██ ██ ██ ██ ██  ████   ▄█▀██
██ ▀█▄ ▀█▄██ ██ ██ ██ ██ ██ ██ ██▄ ██ ▀█▄ ▀█▄██

"""


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, cwd=cwd)


def _dirty_tree(repo_root: Path) -> bool:
    result = _run(["git", "status", "--porcelain"], cwd=repo_root)
    return bool(result.stdout.strip())


def _wait_for_clean_tree(repo_root: Path) -> None:
    while _dirty_tree(repo_root):
        warning(
            "Your working tree has uncommitted changes. Stash, commit, or otherwise clean it, then press Enter to continue."
        )
        prompt_text("Press Enter when ready", default="")


def _current_branch(repo_root: Path) -> str:
    result = _run(["git", "branch", "--show-current"], cwd=repo_root)
    return result.stdout.strip() or "current branch"


def _branch_exists(name: str, repo_root: Path) -> bool:
    result = _run(["git", "branch", "--list", name], cwd=repo_root)
    return bool(result.stdout.strip())


def _make_thread_id(title: str) -> str:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:40]
    return f"{date}_{slug}"


def _unique_thread_id(base: str, repo_root: Path) -> str:
    threads_dir = repo_root / "kamma" / "threads"
    if not (threads_dir / base).exists():
        return base
    i = 2
    while (threads_dir / f"{base}_{i}").exists():
        i += 1
    return f"{base}_{i}"


def _checkout_branch(branch: str, repo_root: Path) -> bool:
    if _branch_exists(branch, repo_root):
        result = _run(["git", "checkout", branch], cwd=repo_root)
    else:
        result = _run(["git", "checkout", "-b", branch], cwd=repo_root)
    return result.returncode == 0


def _launch_agent(
    initial_instruction: str,
    agent: str,
    repo_root: Path,
    models: dict[str, str] | None = None,
) -> int:
    spec = get_agent_spec(agent)
    if spec is None:
        error(f"Unknown agent '{agent}'.")
        return 1

    cmd = build_launch_command(agent, initial_instruction, models=models)
    info(f"Launching {describe_agent(agent, models)}...")
    try:
        result = subprocess.run(cmd, cwd=str(repo_root))
    except FileNotFoundError:
        error(f"{spec.label} is not available on PATH. Run `kammika init` again to refresh detected agents.")
        return 1

    if result.returncode != 0:
        error(f"{spec.label} exited with code {result.returncode}. Queue preserved for retry.")
    return result.returncode


def _choose_agent(agents: list[str]) -> str:
    available = supported_agent_keys(agents)
    if not available:
        error("No supported agents are configured. Run `kammika init` to detect local agents.")
        raise typer.Exit(1)

    console.print()
    for i, agent in enumerate(available, 1):
        spec = get_agent_spec(agent)
        muted(f"{i}. {spec.label if spec else agent}")
    console.print()

    while True:
        choice = prompt_text(f"Choose agent [1-{len(available)}]", default="1")
        try:
            idx = int(choice) - 1
        except ValueError:
            idx = -1
        if 0 <= idx < len(available):
            return available[idx]
        warning(f"Enter a number between 1 and {len(available)}.")


def _choose_branch_mode(repo_root: Path) -> str:
    current = _current_branch(repo_root)
    console.print()
    console.print(BRANCH_BANNER, style="banner")
    console.print()
    muted(f"1. Current branch ({current})")
    muted("2. New branch")
    console.print()

    while True:
        choice = prompt_text("Choose branch mode [1-2]", default="1")
        if choice == "1":
            return "current"
        if choice == "2":
            return "new"
        warning("Enter 1 or 2.")


def _load_pending_queue() -> dict | None:
    qp = queue_path()
    if not qp.exists():
        return None
    try:
        queue = json.loads(qp.read_text())
    except json.JSONDecodeError:
        return None
    if isinstance(queue, dict) and queue.get("number"):
        return queue
    return None


def _remaining_issue_count(config: KammikaConfig, pending_number: int | None = None) -> int | None:
    try:
        from kammika.commands import triage as triage_command

        issue_candidates = triage_command._fetch_issues(config.repo)
        merged = {candidate.number: candidate for candidate in issue_candidates}

        if config.project:
            owner, proj_number = triage_command._parse_project_ref(config.project)
            project_status = triage_command._fetch_project_items(owner, proj_number)
            for number, status in project_status.items():
                if number in merged:
                    merged[number].status = status

        filtered = [
            candidate
            for candidate in merged.values()
            if candidate.status.lower() not in triage_command._BLOCKED_STATUSES
        ]
        claimed = triage_command._claimed_issue_numbers()
        remaining = [candidate for candidate in filtered if candidate.number not in claimed]
        if pending_number is not None:
            remaining = [candidate for candidate in remaining if candidate.number != pending_number]
        return len(remaining)
    except Exception:
        return None


def _print_session_summary(completed_count: int, config: KammikaConfig | None = None) -> None:
    pending = _load_pending_queue()
    pending_number = pending.get("number") if pending else None
    remaining_count = _remaining_issue_count(config, pending_number) if config else None

    parts = [f"Completed this session: {completed_count}"]
    if pending_number is not None:
        parts.append(f"pending issue: #{pending_number}")
    else:
        parts.append("pending issue: none")

    if remaining_count is not None:
        parts.append(f"remaining actionable issues: {remaining_count}")

    console.print()
    console.print(warm_panel(f"[info]{' | '.join(parts)}[/info]", "kammika stopped"))
    console.print()


def _build_initial_instruction(number: int, title: str, body: str) -> str:
    issue_description = f"{number}: {title}".strip()
    if body.strip():
        issue_description = f"{issue_description}\n{body.strip()}"
    command_body = KAMMA_COMMAND_TEMPLATE.replace("{{args}}", issue_description)
    issue_context_steps = (
        f"Before doing anything else, get up to date on this issue:\n"
        f"1. Run `gh issue view {number} --comments` to read the full issue and all comments.\n"
        f"2. Run `git log --oneline --all --grep='#{number}'` to find any related commits.\n"
        f"This ensures your plan reflects the current state of the work.\n\n"
    )
    return (
        "Follow the full Kamma command below exactly. It is inlined here because slash-command "
        "resolution is not available from this launched session.\n\n"
        f"{issue_context_steps}"
        f"{command_body.strip()}\n"
    )


PAGE_SIZE = 4


def _queue_issue(candidate, source: str, rationale: str) -> dict:
    queue = {
        "number": candidate.number,
        "title": candidate.title,
        "body": candidate.body,
        "rationale": rationale,
        "source": source,
        "picked_at": datetime.now(timezone.utc).isoformat(),
    }
    queue_path().write_text(json.dumps(queue, indent=2) + "\n")
    return queue


def _show_issue_table(
    candidates: list, recommended_number: int | None, page: int, total: int
) -> None:
    from rich.table import Table

    table = Table(show_header=True, header_style="question", expand=False)
    table.add_column("#", style="question", width=3, no_wrap=True)
    table.add_column("Issue", style="muted", width=7, no_wrap=True)
    table.add_column("Title")
    table.add_column("Labels", style="muted")
    table.add_column("Age", style="muted", width=6, no_wrap=True)

    for i, c in enumerate(candidates, 1):
        label_str = ", ".join(c.labels) if c.labels else ""
        title = c.title
        if c.number == recommended_number:
            title = f"[success]★ {title}[/success]"
        table.add_row(str(i), f"#{c.number}", title, label_str, f"{c.age_days}d")

    start = page * PAGE_SIZE + 1
    end = start + len(candidates) - 1
    console.print()
    console.print(table)
    console.print()
    muted(f"Showing {start}–{end} of {total}  |  n = next  |  q = quit")
    console.print()


def _pick_issue(config: KammikaConfig) -> dict | None:
    """Return a queue dict: confirm pending issue or let user page through candidates."""
    from kammika.commands.triage import TRIAGE_BANNER, get_candidates, _llm_pick

    pending = _load_pending_queue()
    if pending and pending.get("number"):
        number = pending["number"]
        title = pending.get("title", "")
        console.print()
        console.print(
            warm_panel(
                f"[question]#{number}:[/question] {title}",
                "Pending issue",
            )
        )
        console.print()
        if prompt_confirm("Start with this issue?", default=True):
            return pending
        queue_path().write_text("{}\n")

    show_banner(TRIAGE_BANNER)

    candidates = get_candidates(config)
    if not candidates:
        warning("No actionable issues found.")
        return None

    if len(candidates) == 1:
        chosen = candidates[0]
        success(f"Auto-selected issue #{chosen.number} because it is the only actionable issue.")
        return _queue_issue(
            chosen,
            source="automatic",
            rationale="Auto-selected because it is the only actionable issue",
        )

    llm_agent = next((agent for agent in config.agents if agent in {"claude", "opencode"}), None)
    if llm_agent is not None:
        muted(f"Asking {describe_agent(llm_agent, config.models)} for a recommendation...")
    else:
        muted("No configured recommendation model available; showing issues without a model recommendation.")
    recommended = _llm_pick(candidates, config.agents, config.models)

    total = len(candidates)
    page = 0

    while True:
        start = page * PAGE_SIZE
        page_candidates = candidates[start : start + PAGE_SIZE]

        _show_issue_table(page_candidates, recommended, page, total)

        n = len(page_candidates)
        while True:
            choice = prompt_text(f"Pick an issue [1-{n}/n/q]", default="n")
            val = choice.strip().lower()
            if val == "q":
                return None
            if val == "n":
                break
            try:
                idx = int(choice) - 1
            except ValueError:
                idx = -1
            if 0 <= idx < n:
                chosen = page_candidates[idx]
                return _queue_issue(chosen, source="user", rationale="Selected by user")
            warning(f"Enter a number between 1 and {n}, 'n' for next, or 'q' to quit.")

        num_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        page = (page + 1) % num_pages


def _sleep_until_next_check() -> None:
    show_banner(SLEEP_BANNER)
    info("No issue is ready right now. I will check again in 1 hour. Press Ctrl-C to stop.")
    console.print()
    time.sleep(IDLE_SLEEP_SECONDS)
    console.print()


def run_cycle() -> None:
    show_banner(RUN_BANNER)

    cfg_path = config_path()
    if not cfg_path.exists():
        error("kamma/kammika.config.json not found. Run `kammika init` first.")
        raise typer.Exit(1)

    try:
        repo_root = target_repo_root()
    except RuntimeError as exc:
        error(f"Error: {exc}")
        raise typer.Exit(1)

    config = KammikaConfig.from_dict(json.loads(cfg_path.read_text()))
    completed_count = 0

    try:
        while True:
            queue = _pick_issue(config)
            if queue is None:
                _sleep_until_next_check()
                continue

            number = queue.get("number")
            title = queue.get("title", "")
            body = queue.get("body", "")

            if not number:
                warning("Queue file is empty or invalid. Nothing to do.")
                _sleep_until_next_check()
                continue

            thread_id_base = _make_thread_id(title)
            thread_id = _unique_thread_id(thread_id_base, repo_root)
            branch = f"kammika/{thread_id}"

            branch_mode = _choose_branch_mode(repo_root)

            if branch_mode == "new":
                console.print()
                _wait_for_clean_tree(repo_root)
                muted(f"Creating branch: {branch}")
                if not _checkout_branch(branch, repo_root):
                    error(f"Could not create or checkout branch '{branch}'.")
                    _print_session_summary(completed_count, config)
                    raise typer.Exit(1)
                success(f"On branch {branch}")
                console.print()
            else:
                console.print()
                success(f"Staying on {_current_branch(repo_root)}")
                console.print()

            selected_agent = _choose_agent(config.agents)
            initial_instruction = _build_initial_instruction(number, title, body)

            console.print()
            console.print(
                warm_panel(
                    f"[question]Issue #{number}:[/question] {title}\n\n[muted]{body[:300]}{'…' if len(body) > 300 else ''}[/muted]",
                    "Starting agent session",
                )
            )
            console.print()

            show_banner(AGENT_BANNER)
            exit_code = _launch_agent(
                initial_instruction,
                selected_agent,
                repo_root,
                models=config.models,
            )

            if exit_code == 0:
                completed_count += 1
                queue_path().write_text("{}\n")
                show_banner(DONE_BANNER)
                continue

            _print_session_summary(completed_count, config)
            raise typer.Exit(exit_code)
    except KeyboardInterrupt:
        _print_session_summary(completed_count, config)
        raise typer.Exit(130)
