# Common ground for every role

Every role reads this first. It holds the principles, the shared words, the task folder and the rules all roles share. Record formats: `records.md` in this folder.

## Principles

- One quality bar for any task, small or large. The volume grows with the task by itself. The process does not grow to match the task's size.
- Build simple from the start, do not simplify later: DRY, KISS, YAGNI, SOLID, above all single responsibility. No noodle code, no 10,000-line file. If one line can do the work of a hundred, write the one line now. The Coordinator proposes building this way from the start.
- Nothing beyond what was agreed. Do not invent extras and do not attach what nobody asked for. An idea or finding that is not in the PRD goes into your report as a backlog item, it is not built. A bad build means a badly written spec, never the person's fault.

## Words

- **Block**: a finished piece of the spec, from start to result, with its own runnable check.
- **Part**: a group of blocks the person can already use. A part is **built** when all its blocks are done, and **passed** when the result tester's and the simplifier's reports on it exist.
- **Working whole**: everything built so far, with every check of every done block green.
- **Skill folder**: the parent of this `references/` folder. The programs are `<skill folder>/scripts/done.py` and `<skill folder>/scripts/resume.py`, run as `python3 "<skill folder>/scripts/done.py" …`.
- **Coordinator home**: the folder `~/.coordinator/`.

## The person

- The person talks only to the Coordinator. Every other role writes for the Coordinator, not for the person.
- The person's documents and things are never edited. Work happens in copies. The original is only read. A copy becomes the working thing only as the last step, on the person's "yes".
- The person's documents (brief, PRD, plan, instructions, final message) are in the person's language. Role documents, specs, checks and reports may be in English.
- No time estimates anywhere, in days or hours.
- Nothing paid (API, SDK, provider) is added without the person's answer.
- Protections, kill switches, limits and trial modes go into the result only when the person asked for them in the brief.
- A model never grades beauty or content. Beauty is agreed by the person on the mockup, content is judged by the person.

## Shared rules

- **Real sources, safe writes.** Real tools and data sources are used by reading only. Writes and sends during the work go to a copy and to a test recipient, except a step the person said "yes" to: the plan's last step (switching the result on for everyone or replacing the working thing with the copy) or the replacement agreed in the right-away goal check.
- **Skills and plugins.** When the result is a skill or a plugin, build and check it with the environment's standard tools by the current official documentation of Anthropic and OpenAI, read at the time of work. Whether runs "with and without the skill" are needed is decided by those tools and that documentation.
- **Input.** Read every input your role document lists for the job; if the launch message leaves one out, take it from the task folder.
- **What you created.** Append everything you create outside the deliverable (copies, test chats, test records, drafts) to `created.md`.
- **Without programs.** If `python3` does not run here, whoever would run `done.py` runs every check it names by hand and pastes the full output into the report. "Done" then rests on that output, which the Coordinator compares with the checks in `spec.md`.

## The task folder

One project, one task, one task folder. In a browser or on a phone there is no folder: documents and results go to the chat as files, and records live in the conversation.

| Path | What | Who writes |
|---|---|---|
| `interview.md` | The person's words, word for word, as they come | Coordinator |
| `brief-v<N>.md` | "What I want" | Coordinator |
| `prd-v<N>.md`, `prd-v<N>-scheme.html` | "How it works", with one picture of the scheme | Coordinator |
| `research.md` | What exists, how it is done well, known mistakes, checked sources | Researcher |
| `spec.md` | The spec in blocks, each block linked to PRD stories | Composer |
| `checks/` | Runnable checks for blocks and defects | Composer |
| `plan.md` | The full plan, reading it is optional for the person | Coordinator |
| `now.md` | Working file: stage, last step, next step | Coordinator |
| `reports/` | Reports of every role, one file per report | Each role writes its own |
| `copies/` | Copies of the person's things | Researcher |
| `access/` | Accesses the person hands over | The person |
| `created.md` | Everything roles created outside the deliverable | Each role appends its own |
| `backlog.md` | Findings and ideas that do not break requirements. Lives next to the result, or next to the existing thing when the work changed it, not among the task records in `.coordinator/` or `reports/` | Executor |
| `.coordinator/` | Records the programs and hooks read | As named in `records.md` |

- A new version of an agreed document is a new file (`brief-v2.md`). The previous version stays.
- Agents take accesses from `access/` and read the files there as they are. No program filters lines that look like passwords. Agents never clean up `access/`.

## Reports

Every role except the Coordinator ends with a report in the task folder's `reports/` (never in the Coordinator home), named `<role>-<job>.md` unless the role document names it otherwise. In every report file name, spaces in the job become hyphens: `executor-right-away.md`. The report says what was done, what was found, what was changed outside the task folder (an exact list), and what was created. Findings that are not in the PRD stay in the report as backlog items.
