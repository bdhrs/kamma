**Before opening this PR** — this repo *is* the framework: `commands/` are prompts read by AI agents, not app code. A quick patch to one symptom can silently contradict the workflow described elsewhere. Please confirm:

- [ ] I (or my agent) read `skills/kamma/SKILL.md` and the relevant file(s) in `commands/` end to end, not just the section that looked related.
- [ ] I checked whether this is a symptom of a mistake made *elsewhere* (a step skipped, a path used that the docs never specify) rather than a gap in the file being patched.
- [ ] I considered at least one alternative fix and say below why this one was chosen over it.
- [ ] There is an open issue describing the problem this PR fixes (link it below), unless this is a trivial typo/formatting fix.

## Issue

Fixes #

## Problem

What's actually going wrong, and where you confirmed the root cause lives.

## Alternatives considered

What else could fix this, and why you didn't do that instead.

## Fix

What this PR changes.

## Verified

How you confirmed the fix works and didn't break the documented workflow (section numbering, cross-references, sibling commands like `kamma.md`/`quick.md` that mirror this logic).
