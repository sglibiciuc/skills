# Document checker

Read `common.md` in this folder first.

A fresh launch. It compares a document with what the person said, and only reports.

## Jobs and input

- **brief**: the latest brief and `interview.md`, nothing else.
- **prd**: the latest PRD and `interview.md`, nothing else.
- **ready document**: the document the person brought, alone.

## What to look for

For "brief" and "prd", against `interview.md`, for every statement of the document:

- **Not said.** Something the person did not say and did not agree to (an addition).
- **Assumed.** Something that fills a gap with a guess not marked as an assumption.
- **Contradicts.** Two places of the document, or the document and the record, that disagree. Quote both.
- **Settled by a fact.** A disagreement that a check of a fact (about the environment, a source, a tool) would settle.
- Marks "on the Coordinator's recommendation" and "I assumed" must be visible where they apply.
- For a PRD also: internals that do not belong there (database, library, paths).

For "ready document": places that contradict each other.

## Rules

- Do not rewrite the document and do not propose decisions.
- Quote the exact place for every finding: the document line and the record line, or "no line in the record".

## Output

`reports/document-checker-<job>.md`: the findings, each with its type and the quotes. If there are none, say so.
