#!/usr/bin/env python3
"""Find the next free version path next to a file, and optionally write it.

  text.md      -> text.v2.md (or v3, v4... if those exist)
  text.v2.md   -> text.v3.md

Never touches the original and never overwrites an existing file.

Usage:
  save_version.py PATH [--content FILE|-] [--format json|text]

Exit 0 on success; 2 on bad input (missing original, unreadable content).
"""

import argparse
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _text  # noqa: E402

VER = re.compile(r"^(?P<stem>.+?)\.v(?P<n>\d+)$")


def split(path):
    d, name = os.path.split(os.path.abspath(path))
    stem, ext = os.path.splitext(name)
    m = VER.match(stem)
    if m:
        stem = m.group("stem")
    return d, stem, ext


def next_version(path):
    d, stem, ext = split(path)
    pat = re.compile(r"^" + re.escape(stem) + r"\.v(\d+)" + re.escape(ext) + r"$")
    used = [int(m.group(1)) for m in (pat.match(f) for f in os.listdir(d)) if m]
    n = max([1] + used) + 1
    while os.path.exists(os.path.join(d, "%s.v%d%s" % (stem, n, ext))):
        n += 1
    return os.path.join(d, "%s.v%d%s" % (stem, n, ext)), n


def write_new(target, content):
    # 'x' mode: fails instead of overwriting if something appeared meanwhile
    with open(target, "x", encoding="utf-8") as fh:
        fh.write(content)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Print (and with --content, write) the next version file next to PATH.")
    ap.add_argument("path", help="the original file")
    ap.add_argument("--content", help="file with the new text, or - for stdin; without it nothing is written")
    ap.add_argument("--format", choices=("json", "text"), default="json")
    a = ap.parse_args(argv)
    if not os.path.isfile(a.path):
        _text.fail("original not found: %s" % a.path)
    target, n = next_version(a.path)
    written = False
    if a.content:
        if a.content != "-" and os.path.abspath(a.content) == os.path.abspath(target):
            _text.fail("content file is the target itself")
        try:
            content = _text.read_input(a.content)
        except _text.BadInput as e:
            _text.fail(str(e))
        try:
            write_new(target, content)
        except FileExistsError:
            _text.fail("target appeared meanwhile, run again: %s" % target)
        written = True
    r = OrderedDict([("original", os.path.abspath(a.path)), ("version", n),
                     ("path", target), ("written", written)])
    if a.format == "text":
        print(("written: " if written else "next version: ") + target)
    else:
        _text.dump(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
