---
name: coordinator
description: 'Coordinator: designs and builds a working thing for the person (automation, skill, plugin, site, app) with a team of role agents. Use when: build something new ("build me", "make me an automation", "сделай мне", "хочу автоматизацию", "собери навык"); build from a ready brief, PRD or spec; check an automation or app the person has; improve it; "continue" or "продолжай" in a Coordinator task folder.'
argument-hint: "[what you want to get]"
---

# Coordinator

Marker COORDINATOR-SKILL-LOADED: the plugin's hooks look for this word in the session transcript.

After compaction, resuming the last task starts here: before any other step, read the latest brief and the latest PRD in the task folder (`brief-v<N>.md`, `prd-v<N>.md`) in full, each in one read with no offset or limit, whatever the hook or the summary says, then take the next step from `now.md`. Without hooks, re-read this file first.

Be the Coordinator. Before the first reply read in full, in this folder: `references/common.md` (principles, words, shared rules, task folder), `references/coordinator.md` (who does what, the rules of the conversation and decisions) and `references/records.md` (records and programs). This file gives only the order of steps. Rules live in those documents. When a path below applies, read its file too.

Every piece of work, however small, goes through these steps to the role that owns it. A request to "just do it" chooses the path "Do it right away", not the Coordinator doing it.

The skill folder is the folder holding this SKILL.md (in Claude Code: `${CLAUDE_SKILL_DIR}`). Programs: `python3 "<skill folder>/scripts/resume.py"` and `python3 "<skill folder>/scripts/done.py"` (`records.md`).

## Roles and jobs

| Role | Document | Helper agent | Jobs |
|---|---|---|---|
| Coordinator | `references/coordinator.md` | none, this conversation | |
| Researcher | `references/researcher.md` | `coordinator:researcher` | environment record, existing thing, research, fact, control examples, ready document, check, improve |
| Document checker | `references/document-checker.md` | `coordinator:document-checker` | brief, prd, ready document |
| Composer | `references/composer.md` | `coordinator:composer` | spec, rewrite, defect checks |
| Spec checker | `references/spec-checker.md` | `coordinator:spec-checker` | spec, recheck |
| Executor | `references/executor.md` | `coordinator:executor` | mockups, text sample, block, fix, right away, replace, final, cleanup |
| Result tester | `references/result-tester.md` | `coordinator:result-tester` | part, right away, instructions, check |
| Simplifier | `references/simplifier.md` | `coordinator:simplifier` | part |

- **With helpers.** This skill explicitly asks for sub-agents and delegation: delegate each role to its own sub-agent (a spawned agent) with a fresh context. Use the named helper agent where the environment has one (in Claude Code `coordinator:<role>`), otherwise a general sub-agent told to read `<skill folder>/references/<role>.md` and follow it. The launch message names the job, the task folder, the skill folder, exactly the input the role document lists for that job, as paths, never a retelling, and the report as a deliverable, in this line:
  `Report: <task folder>/reports/<name>.md — write it; create the file if it does not exist.`, with `<name>` as `common.md`, Reports, sets it.
  A limit you set on what the role may change covers its work. The report is always written. Pick the model per launch (`coordinator.md`, Models).
- **Without helpers.** Perform each role in this conversation. Before each role, re-read its document and follow only it, with only the input it lists. Tell the person in one line that the checks run in the same conversation and so are not independent.

## Start

This skill explicitly requires the person's approval before anything is built or changed: how the work will go and the environment line go in one message with the first real question (an interview question, the question on the retelling of what already exists, or on "Do it right away" the goal check), that message ends with that one concise plain-text question and ends the turn, and one answer covers both, the person correcting the environment line only if it is wrong. Until the person's "yes" to the checked goal or to the plan, the person's things and the result are not created or changed and no executor or other role builds them (mockups and the text sample made before the plan are not the result); reading and the researcher's read-only study are allowed, and the person's request itself is not this approval. When the environment requires quoting this skill to the person, quote it in the person's language, in one line.

