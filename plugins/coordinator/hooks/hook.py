#!/usr/bin/env python3
"""Coordinator hooks. They only check that a record exists, the rules themselves live in the role documents.
Record formats: skills/coordinator/references/records.md.

Usage (from hooks.json): python3 hook.py session-start | prompt | stop   (hook JSON on stdin)

session-start  Says that hooks are active. On a new session with an active task pointer, says that an
               unfinished Coordinator task exists and how to continue. After compaction or resume in a
               Coordinator session, returns the role and the working file (the output of resume.py).
prompt         In a Coordinator session, when the person answers, moves the open stop record
               (human or pause) to stops.log.
stop           In a Coordinator session after the plan is approved, the turn ends only with a stop record
               (human, pause, or final with every block done and both reports for every part, newer than approved).
               There is no loop guard here on purpose: the hook keeps the turn going until the record
               exists. Claude Code itself ends the turn after 8 consecutive stop-hook continuations
               without a tool call (CLAUDE_CODE_STOP_HOOK_BLOCK_CAP), which is the loop protection.
               Codex 0.154 has no such cap: there the person stops the loop by interrupting the turn.
Codex runs this same hooks.json as a plugin hook, with the same payload fields and output shapes.
A Coordinator session is one whose transcript holds the skill's marker word.
Any error lets Claude Code go on as usual: the text of the instructions still holds.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "skills", "coordinator", "scripts"))
import resume  # noqa: E402
import state  # noqa: E402

MARKER = "COORDINATOR-SKILL-" + "LOADED"  # split so this file never matches itself


def coordinator_session(data):
    path = data.get("transcript_path") or ""
    try:
        with open(os.path.expanduser(path), encoding="utf-8", errors="ignore") as f:
            return MARKER in f.read()
    except OSError:
        return False


def task_of(data):
    return state.find_task(data.get("cwd") or os.getcwd())


def session_start(data):
    lines = ["Coordinator plugin: hooks are active in this session."]
    active = state.active_task()
    if data.get("source") == "startup" and active:
        lines.append("There is an unfinished Coordinator task in %s. If the person says \"continue\" (or the same in "
                     "their language), load the coordinator skill and follow its Return steps (resume.py)." % active)
    if data.get("source") in ("compact", "resume") and coordinator_session(data):
        task = task_of(data)
        if task:
            lines.append(resume.summary(task))
            lines.append("Rules for the return: skills/coordinator/references/pause-and-return.md.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": "\n".join(lines)}}))


def prompt(data):
    if not coordinator_session(data):
        return
    task = task_of(data)
    if task:
        state.archive_stop(task)


def stop(data):
    if not coordinator_session(data):
        return
    task = task_of(data)
    if not task or not state.plan_approved(task):
        return
    record = state.read_stop(task)
    where = state.rec(task, "stop")
    if record is None or record[0] not in state.STOP_KINDS:
        reason = ("Plan approved, no valid stop record in %s. Rule: coordinator.md, Build. "
                  "Record format: records.md, stop." % where)
    elif record[0] == "final" and state.final_gaps(task):
        reason = ("Stop record in %s is final, missing: %s. Rule: coordinator.md, Findings and Final."
                  % (where, "; ".join(state.final_gaps(task))))
    else:
        return
    print(json.dumps({"decision": "block", "reason": reason}))


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        data = {}
    try:
        {"session-start": session_start, "prompt": prompt, "stop": stop}[sys.argv[1]](data)
    except Exception as e:  # never break the session: the text rules still apply
        print("coordinator hook skipped: %s" % e, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
