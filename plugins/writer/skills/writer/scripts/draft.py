#!/usr/bin/env python3
"""Private revision-bound drafts. Standard library only; no model/API calls.

source/put stage text for the PostToolUse hook. --standalone runs the same
analysis in hosts without lifecycle hooks. accept checks the current revision
and decisions for remaining findings before returning the text for delivery.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
import slop_scan
import _text

MARKER = "WRITER_DRAFT:"
MAX_BYTES = 4 * 1024 * 1024


class DraftError(Exception):
    pass


def root():
    base = Path(os.environ.get("WRITER_DRAFT_ROOT", str(Path(tempfile.gettempdir()) / "writer-drafts")))
    if base.is_symlink():
        raise DraftError("draft root is a symlink")
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    if base.stat().st_uid != os.getuid():
        raise DraftError("draft root belongs to another user")
    base.chmod(0o700)
    return base.resolve()


def directory(ident):
    if not re.fullmatch(r"[a-f0-9]{32}", ident or ""):
        raise DraftError("invalid draft id")
    path = root() / ident
    if path.is_symlink() or not path.is_dir():
        raise DraftError("draft directory missing or unsafe")
    return path


def read(path):
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
        raise DraftError("draft file missing or unsafe")
    if path.stat().st_size > MAX_BYTES:
        raise DraftError("draft exceeds 4 MiB")
    return path.read_text(encoding="utf-8")


def load(path):
    return json.loads(read(path))


def write(path, content):
    if path.is_symlink():
        raise DraftError("refusing a symlink")
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex)
    with tmp.open("x", encoding="utf-8") as stream:
        os.chmod(tmp, 0o600)
        stream.write(content)
    tmp.replace(path)


def save(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def state(ident, cwd=None):
    path = directory(ident)
    meta = load(path / "state.json")
    if meta["cwd"] != str(Path(cwd or os.getcwd()).resolve()):
        raise DraftError("draft belongs to a different working folder")
    return path, meta


def revision(path, meta):
    data = {"kind": meta["kind"], "text": read(path / "text.txt"),
            "max_chars": meta.get("max_chars"), "max_words": meta.get("max_words")}
    if (path / "source.txt").exists():
        data["source"] = read(path / "source.txt")
    return digest(json.dumps(data, ensure_ascii=False, sort_keys=True))


def finding_key(finding):
    return "%s:%s:%s" % (finding["line"], finding["column"], finding["id"])


def analyze(ident, cwd=None):
    path, meta = state(ident, cwd)
    rev = revision(path, meta)
    report_path = path / "analysis.json"
    if report_path.exists():
        old = load(report_path)
        if old["revision"] == rev:
            return old
    text = read(path / "text.txt")
    scan = slop_scan.scan(text)
    result = {"id": ident, "kind": meta["kind"], "revision": rev,
              "text_sha256": digest(text), "slop": scan,
              "finding_keys": [finding_key(f) for f in scan["findings"]]}
    if meta["kind"] == "draft" and (path / "source.txt").exists():
        result["source_sha256"] = digest(read(path / "source.txt"))
    limits = []
    for name, count in (("max_chars", len(text)), ("max_words", len(_text.words(text)))):
        bound = meta.get(name)
        if bound is not None and count > bound:
            limits.append({"limit": name, "maximum": bound, "actual": count})
    result["exceeded_limits"] = limits
    if revision(path, load(path / "state.json")) != rev:
        raise DraftError("draft changed during analysis; analyze the new revision")
    save(report_path, result)
    return result


def stage(text, ident=None, source=None, kind="draft", max_chars=None, max_words=None, owner=None):
    if not text.strip() or len(text.encode("utf-8")) > MAX_BYTES:
        raise DraftError("provide nonempty UTF-8 text up to 4 MiB")
    owner = owner or os.environ.get("WRITER_SESSION_ID")
    if not owner:
        raise DraftError("provide --session from Writer's startup message, or --standalone")
    owner_hash = "standalone" if owner == "standalone" else digest(owner)
    if any(value is not None and value < 0 for value in (max_chars, max_words)):
        raise DraftError("length limits must be nonnegative")
    if ident:
        path, meta = state(ident)
        if meta.get("owner") != owner_hash:
            raise DraftError("draft belongs to a different session")
        if kind == "source":
            raise DraftError("start a new source draft instead of replacing it")
        if meta["kind"] == "source":
            report = load(path / "analysis.json")
            if report["revision"] != revision(path, meta):
                raise DraftError("source analysis is missing or stale")
            write(path / "source.txt", read(path / "text.txt"))
    else:
        ident = uuid.uuid4().hex
        path = root() / ident
        path.mkdir(mode=0o700)
        meta = {"cwd": str(Path.cwd().resolve()),
                "owner": owner_hash}
    if source is not None:
        write(path / "source.txt", source)
    for name, value in (("max_chars", max_chars), ("max_words", max_words)):
        if value is not None and value < 0:
            raise DraftError("length limits must be nonnegative")
        if value is not None or name not in meta:
            meta[name] = value
    meta["kind"] = kind
    write(path / "text.txt", text)
    save(path / "state.json", meta)
    return {"id": ident, "marker": MARKER + ident,
            "path": str(path / "text.txt"), "revision": revision(path, meta),
            "status": "awaiting_analysis"}


def accept(ident, rev, decisions):
    path, meta = state(ident)
    if meta["kind"] != "draft":
        raise DraftError("a source is not a finished draft")
    report = load(path / "analysis.json")
    if rev != revision(path, meta) or rev != report["revision"]:
        raise DraftError("analysis belongs to another revision")
    if report["exceeded_limits"]:
        raise DraftError("the person's length limit is exceeded")
    keys = set(report["finding_keys"])
    if not isinstance(decisions, dict) or set(decisions) != keys:
        raise DraftError("provide a keep reason for each remaining finding_key, or revise the draft")
    if any(not isinstance(reason, str) or not reason.strip() for reason in decisions.values()):
        raise DraftError("each keep reason must be nonempty")
    save(path / "accepted.json", {"revision": rev, "decisions": decisions})
    return read(path / "text.txt")


def accepted(ident, cwd=None):
    path, meta = state(ident, cwd)
    receipt = load(path / "accepted.json")
    if receipt["revision"] != revision(path, meta):
        raise DraftError("accepted revision is stale")
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("source", "put"):
        p = sub.add_parser(name)
        p.add_argument("--text", default="-", help="UTF-8 file or - for stdin")
        p.add_argument("--standalone", action="store_true", help="analyze here when host has no lifecycle hooks")
        p.add_argument("--session", help="session id from the Writer startup hook")
        if name == "put":
            p.add_argument("--id")
            p.add_argument("--source", help="source material file, optional")
            p.add_argument("--max-chars", type=int)
            p.add_argument("--max-words", type=int)
    p = sub.add_parser("accept")
    p.add_argument("id")
    p.add_argument("--revision", required=True)
    p.add_argument("--decisions", default="{}", help="JSON object or - for stdin")
    p = sub.add_parser("analyze")
    p.add_argument("id")
    args = ap.parse_args()
    try:
        if args.command in ("source", "put"):
            result = stage(_text.read_input(args.text), getattr(args, "id", None),
                           _text.read_input(args.source) if getattr(args, "source", None) else None,
                           "source" if args.command == "source" else "draft",
                           getattr(args, "max_chars", None), getattr(args, "max_words", None),
                           "standalone" if args.standalone else args.session)
            if args.standalone:
                result["analysis"] = analyze(result["id"])
            print(json.dumps(result, ensure_ascii=False))
        elif args.command == "analyze":
            print(json.dumps(analyze(args.id), ensure_ascii=False))
        else:
            decisions = json.loads(sys.stdin.read() if args.decisions == "-" else args.decisions)
            print(accept(args.id, args.revision, decisions), end="")
        return 0
    except (DraftError, _text.BadInput, OSError, ValueError, KeyError) as error:
        print("Writer draft not ready: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
