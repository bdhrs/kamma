---
description: Sweep kamma lessons across every repo, find recurring mistakes, and consolidate them into durable improvements to the kamma framework itself.
---

## 1.0 PURPOSE
You are an AI agent for the Kamma framework. This is the cross-repo self-improvement loop. `/kamma:4-finalize` writes a `kamma/lessons.md` line after each thread; over time the same mistakes recur across repos. This command reads those lessons from every repo on the machine, finds the patterns that keep repeating, and turns them into lasting improvements to the **kamma framework itself** — the command prompts, the skill, and the templates.

Division of labour with finalize:
- `/kamma:4-finalize` reflect → repo-local + immediate; it owns the **agent files** (local and global).
- `kamma-improve` → systemic + cross-repo; it owns the one thing finalize cannot reach: the **kamma framework prompts/skill**.

CRITICAL: Check the result of every tool call. If one fails, don't stop — try another way, reassess, and keep going. Tell the user about important failures.

TO-DO LIST: Keep a running to-do list for this command. Add work before you start it, tick items off as you finish.

### 1.1 Boundaries (read before doing anything)
- **Run anywhere, write only inside the kamma source repo.** Reading roams the whole machine; the ONLY files you may modify are the kamma framework files and the backlog `kamma/improve.md`, both under the located kamma repo.
- **Never** edit agent files (`AGENTS.md` / `CLAUDE.md`, local or global) — finalize owns those. **Never** edit any other repo. **Never** run git that writes — no commit, push, or add. (Read-only `git log` for the Phase 5 staleness check is fine.)
- **Question Tool Rule:** every question to the user goes through a native question tool (`AskUserQuestion` first, then `request_user_input`). Fall back to plain chat only if the tool call actually fails.

---

## 2.0 LOCATE THE KAMMA REPO
The kamma source repo is the only valid write target. Its fingerprint is a directory containing all three of: `commands/kamma.md`, `scripts/sync.py`, `skills/kamma/SKILL.md`.

1. If the current working directory matches the fingerprint, use it.
2. Otherwise find it during the lesson scan (Phase 3). Check the parent of the cwd first, then anywhere under the scan root.
3. If none is found, explain that kamma-improve needs the kamma source repo to write to, ask the user for its path (native question tool), and stop if not given.
4. If more than one checkout is found, ask which to use (native question tool).

Call the chosen directory `<KAMMA>`. Every write below happens under `<KAMMA>/`.

---

