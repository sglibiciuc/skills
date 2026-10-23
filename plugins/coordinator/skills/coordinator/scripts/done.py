#!/usr/bin/env python3
"""Mark a block done only after a green run of its checks and the checks of every earlier block.

Usage: python3 done.py <task-folder> <block-id>   run and, on green, mark the block done
       python3 done.py <task-folder> --all        run the checks of every done block, write nothing

Refuses (exit 1, nothing written) when:
  - an earlier block is not marked done (one block at a time, on a working whole);
  - an earlier finished part lacks the result tester's or the simplifier's report;
  - any check exits non-zero.
Record formats: references/records.md.
"""
import datetime
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state  # noqa: E402

TIMEOUT = 900


def run_checks(task, blocks):
    """Run every check of the given blocks from the task folder. Returns (green, results)."""
    results, green = [], True
    for b in blocks:
        if not b["checks"]:
            print("FAIL  [block %s]  no check command in blocks.json" % b["id"])
            green = False
            continue
        for cmd in b["checks"]:
            # Check commands are written by the composer for this task folder and run as shell commands on purpose.
            try:
                run = subprocess.run(cmd, shell=True, cwd=task, capture_output=True, text=True, timeout=TIMEOUT)
                code, out = run.returncode, run.stdout + run.stderr
            except subprocess.TimeoutExpired:
                code, out = -1, "timed out after %d s (done.py time limit)" % TIMEOUT
            results.append({"block": b["id"], "check": cmd, "exit": code})
            print("%s  [block %s]  %s" % ("PASS" if code == 0 else "FAIL", b["id"], cmd))
            if code != 0:
                green = False
                print("\n".join("    " + line for line in out.strip().splitlines()[-30:]))
    return green, results


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip())
        return 2
    task, block_id = os.path.abspath(argv[1]), argv[2]
    try:
        parts = state.load_parts(task)
    except state.RecordError as e:
        print("REFUSED: %s" % e)
        return 1
    order = [(pid, b) for pid, blocks in parts for b in blocks]
    if not order:
        print("REFUSED: no blocks in %s" % state.rec(task, "blocks.json"))
        return 1
    done = state.done_blocks(task)

    if block_id == "--all":
        targets = [b for _, b in order if b["id"] in done]
        green, _ = run_checks(task, targets)
        print("%s: checks of %d done blocks. Nothing written." % ("GREEN" if green else "RED", len(targets)))
        return 0 if green else 1

    ids = [b["id"] for _, b in order]
    if block_id not in ids:
        print("REFUSED: block %s is not in .coordinator/blocks.json" % block_id)
        return 1
    idx = ids.index(block_id)
    part_id = order[idx][0]
    not_done = [i for i in ids[:idx] if i not in done]
    if not_done:
        print("REFUSED: earlier blocks are not done: %s" % ", ".join(not_done))
        return 1
    for pid, _ in parts:
        if pid == part_id:
            break
        missing = state.missing_reports(task, pid)
        if missing:
            print("REFUSED: part %s is built but not passed, reports missing: %s (coordinator.md, Findings)."
                  % (pid, ", ".join(os.path.relpath(p, task) for p in missing)))
            return 1

    green, results = run_checks(task, [b for _, b in order[: idx + 1]])
    if not green:
        print("RED: block %s is not marked done, a check failed (executor.md, Block)." % block_id)
        return 1

    with open(state.rec(task, "done.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"block": block_id, "time": datetime.datetime.now().isoformat(timespec="seconds"),
                            "checks": results}, ensure_ascii=False) + "\n")
    done = state.done_blocks(task)
    count = sum(1 for i in ids if i in done)
    print("GREEN: block %s marked done. Done %d of %d (%d%%)." % (block_id, count, len(ids), round(100 * count / len(ids))))
    part_blocks = [b["id"] for pid, blocks in parts if pid == part_id for b in blocks]
    if all(i in done for i in part_blocks):
        print("Part %s is built. Reports it needs: %s (coordinator.md, Findings)."
              % (part_id, ", ".join(os.path.relpath(p, task) for p in state.report_paths(task, part_id))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
