"""Read the records of a Coordinator task folder. Shared by done.py, resume.py and the hooks.

The record formats are described in references/records.md.
"""
import datetime
import json
import os
import re

STOP_KINDS = ("human", "pause", "final")


class RecordError(Exception):
    """A record exists but is malformed. The message says what to fix."""


def home():
    return os.path.expanduser("~/.coordinator")


def is_task(path):
    return bool(path) and os.path.isdir(os.path.join(path, ".coordinator"))


def active_task():
    try:
        with open(os.path.join(home(), "active"), encoding="utf-8") as f:
            path = f.read().strip()
    except OSError:
        return None
    return path if is_task(path) else None


def find_task(start):
    """A task folder at start or one of its parents, else the pointer's task if it lies inside start, else None."""
    start = probe = os.path.abspath(start)
    while True:
        if is_task(probe):
            return probe
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent
    task = active_task()
    if task:
        real_start = os.path.realpath(start)
        if os.path.commonpath([real_start, os.path.realpath(task)]) == real_start:
            return task
    return None


def rec(task, name):
    return os.path.join(task, ".coordinator", name)


def load_parts(task):
    """[(part_id, [block, ...])], block = {"id", "checks": [command, ...]}. Empty if there is no blocks.json."""
    path = rec(task, "blocks.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        parts = [(str(p["id"]), [{"id": str(b["id"]), "checks": b["checks"]} for b in p["blocks"]])
                 for p in data["parts"]]
        for _, blocks in parts:
            for b in blocks:
                if not isinstance(b["checks"], list) or not all(isinstance(c, str) and c.strip() for c in b["checks"]):
                    raise TypeError("block %s: checks must be a list of command strings" % b["id"])
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        raise RecordError("%s does not match the format in references/records.md (%s: %s)"
                          % (path, type(e).__name__, e))
    seen_parts, seen_blocks = set(), set()
    for pid, blocks in parts:
        if pid in seen_parts:
            raise RecordError("%s: part id %s is used twice" % (path, pid))
        seen_parts.add(pid)
        for b in blocks:
            if b["id"] in seen_blocks:
                raise RecordError("%s: block id %s is used twice, block ids must be unique in the whole file"
                                  % (path, b["id"]))
            seen_blocks.add(b["id"])
    return parts


def done_blocks(task):
    path = rec(task, "done.jsonl")
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {json.loads(line)["block"] for line in f if line.strip()}


def report_paths(task, part_id):
    return [os.path.join(task, "reports", "part-%s-%s.md" % (part_id, who)) for who in ("tester", "simplifier")]


def missing_reports(task, part_id):
    return [p for p in report_paths(task, part_id) if not os.path.exists(p)]


def stale_final(task):
    """A final record older than approved belongs to earlier work: a new improvement cancels it."""
    stop, approved = rec(task, "stop"), rec(task, "approved")
    return os.path.exists(approved) and os.path.getmtime(stop) < os.path.getmtime(approved)


def read_stop(task):
    """(kind, text) of the current stop record, or None. A stale final counts as no record."""
    path = rec(task, "stop")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        lines = f.read().strip().splitlines() or [""]
    kind = lines[0].strip().lower()
    if kind == "final" and stale_final(task):
        return None
    return kind, " ".join(lines[1:]).strip()


def archive_stop(task):
    """Move an open human or pause record, or a stale final, to stops.log. A current final stays."""
    path = rec(task, "stop")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        lines = f.read().strip().splitlines() or [""]
    stop = (lines[0].strip().lower(), " ".join(lines[1:]).strip())
    if stop[0] == "final" and not stale_final(task):
        return
    with open(rec(task, "stops.log"), "a", encoding="utf-8") as f:
        f.write("%s\t%s\t%s\n" % (datetime.datetime.now().isoformat(timespec="seconds"), stop[0], stop[1]))
    os.remove(rec(task, "stop"))


def plan_approved(task):
    return os.path.exists(rec(task, "approved"))


def latest(task, stem):
    """Latest version of a document: <stem>-v<N>.md with the highest N, else <stem>.md, else None."""
    best, best_n = None, -1
    for name in os.listdir(task):
        m = re.fullmatch(re.escape(stem) + r"-v(\d+)\.md", name)
        if m and int(m.group(1)) > best_n:
            best, best_n = name, int(m.group(1))
    if best is None and os.path.exists(os.path.join(task, stem + ".md")):
        best = stem + ".md"
    return best


def final_gaps(task):
    """What keeps the work from a final: blocks not done, parts without both reports."""
    gaps, done = [], done_blocks(task)
    for part_id, blocks in load_parts(task):
        for b in blocks:
            if b["id"] not in done:
                gaps.append("block %s is not marked done" % b["id"])
        for p in missing_reports(task, part_id):
            gaps.append("report missing: %s" % os.path.relpath(p, task))
    return gaps
