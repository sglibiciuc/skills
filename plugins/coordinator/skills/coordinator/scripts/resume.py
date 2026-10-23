#!/usr/bin/env python3
"""Return to work: print who to be, what to read and where the work stopped.

Usage: python3 resume.py [task-folder]        summary; an open human or pause record moves to stops.log
       python3 resume.py --activate <folder>  point the Coordinator home at this task folder
       python3 resume.py --deactivate         clear the pointer (when the task ends: final, right-away result,
                                              check report, full stop)
       python3 resume.py --check              print "programs run" (the environment check)
Without a folder, the task is found in the current folder or its parents, else through the pointer if it
points inside the current folder.
Record formats: references/records.md.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state  # noqa: E402


def summary(task):
    lines = ["Coordinator: return to work.", "Task folder: %s" % task,
             "Role: you are the Coordinator. If the coordinator skill is not loaded in this session, load it first "
             "(skill coordinator:coordinator, or read SKILL.md next to this scripts folder)."]
    order = ["%s (in full)" % d for d in (state.latest(task, "brief"), state.latest(task, "prd")) if d]
    if os.path.exists(os.path.join(task, "spec.md")):
        order.append("spec.md")
    order.append("now.md (working file: the next step)")
    lines.append("Read in this order before anything else: " + ", then ".join(order) + ".")
    lines.append("Plan approved: %s." % ("yes" if state.plan_approved(task) else "no"))
    try:
        parts = state.load_parts(task)
    except state.RecordError as e:
        parts = []
        lines.append("Blocks: %s" % e)
    ids = [b["id"] for _, blocks in parts for b in blocks]
    if ids:
        done = state.done_blocks(task)
        count = sum(1 for i in ids if i in done)
        nxt = next((i for i in ids if i not in done), None)
        lines.append("Blocks done: %d of %d (%d%%). Next block: %s."
                     % (count, len(ids), round(100 * count / len(ids)), nxt or "none, all done"))
        for pid, blocks in parts:
            missing = state.missing_reports(task, pid)
            if blocks and all(b["id"] in done for b in blocks) and missing:
                lines.append("Part %s is built but not passed: reports missing: %s."
                             % (pid, ", ".join(os.path.relpath(p, task) for p in missing)))
    stop = state.read_stop(task)
    if stop:
        lines.append("Open stop record: %s. %s" % stop)
    return "\n".join(lines)


def main(argv):
    arg = argv[1] if len(argv) > 1 else None
    if arg == "--check":
        print("programs run")
        return 0
    if arg == "--deactivate":
        pointer = os.path.join(state.home(), "active")
        if os.path.exists(pointer):
            os.remove(pointer)
        print("No active task.")
        return 0
    if arg == "--activate":
        task = os.path.abspath(argv[2]) if len(argv) > 2 else ""
        if not state.is_task(task):
            print("REFUSED: %s has no .coordinator/ folder" % task)
            return 1
        os.makedirs(state.home(), exist_ok=True)
        with open(os.path.join(state.home(), "active"), "w", encoding="utf-8") as f:
            f.write(task + "\n")
        print("Active task: %s" % task)
        return 0
    task = os.path.abspath(arg) if arg else state.find_task(os.getcwd())
    if not state.is_task(task):
        print("No Coordinator task folder found from %s. Ask the person where the task folder is." % os.getcwd())
        return 1
    state.archive_stop(task)
    print(summary(task))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
