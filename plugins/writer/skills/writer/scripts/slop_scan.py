#!/usr/bin/env python3
"""Scan text for AI-writing tells listed in data/slop/*.json.

Reports places and reasons, never rewrites and never scores. Each finding is a
reason to look: the caller decides whether to change the place or keep it.
Severity says how often the pattern is a tell: 'hard' almost always, 'soft' only
in some contexts.

Usage:
  slop_scan.py FILE|-  [--lang auto|ru|en|<code>] [--ignore id,id] [--format json|text]

Exit 0 when the scan ran (with or without findings); 2 on bad input.
"""

import argparse
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _text  # noqa: E402

SLOP_DIR = os.path.join(_text.DATA_DIR, "slop")


def load_catalog(lang):
    """Return (patterns, files_used, note). Unknown language -> common only."""
    files = [os.path.join(SLOP_DIR, "common.json")]
    note = None
    lang_file = os.path.join(SLOP_DIR, "%s.json" % lang)
    if lang != "common" and os.path.isfile(lang_file):
        files.append(lang_file)
    else:
        note = "no pattern pack for language '%s'; scanned with common patterns only" % lang
    patterns = []
    for f in files:
        patterns.extend(_text.load_json(f)["patterns"])
    return patterns, [os.path.relpath(f, _text.DATA_DIR) for f in files], note


def compile_pattern(p):
    flags = re.UNICODE | re.MULTILINE
    if not p.get("case_sensitive"):
        flags |= re.IGNORECASE
    if "regex" in p:
        return re.compile(p["regex"], flags)
    alts = sorted((re.escape(w).replace(r"\ ", r"\s+") for w in p["words"]), key=len, reverse=True)
    return re.compile(r"(?<![\w])(?:" + "|".join(alts) + r")(?![\w])", flags)


def scan(text, lang="auto", ignore=()):
    detected = _text.detect_lang(text) if lang == "auto" else lang
    patterns, files, note = load_catalog(detected)
    starts = _text.line_starts(text)
    ignore = set(ignore)
    findings = []
    for p in patterns:
        if p["id"] in ignore:
            continue
        for m in compile_pattern(p).finditer(text):
            if m.end() == m.start():
                continue
            line, col = _text.line_col(starts, m.start())
            findings.append(OrderedDict([
                ("line", line), ("column", col), ("id", p["id"]),
                ("category", p["category"]), ("severity", p["severity"]),
                ("match", m.group(0).strip()[:120]), ("hint", p["hint"]),
            ]))
    findings.sort(key=lambda f: (f["line"], f["column"], f["id"]))
    n_words = len(_text.words(text))
    by_cat = OrderedDict()
    for f in findings:
        c = by_cat.setdefault(f["category"], {"hard": 0, "soft": 0})
        c[f["severity"]] += 1
    hard = sum(1 for f in findings if f["severity"] == "hard")
    summary = OrderedDict([
        ("words", n_words),
        ("findings", len(findings)),
        ("hard", hard),
        ("soft", len(findings) - hard),
        ("by_category", by_cat),
    ])
    return OrderedDict([
        ("language", detected),
        ("language_source", "auto" if lang == "auto" else "flag"),
        ("catalogs", files),
        ("note", note),
        ("ignored", sorted(ignore)),
        ("summary", summary),
        ("findings", findings),
    ])


def as_text(r):
    s = r["summary"]
    out = ["slop_scan: language=%s (%s), catalogs: %s" % (r["language"], r["language_source"], ", ".join(r["catalogs"]))]
    if r["note"]:
        out.append("note: " + r["note"])
    out.append("%d findings (hard %d, soft %d) in %d words"
               % (s["findings"], s["hard"], s["soft"], s["words"]))
    for cat, c in s["by_category"].items():
        out.append("  %-20s hard %d  soft %d" % (cat, c["hard"], c["soft"]))
    for f in r["findings"]:
        out.append("%d:%d  [%s] %s  «%s»  %s" % (f["line"], f["column"], f["severity"], f["id"], f["match"], f["hint"]))
    if not r["findings"]:
        out.append("No patterns matched.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Show places that look machine-written or bureaucratic, each with the "
                                             "reason. Never rewrites text; the caller decides.")
    ap.add_argument("path", help="text file, or - for stdin")
    ap.add_argument("--lang", default="auto", help="auto, ru, en or another language code; auto by default")
    ap.add_argument("--ignore", default="", help="comma-separated pattern ids to skip")
    ap.add_argument("--format", choices=("json", "text"), default="json")
    a = ap.parse_args(argv)
    try:
        text = _text.read_input(a.path)
    except _text.BadInput as e:
        _text.fail(str(e))
    lang = a.lang.strip().lower()
    if not re.fullmatch(r"auto|[a-z]{2,3}", lang):
        _text.fail("--lang must be auto or a 2-3 letter language code")
    ignore = [i.strip() for i in a.ignore.split(",") if i.strip()]
    r = scan(text, lang, ignore)
    if a.format == "text":
        print(as_text(r))
    else:
        _text.dump(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
