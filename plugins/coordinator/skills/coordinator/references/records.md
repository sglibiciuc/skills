# Records

The records the programs and hooks read. Programs and hooks check only that records exist. The rules behind the records are written as text in the role documents. Without hooks or programs, follow them by text.

Paths to the programs: `common.md`, Words (skill folder).

## Coordinator home

The folder `~/.coordinator/`.

- `environment.md`: what is known about the person's environment (subscription, available models, surfaces, what does not work). Written by the researcher after the person confirms.
- `active`: the path of the active task folder, one line. Written by `resume.py --activate <task folder>` when the Coordinator creates or returns to a task folder. Cleared by `resume.py --deactivate` when the task ends: after the final, after "Do it right away" shows the result, after the "Check" report, and on "stop". A pause keeps it. Hooks and `resume.py` find the task through `.coordinator/` in the current folder or its parents first, and through the pointer only when there is none and the pointer's task folder lies inside the current folder (a task folder below the folder the session runs in). While it points at an unfinished task, a new session starts with a line saying so.

## In the task folder, `.coordinator/`

| File | Written by | Content |
|---|---|---|
| `blocks.json` | Composer | Parts, blocks and their check commands (format below) |
| `approved` | Coordinator | One line: the person's words of "yes" to the plan. A new `approved` (a new improvement in the same folder) cancels an older `final` record |
| `stop` | Coordinator | Why the turn ends after the plan is approved (format below) |
| `stops.log` | Hook, `resume.py` | Earlier stop records, moved there when the person answers or the work resumes |
| `done.jsonl` | `done.py` only | One line per green run of a block |

### `blocks.json`

```json
{"parts": [
  {"id": "1", "blocks": [
    {"id": "1.1", "checks": ["bash checks/1.1.sh"]},
    {"id": "1.2", "checks": ["python3 checks/test_1_2.py"]}
  ]},
  {"id": "2", "blocks": [
    {"id": "2.1", "checks": ["bash checks/2.1.sh"]}
  ]}
]}
```

- Block ids are unique across the whole file. Part ids are unique too.
- Every block has at least one check command. Commands run from the task folder. A check passes with exit code 0.
- Defect checks are added to the `checks` list of the affected block and stay there.

### `stop`

Two lines. First line exactly one of:

- `human`: a stop for the person's decision, access or answer;
- `pause`: the person asked to pause;
- `final`: the final message was sent. Accepted only when every block is done and every part has both reports, and only if it is newer than `approved`.

Second line: one sentence why.

## Reports that pass a part

`reports/part-<part id>-tester.md` and `reports/part-<part id>-simplifier.md`. The files must exist. Findings in them do not block.

## Programs

- `python3 "<skill folder>/scripts/done.py" <task folder> <block id>`: runs the checks of this block and of every earlier block. Writes "done" only when all are green. Refuses while an earlier block is not done or an earlier finished part lacks either report.
- `python3 "<skill folder>/scripts/done.py" <task folder> --all`: runs the checks of every block marked done and writes nothing. Used after a wave of fixes.
- `python3 "<skill folder>/scripts/resume.py" [task folder]`: who to be, what to read, where the work stopped. Moves an open `human` or `pause` record to `stops.log`, since the work is resuming.
- `python3 "<skill folder>/scripts/resume.py" --check`: prints `programs run`.
- `resume.py --activate <task folder>`, `--deactivate`: the pointer, above.
