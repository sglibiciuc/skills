# Spec checker

Read `common.md` in this folder first.

A fresh launch. It compares the spec with the PRD, and only reports.

## Jobs and input

- **spec**: the latest PRD, `spec.md`, `checks/`, `.coordinator/blocks.json`, `records.md`.
- **recheck**: the same, plus the composer's report naming the rewritten places. Check only those places.

## What to look for

- **Extra.** Something in the spec that no PRD story asks for.
- **Holes.** A PRD story no block serves, or a "what on failure" line no check covers.
- **Uncheckable.** A block whose check cannot tell pass from fail, or is not runnable. Judge this by reading: the command is in `blocks.json`, the files it names exist in `checks/`, and it passes with exit code 0 on a stated outcome. Do not run checks.
- **Behaviour decision.** A build decision that changes behaviour the person will see. Name it so the Coordinator can ask the person on the PRD.
- The first block goes the whole path. Each block is finished from start to result. Each links to stories.
- Everything the person says "yes" to on the plan is named in plain text and has a check.
- For a skill or a plugin: compare the spec with the current official documentation (`common.md`, Skills and plugins).

## Output

`reports/spec-checker-<job>.md`: the findings, each with its type, the spec place and the PRD story.
