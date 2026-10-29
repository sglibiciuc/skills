"""Shared helpers for the writer scripts. Standard library only.

Not a CLI. Imported by the other scripts.
Boundaries never use \\b: Cyrillic needs explicit (?<![\\w]) ... (?![\\w]).
"""

import json
import os
import re
import sys

FLAGS = re.UNICODE | re.IGNORECASE

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
LANG_DIR = os.path.join(DATA_DIR, "lang")
_LANG_CACHE = {}


def load_lang(code):
    """Word lists of one language from data/lang/<code>.json; {} when the file is missing."""
    if code not in _LANG_CACHE:
        path = os.path.join(LANG_DIR, "%s.json" % code)
        _LANG_CACHE[code] = load_json(path) if os.path.isfile(path) else {}
    return _LANG_CACHE[code]


def all_langs():
    """Every language file in data/lang, as a list of dicts (empty when there are none)."""
    if not os.path.isdir(LANG_DIR):
        return []
    codes = sorted(f[:-5] for f in os.listdir(LANG_DIR) if f.endswith(".json"))
    return [load_lang(c) for c in codes]


WORD_RE = re.compile(r"[^\W\d_](?:[\w’'-]*[^\W_])?", re.UNICODE)
CYR_RE = re.compile("[\u0430-\u044f\u0451\u0410-\u042f\u0401]")
LAT_RE = re.compile(r"[a-zA-Z]")
LETTER_RE = re.compile(r"[^\W\d_]", re.UNICODE)

EN_STOP = {
    "the", "and", "of", "to", "a", "in", "is", "it", "that", "for", "on",
    "with", "as", "was", "be", "this", "are", "you", "we", "at", "by", "or",
    "not", "have", "from", "but", "they", "an", "will", "your", "our",
}


class BadInput(Exception):
    """Raised for unreadable input; CLIs turn it into exit code 2."""


def read_input(path):
    """Read UTF-8 text from a path or '-' (stdin)."""
    if path is None:
        raise BadInput("no input: give a file path or '-' for stdin")
    if path == "-":
        data = sys.stdin.buffer.read()
    else:
        if not os.path.isfile(path):
            raise BadInput("file not found: %s" % path)
        with open(path, "rb") as fh:
            data = fh.read()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise BadInput("input is not valid UTF-8: %s" % path)


def fail(msg):
    sys.stderr.write("error: %s\n" % msg)
    sys.exit(2)


def words(text):
    return WORD_RE.findall(text)


def detect_lang(text):
    """Guess 'ru', 'en' or 'other' by script share, then stop-word hit rate."""
    cyr = len(CYR_RE.findall(text))
    lat = len(LAT_RE.findall(text))
    letters = len(LETTER_RE.findall(text))
    if letters == 0:
        return "other"
    toks = [w.lower() for w in words(text)]
    n = max(1, len(toks))
    if cyr / letters >= 0.5:
        stop = set(load_lang("ru").get("stop_words", []))
        hits = sum(1 for t in toks if t in stop)
        # Cyrillic but no Russian function words: Ukrainian, Bulgarian, etc.
        if n >= 8 and hits / n < 0.04:
            return "other"
        return "ru"
    if lat / letters >= 0.5:
        hits = sum(1 for t in toks if t in EN_STOP)
        if n >= 8 and hits / n < 0.05:
            return "other"
        return "en"
    return "other"


def line_starts(text):
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def line_col(starts, offset):
    """1-based line and column for a character offset."""
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1, offset - starts[lo] + 1


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
