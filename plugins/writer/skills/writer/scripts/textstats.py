#!/usr/bin/env python3
"""Count a text's length and compare it with a limit the person named.

Characters are counted on the trimmed text, with and without spaces; words as the
other scripts split them. With --max-chars or --max-words the output says how far
the text is under or over that limit. There is no built-in limit.

Usage:
  textstats.py FILE|-  [--max-chars N] [--max-words N] [--format json|text]

Exit 0 when counted; 2 on bad input.
"""

import argparse
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _text  # noqa: E402


def measure(text, max_chars=None, max_words=None):
    trimmed = text.strip()
    r = OrderedDict([
        ("characters", len(trimmed)),
        ("characters_no_spaces", len(re.sub(r"\s", "", trimmed))),
        ("words", len(_text.words(trimmed))),
    ])
    limits = OrderedDict()
    if max_chars is not None:
        limits["characters"] = OrderedDict([("limit", max_chars), ("value", r["characters"]),
                                            ("over_by", r["characters"] - max_chars)])
    if max_words is not None:
        limits["words"] = OrderedDict([("limit", max_words), ("value", r["words"]),
                                       ("over_by", r["words"] - max_words)])
    r["limits"] = limits
    return r


def as_text(r):
    out = ["characters: %d (no spaces %d), words: %d" % (r["characters"], r["characters_no_spaces"], r["words"])]
    for unit, l in r["limits"].items():
        if l["over_by"] > 0:
            out.append("%s: %d, limit %d, over by %d" % (unit, l["value"], l["limit"], l["over_by"]))
        else:
            out.append("%s: %d, limit %d, %d to spare" % (unit, l["value"], l["limit"], -l["over_by"]))
    return "\n".join(out)


def positive(s):
    n = int(s)
    if n <= 0:
        raise argparse.ArgumentTypeError("must be a positive number")
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description="Count characters and words; compare with a limit the person named.")
    ap.add_argument("path", help="text file, or - for stdin")
    ap.add_argument("--max-chars", type=positive, help="the person's limit in characters (spaces included)")
    ap.add_argument("--max-words", type=positive, help="the person's limit in words")
    ap.add_argument("--format", choices=("json", "text"), default="json")
    a = ap.parse_args(argv)
    try:
        text = _text.read_input(a.path)
    except _text.BadInput as e:
        _text.fail(str(e))
    r = measure(text, a.max_chars, a.max_words)
    print(as_text(r)) if a.format == "text" else _text.dump(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
