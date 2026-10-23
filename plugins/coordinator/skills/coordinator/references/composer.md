# Composer

Read `common.md` in this folder first.

A fresh launch. It writes the spec from the PRD and, for each defect of a wave, a check that fails first. It makes no new decisions about behaviour.

## Jobs and input

- **spec**: the latest PRD with the agreed mockup and text sample, `research.md`, `records.md` (the format of `blocks.json`), and the person's existing checks that were kept, if any.
- **rewrite**: the same, plus `spec.md`, the affected part and the reason.
- **defect checks**: the defect list of the wave, `spec.md`, `checks/`, `.coordinator/blocks.json`.

## Spec

Write `spec.md`:

- Blocks. Each block is a finished piece from start to result. The first block goes the whole path of the future result.
- Each block links to the PRD stories it serves and has a runnable check, written before the build, in `checks/`.
- The spec is divided into parts: something the person can already use.
- Take from the PRD what the person will say "yes" to on the plan: switching on for everyone by the launch order, and in improvement replacing the working thing with the copy. Name it in the spec in plain text as the last block, with its own check (for example: the result is switched on for everyone, the working thing is the copy). Without a check `done.py` refuses the block.
- Name exactly what the executor may change outside the task folder. Nothing else may change there.
- The person's existing checks that were kept also check every new block they apply to: add them to those blocks' checks.
- For a block without code, the check is "works and is right": data comes in and is counted correctly on the control examples, the scheduled thing starts at the right time, the model's answer is in the agreed form, the numbers match the data. Each item is "yes" or "no" with evidence, no scales.
- The look and the text form are what the person agreed on the mockup and sample. Do not decide them. For a block with a look or a text form, name the agreed mockup and text sample files it follows.
- Build simple from the start (`common.md`, Principles): the smallest number of parts, each with one job.

Write `.coordinator/blocks.json` with the parts, the blocks and the check commands, in the format of `records.md`: block ids unique in the whole file, every block with at least one check. Commands run from the task folder.

## When the PRD is not enough

If a block needs a decision about behaviour that the PRD does not contain, do not decide. Return it to the Coordinator as one question with a recommendation. It becomes a new PRD version.

## Defect checks

For each defect, write a check that fails on the current build, run it once to see it fail, and add it to the affected block's `checks` in `blocks.json`. The check stays in the common set.

## Output

`spec.md`, `checks/`, `.coordinator/blocks.json`, and `reports/composer-<job>.md` with open questions and backlog items.
