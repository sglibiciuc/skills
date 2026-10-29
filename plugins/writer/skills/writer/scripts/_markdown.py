# Adapted from ilyautov/humanizer-ru, commit 3621b1ca6b9a2f84f28f692222470dc25706255d.
# MIT license: ../licenses/ilyautov-MIT.txt.
"""Mask closed Markdown code while preserving offsets, quotes and URLs.

Reuses upstream fence recognition. Writer adds exact-run inline delimiters
and escaped opener handling. Unclosed fences stay visible for review.
This is a bounded code projection, not a complete CommonMark parser.
"""
from __future__ import annotations
import re

GAP = "·"
_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*$")

def _blank(s: str) -> str:
    return re.sub(r"[^\n]", GAP, s)


def _fence_ranges(lines: list[str]) -> list[tuple[int, int]]:
    """Inclusive line ranges for closed fenced code blocks."""
    ranges: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        m = _FENCE_OPEN.match(lines[i])
        if not m or (m.group(1)[0] == "`" and "`" in m.group(2)):
            i += 1
            continue
        ch, need = m.group(1)[0], len(m.group(1))
        j = i + 1
        while j < len(lines):
            c = _FENCE_CLOSE.match(lines[j])
            if c and c.group(1)[0] == ch and len(c.group(1)) >= need:
                break
            j += 1
        if j >= len(lines):
            i += 1
            continue
        ranges.append((i, j))
        i = j + 1
    return ranges


def mask_code(text: str) -> str:
    """Writer projection: keep quotes/URLs visible, mask only closed code.

    Adaptation: inline delimiters must have equal run lengths, including
    embedded shorter backtick runs. Offsets and newlines remain unchanged.
    """
    lines = text.split("\n")
    in_code = {i for a, b in _fence_ranges(lines) for i in range(a, b + 1)}
    out = []
    for i, line in enumerate(lines):
        if i in in_code:
            out.append(_blank(line))
            continue
        runs = list(re.finditer(r"`+", line))
        chars = list(line)
        j = 0
        while j < len(runs):
            before = line[:runs[j].start()]
            slashes = len(before) - len(before.rstrip("\\"))
            if slashes % 2:
                j += 1
                continue
            end = next((k for k in range(j + 1, len(runs))
                        if len(runs[k].group()) == len(runs[j].group())), None)
            if end is None:
                j += 1
                continue
            chars[runs[j].start():runs[end].end()] = _blank(line[runs[j].start():runs[end].end()])
            j = end + 1
        out.append("".join(chars))
    return "\n".join(out)
