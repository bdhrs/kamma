# Project Workflow

## Guiding Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
2. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` *before* implementation
3. **Write Tests:** Write tests for new functionality where appropriate
4. **Non-Interactive & CI-Aware:** Prefer non-interactive commands
5. **Independent Review Before Completion:** Implementation is not complete until it has been independently reviewed

## Task Workflow

All tasks follow a strict lifecycle:

### Standard Task Workflow

1. **Select Task:** Choose the next available task from `plan.md` in sequential order

2. **Mark In Progress:** Edit `plan.md` and change the task from `[ ]` to `[~]`

3. **Implement:** Write the code to complete the task. Follow the project's coding standards and conventions.

4. **Test:** Run relevant tests to verify the implementation works correctly.

5. **Prepare for Independent Review:**
   - Stop when the work is locally implemented and verified.
   - Instruct the user to run `/kamma:3-review`.
   - Recommend using a different agent or tool than the implementation agent when possible.

6. **Implement Accepted Review Findings:**
   - Apply valid findings from `/kamma:3-review`.
   - Re-run relevant tests and verification.
   - Repeat review if needed until blocking issues are resolved.

7. **Finalize the Thread:**
   - After review is clear, run `/kamma:4-finalize`.
   - Mark the thread complete, sync project docs, and handle archive/delete/skip cleanup there.

8. **Document Deviations:** If implementation differs from tech stack:
   - **STOP** implementation
   - Update `tech-stack.md` with new design
   - Add dated note explaining the change
   - Resume implementation

9. **Commit Code Changes:**
   - Stage all code changes related to the task.
   - Propose a clear, concise commit message.
   - Perform the commit.

10. **Update Plan:**
   - Update `plan.md`: change the task from `[~]` to `[x]`.
   - Commit the plan update.

### Phase Completion Verification

**Trigger:** Executed when a task completes a phase in `plan.md`.

1.  **Announce:** Inform the user that the phase is complete.

2.  **Run Tests:** Execute the project's test suite for the affected area.
    -   If tests fail, inform the user and attempt to fix (max 2 attempts). If still failing, stop and ask for guidance.

3.  **Manual Verification:** Propose step-by-step manual verification steps to the user.

4.  **Await Confirmation:** Ask the user: "Does this meet your expectations? Please confirm or provide feedback."

5.  **Create Checkpoint:** Commit with message like `kamma(checkpoint): End of Phase X`.

6.  **Update Plan:** Record the checkpoint in `plan.md`.

### Quality Gates

Before marking any task complete, verify:

- [ ] Implementation works correctly
- [ ] Relevant tests pass
- [ ] Independent review has been completed
- [ ] Accepted review findings have been implemented
- [ ] Finalization has been completed
- [ ] Code follows project's style guidelines
- [ ] No linting errors
- [ ] Documentation updated if needed

## Commit Guidelines

Follow the project's commit conventions. If none defined, use:

```
<type>(<scope>): <description>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Maintenance tasks

## Definition of Done

A task is complete when:

1. All code implemented to specification
2. Relevant tests passing
3. Independent review completed and accepted findings addressed
4. Finalization completed
5. Code passes linting
6. Changes committed with proper message
7. `plan.md` updated
