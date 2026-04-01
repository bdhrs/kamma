# Status Command Rename Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename the status command to `5-status` so Kamma commands appear as a consistent numbered flow.

**Architecture:** Rename the source command file, update every documentation and skill reference that mentions the old command name, then republish the installed command artifacts with the updated filename. Keep command content unchanged aside from invocation references.

**Tech Stack:** Markdown command docs, shell copy script

---

### Task 1: Rename the source command

**Files:**
- Create: `commands/5-status.md`
- Modify: `commands/status.md`

**Step 1: Preserve the existing status command content**

Move the current status command content into `commands/5-status.md`.

**Step 2: Remove the old source path**

Delete `commands/status.md` after the new numbered file exists.

### Task 2: Update references

**Files:**
- Modify: `README.md`
- Modify: `skills/kamma/SKILL.md`
- Modify: `commands/0-setup.md`
- Modify: `commands/5-status.md`

**Step 1: Rename user-facing invocation references**

Change `/kamma:status` references to `/kamma:5-status` and update any file-path references from `status.md` to `5-status.md`.

### Task 3: Republish commands

**Files:**
- Modify: `copy.sh`

**Step 1: Re-run install sync**

Run `./copy.sh` after the rename so installed command artifacts use `kamma-5-status`.

### Task 4: Verify installed outputs

**Files:**
- Modify: `commands/5-status.md`

**Step 1: Inspect installed command names**

Confirm the synced destinations contain `5-status` instead of `status`.