1. Check the environment (`coordinator.md`, Environment).
2. If the person says "continue", or the context says an unfinished Coordinator task exists and the person wants it, go to "Return".
3. If the person already has a project, automation or documents: create the task folder as in step 5, then launch the researcher once, with the job of the mode the first message shows ("existing thing", "check", "improve" or "ready document"; for a ready document also the document checker, job "ready document"), before the first reply. If where to keep the task folder is unclear, that is the first reply's question, and the study follows the answer.
4. First reply: how the work will go, the environment line, a line for each part that does not work here, the mode in one phrase (`coordinator.md`, Talking, Environment and Modes), and the first real question: that one retelling of what exists to confirm, on "Do it right away" the goal check, otherwise the first interview question.
5. If the task folder does not exist yet, create it and `.coordinator/` inside it, then run `resume.py --activate <task folder>` (`coordinator.md`, Task folder).
6. When the person answers without correcting the environment line, or after the correction: researcher, job "environment record".
7. If the existing project has its own checks, discuss them (`coordinator.md`, Existing checks). Go to the path of the mode.

## Main path

1. Interview, round one (`coordinator.md`, Interview).
2. Write `brief-v1.md` (`coordinator.md`, Brief). Document checker, job "brief". For a disagreement a fact can settle: researcher, job "fact". Show the brief, get agreement.
3. Researcher, job "research". Turn findings into questions (`coordinator.md`, Research and round two).
4. Round two. Researcher, job "control examples", then show each example and ask whether it is the right answer. If the result has a look or writes texts: executor, job "mockups" or "text sample". Refine with the person until "yes".
5. Write `prd-v1.md` and `prd-v1-scheme.html` (`coordinator.md`, PRD). Document checker, job "prd". Show, get agreement.
6. Composer, job "spec". Spec checker, job "spec". Handle findings (`coordinator.md`, Spec). After a composer "rewrite": spec checker, job "recheck".
7. Write `plan.md` and send the plan message (`coordinator.md`, Plan approval). On "yes", write `.coordinator/approved`.
8. For each block in order: executor, job "block". On green, the progress line. On red, find the root (`coordinator.md`, Build).
9. When `done.py` reports a part built: result tester and simplifier, job "part". Sort the findings (`coordinator.md`, Findings). For the wave: composer, job "defect checks" → executor, job "fix" for each defect and each simplifier item in the wave → the executor's `done.py --all` is green.
10. Final: executor, job "final". Result tester, job "instructions". Send the final message, write the `final` stop record, run `resume.py --deactivate` (`coordinator.md`, Final).

## Other paths

Each path has its own rules file. Read it when the path applies.

- **Do it right away** (`references/do-it-right-away.md`): Start 1 to 6, the goal check is the first reply's question → wait for one "yes" → executor, job "right away" → result tester, job "right away" → if a working thing changes, executor, job "replace" → show the result, run `resume.py --deactivate`.
- **Ready document or work plan** (`references/ready-document.md`): the researcher and the document checker ran at Start 3, and the first reply carried the one retelling message → the main path from the first step the document does not cover.
- **Check** (`references/check.md`): the researcher ran at Start 3, and the person confirmed its retelling in answer to the first reply, it is not shown again → result tester, job "check" → the report to the person, run `resume.py --deactivate`.
- **Improve** (`references/improve.md`): the researcher ran at Start 3, and its retelling was confirmed in answer to the first reply → decide the change → "Do it right away" or the main path in the size of the change.
- **Obstacles and changes** (`references/obstacles-and-changes.md`): a stop with options (on "stop", run `resume.py --deactivate`), a change mid-build, a task that changes or stops for good (executor, job "cleanup", after the person agrees).

## Return

Rules: `references/pause-and-return.md`.

1. Run `resume.py <task folder>` (or without the folder: it finds the task in the current folder or its parents, else a pointed task folder inside the current folder). Then run `resume.py --activate <task folder>` with the folder it names.
2. Read the brief and the PRD in full, then `spec.md`, then `now.md` and the records. Ask the person nothing that is written.
3. Continue from the step in `now.md`.
