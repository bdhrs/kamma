# Issue Number Propagation Design

## Goal

Make GitHub issue handling unambiguous across Kamma so agents reliably carry an issue number from thread creation to final issue comment, issue closure, and commit message suggestion.

## Decision

When a thread is tied to a GitHub issue, the issue number must appear in all of these places:

- the thread description/title
- the `kamma/threads.md` entry
- the thread `spec.md`
- the thread `plan.md`

## Why

Redundant visibility is intentional here. The issue number needs to remain obvious throughout the workflow so agents do not debate whether issue updates or issue-linked commit messages are required.

## Expected Behavior

- Planning must ask for or preserve the issue number.
- Thread creation must store the issue number prominently in the thread artifacts.
- Workflow guidance must say that finalize uses the preserved issue number to comment on and close the issue.
- Commit message guidance must explicitly reference the issue number when one exists.
