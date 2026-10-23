#!/usr/bin/env python3
"""Append-only interview log for the thoughts-to-doc skill.

The log keeps every message of the interview exactly as it was said. This script
only ever adds entries at the end of the file and numbers them; it never rewrites
an earlier entry.

Commands:
  init    create <dir>/interview-log.md (fails if it already exists, unless --resume)
  append  add one entry; the text is read as UTF-8 from stdin, or from --file,
          and written as given (a UTF-8 BOM is dropped; a final newline is added
          if missing)

Entry kinds (who spoke):
  opening         person       the message that started the skill, if it had text
  mode            person       a message that picks or switches the mode, whole
  question        interviewer  the mode explanation, a question, or a paraphrase
                               put back to check
  suggestion      interviewer  mode B only: options offered to the person
  draft           interviewer  a brief as shown, headed by the checker's verdict
  answer          person       the person's reply
  draft-feedback  person       the person's reaction to a shown brief

Examples:
  python3 log.py init --dir <YYYY-MM-DD>_<topic>
  python3 log.py append --log <YYYY-MM-DD>_<topic>/interview-log.md --kind answer <<'EOF'
  exactly what the person wrote
  EOF
  python3 log.py append --log <YYYY-MM-DD>_<topic>/interview-log.md --kind answer --file entry.txt

Use --file (a UTF-8 text file) where there is no heredoc, e.g. in PowerShell, or
when the text itself contains a line reading EOF.

Exit codes: 0 ok, 1 empty entry or file error, 2 bad arguments (message on stderr).
"""
import argparse
import datetime
import os
import re
import sys

LOG_NAME = "interview-log.md"
KINDS = {
    "opening": "person",
    "mode": "person",
    "question": "interviewer",
    "suggestion": "interviewer",
    "draft": "interviewer",
    "answer": "person",
    "draft-feedback": "person",
}
ENTRY = re.compile(
    r"^### \[(\d+)\] (?:" + "|".join(map(re.escape, KINDS)) + r") · "
    r"(?:person|interviewer) · \d{4}-\d{2}-\d{2} \d{2}:\d{2}$",
    re.M,
)
HEADER = (
    "# Interview log\n\n"
    "Raw record of the interview, verbatim and in order. Entries are only ever added\n"
    "at the end; nothing here is corrected. `brief.md` in this folder is built from it.\n"
)


def fail(message):
    print(f"log.py: {message}", file=sys.stderr)
    sys.exit(1)


def cmd_init(args):
    os.makedirs(args.dir, exist_ok=True)
    path = os.path.join(args.dir, LOG_NAME)
    if os.path.exists(path):
        if not args.resume:
            fail(f"{path} already exists; use --resume to continue it")
        print(path)
        return
    with open(path, "x", encoding="utf-8", newline="") as f:
        f.write(HEADER)
    print(path)


def read_text(args):
    try:
        if args.file:
            with open(args.file, "rb") as f:
                raw = f.read()
        else:
            raw = sys.stdin.buffer.read()
        return raw.decode("utf-8-sig")
    except OSError as e:
        fail(f"cannot read {args.file}: {e.strerror}")
    except UnicodeDecodeError:
        fail("entry text is not valid UTF-8")


def cmd_append(args):
    if not os.path.isfile(args.log):
        fail(f"{args.log} not found; run init first")
    text = read_text(args)
    if not text.strip():
        fail("empty entry: pass the text on stdin or with --file")
    with open(args.log, encoding="utf-8", newline="") as f:
        existing = f.read()
    number = 1
    for m in ENTRY.finditer(existing):
        if int(m.group(1)) == number:
            number += 1
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    who = KINDS[args.kind]
    body = text if text.endswith("\n") else text + "\n"
    entry = f"\n### [{number}] {args.kind} · {who} · {stamp}\n\n{body}"
    with open(args.log, "a", encoding="utf-8", newline="") as f:
        f.write(entry)
    print(number)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create the log in a task folder")
    p_init.add_argument("--dir", required=True, help="task folder, created if missing")
    p_init.add_argument("--resume", action="store_true",
                        help="if the log exists, keep it and print its path")
    p_init.set_defaults(func=cmd_init)

    p_append = sub.add_parser("append", help="append one entry; text from stdin or --file")
    p_append.add_argument("--log", required=True, help="path to interview-log.md")
    p_append.add_argument("--kind", required=True, choices=sorted(KINDS),
                          help="entry kind; see the list above")
    p_append.add_argument("--file", help="read the entry text from this UTF-8 file")
    p_append.set_defaults(func=cmd_append)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