## 3.0 DISCOVER LESSONS
1. **Scan root:** use `{{args}}` if the user passed a directory; otherwise `$HOME`.
2. **Find lesson files** in a single pass (don't shell-loop): every `*/kamma/lessons.md` under the scan root, excluding `.git`, `node_modules`, and `*/kamma/archive/*` (archived per-thread copies — the live `kamma/lessons.md` is the source of truth). For example:
   ```
   find <root> -type f -path '*/kamma/lessons.md' \
     -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/archive/*'
   ```
3. Locate `<KAMMA>` per Phase 2 from this scan's results before continuing. Then read `<KAMMA>/kamma/improve.md` (the backlog) in full if it exists — you need the Done table, the existing Remaining issues, and the per-source watermarks to dedupe against. If it doesn't exist yet, treat every lesson as new; you'll create it in Phase 6.

---

## 4.0 EXTRACT NEW LESSONS (batched, compaction-safe)
Create a working file `<KAMMA>/kamma/improve-triage-<YYYYMMDD>.md` (use today's date). Process the lesson files in batches of ~15. For each source repo:

- Look up its watermark in `improve.md`'s `## Sources` section: the date through which this source was last processed. Ingest every lesson dated **on or after** that watermark (all lines for a new source). Re-reading the watermark day is deliberate — the dedup in Phase 6 drops anything already recorded, so a lesson appended later on the same day is never lost. (Same-day lessons that were filtered as noise carry no backlog evidence and are simply re-evaluated each run — idempotent and harmless.)
- Append each new line to the working file as: `<repo> <date> [TAG] <text>`.
- `[POSITIVE]` lines go under a `## Working well` heading — they are preserve-signals, not issues.

Never hold extraction results only in context — write them to the working file as you go. If there are no new lessons across all sources, report "no new lessons since last run", show the current top 5 from `improve.md` (Phase 7), and stop.

---

## 5.0 DETECT RECURRENCE & DEDUP AGAINST EXISTING RULES
This phase is the whole point — be rigorous.

1. **Cluster by theme** (not exact text) across repos and dates. A cluster seen in ≥2 repos OR ≥3 times is **systemic**. A single sighting is noise unless it is severe (data loss, a rule violation).
2. **Rank** clusters by frequency × recency: a recent cluster outweighs an older one of equal count. Staleness check: if a cluster targets a framework area that was since rewritten (`git -C <KAMMA> log --oneline` of the relevant file), drop or down-rank it.
3. **Dedup against what already exists — before proposing anything.** For each systemic cluster, grep the kamma prompts (`<KAMMA>/commands/*.md`, `skills/kamma/SKILL.md`, `templates/`) and the global agent file (read-only):
   - **Not present anywhere** → propose adding it to the right framework file.
   - **Already a framework rule but still recurring** → the fix is **escalation, not duplication**: make it unmissable (promote to a bold standalone bullet, add a hard gate or checklist item, move it earlier). Cite the recurrence as the evidence. (This is the lesson that a buried rule keeps getting violated.)
   - **Already only a global agent rule (not in the framework)** → out of scope to write; record it as an agent-rule suggestion in Phase 6.

---

## 6.0 MERGE INTO THE BACKLOG (`<KAMMA>/kamma/improve.md`)
Classify each surviving cluster:
- **FRAMEWORK** (writable) — a kamma process/workflow gap. Name the exact file and the proposed edit.
- **AGENT-SUGGESTION** (not written) — a pure behaviour rule that belongs in an agent file; finalize owns it. Record as a recommendation for the user.
- **NEEDS** — can't be auto-resolved (ambiguous, needs a tool or user judgment).

Merge each cluster into `improve.md`:
1. **Matches a Done item** but a newer lesson re-reports it → **REGRESSION**: move it back to Remaining at High severity, tagged `REGRESSION`.
2. **Matches a Remaining item** → append the new `<repo>@<date>` evidence and bump its count. Skip any `<repo>@<date>` evidence already listed (this is what makes re-reading the watermark day safe).
3. **New** → add under the right severity (High/Medium/Low) with the next free issue number.

Every Remaining issue carries an evidence line `(seen in N: <repo>@<date>, …)` (list at most 5, then `+K more`). Severity guide: High = wrong work reaches the user or a phase can't complete; Medium = recurring friction/wasted effort; Low = cosmetic or rare.

Backlog structure (create sections that don't exist):
- `## Done` — table of resolved issues.
- `## Remaining — prioritized` — High / Medium / Low subsections.
- `## Working well — preserve` — `[POSITIVE]` patterns worth protecting.
- `## Sources` — the watermark, one line per source repo: `<repo>: processed through <date>`. This is how processed vs unprocessed is tracked; source `lessons.md` files are never modified.
- `## Notes for next session`.

---

## 7.0 PRESENT TOP 5 AND PICK
Rank Remaining by severity, then recency-weighted frequency, tie-break toward quick wins. Present a table:

| # | Issue | Target | Severity | Seen | Why now |

Below it, report in one or two lines: sources scanned, new lessons, new issues, regressions. Then ask the user to pick one (native question tool; top 4 as options with "Why now" as the description, the rest reachable via Other).

Work the chosen issue:
- **FRAMEWORK** → apply the fix to the source file under `<KAMMA>/`. Keep the addition minimal; escalate rather than duplicate. Then remind the user to run `just sync` to propagate.
- **AGENT-SUGGESTION / NEEDS** → there is nothing to write in the framework; present the recommendation for the user to act on (or to feed to finalize).

---

## 8.0 CLOSE THE LOOP (automatic — don't wait to be asked)
As soon as the fix is applied, before reporting completion:
1. Move the issue from Remaining to the `## Done` table with the date, the target file, and a one-line summary. If only part was fixed, leave the residue as a new numbered Remaining issue with its original evidence.
2. Advance each processed source's watermark in `## Sources` to the newest lesson date seen for that source.
3. Update `## Notes for next session` if the picture changed.
4. Delete the `improve-triage-*.md` working file.

Never end with the fixed issue still under Remaining. Finish with a ready-to-use commit block (do NOT run git — the user commits):
- **Commit message** — one conventional-commit subject (`feat:`/`fix:`/`docs:` …, ≤72 chars, imperative).
- **Description** — bullets, each ≤72 chars, one clause each.
- **Changed files** — every file created or modified, including `kamma/improve.md`.
