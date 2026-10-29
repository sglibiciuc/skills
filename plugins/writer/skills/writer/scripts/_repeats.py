# Adapted from ilyautov/humanizer-ru, commit 3621b1ca6b9a2f84f28f692222470dc25706255d.
# MIT license: ../licenses/ilyautov-MIT.txt. Adaptation: English tokens below.
"""Repeated phrases across lines, adapted from the upstream six-token method.

Writer extends the bounded 600-token scan to English. Quotes are excluded,
headings skipped, overlapping n-grams merged, and function-only phrases ignored.
Results are observations; no score or authorship inference is computed.
"""


from __future__ import annotations

import re
from dataclasses import dataclass, field

REPEAT_N = 6
REPEAT_MAX_TOKENS = 600
REPEAT_MIN_CONTENT = 2
REPEAT_MIN_PHRASES = 2

FUNCTION_WORDS = frozenset("""
а б бы в во вот да для до же за и из или им их к ко как ли либо между на над не ни но о об обо
от ото по под при про с со так там то тоже только у уже чем что чтобы это этот эта эти этого этой
этом этим тот та те того той том тем тех я ты он она оно мы вы они его ее их ему ей нам вам
меня тебя нас вас мне тебе себя себе свой своя свое свои своего своей своих своим который которая
которое которые которого которой которых котором которым был была было были быть есть будет будут
бывает если когда где куда чтоб все весь вся всего всех всем также еще уж даже лишь нет
очень более менее можно нужно надо может могут мой моя мое мои наш наша наше наши ваш ваша ваше
ваши кто чего чему ним ней них него нее нему
""".split())

# Writer adaptation: include English and keep digits as chain boundaries.
FUNCTION_WORDS = FUNCTION_WORDS | frozenset("a an the and or but of to in on at for from with without by as is are was were be been it this that these those i you he she we they my your our their not no can could would should will have has had".split())
_TOKEN_RE = re.compile(r"[а-яёa-z]+(?:-[а-яёa-z]+)*|[0-9]+|[.!?…;:()\[\]\"«»“”„]")
_QUOTE_RE = re.compile(r"«[^«»\n]*»|„[^„“\n]*“|\"[^\"\n]*\"")
_HEADING_RE = re.compile(r"^[ \t]*#{1,6}[ \t]")


@dataclass
class RepeatStats:
    tokens: int
    phrases: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"tokens": self.tokens, "phrases": list(self.phrases)}


def _runs(line: str) -> list[list[str]]:
    """Consecutive word runs, split by numbers and sentence boundaries."""
    runs: list[list[str]] = []
    cur: list[str] = []
    for tok in _TOKEN_RE.findall(line.lower()):
        if "а" <= tok[0] <= "я" or tok[0] == "ё" or "a" <= tok[0] <= "z":
            cur.append(tok.replace("ё", "е"))
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return runs


def repeat_stats(text: str) -> RepeatStats:
    """Return merged phrases repeated across separate lines."""
    text = _QUOTE_RE.sub(" . ", text)
    budget = REPEAT_MAX_TOKENS
    where: dict[str, set[int]] = {}
    order: list[tuple[int, int, list[str]]] = []
    pos = 0
    for li, line in enumerate(text.split("\n")):
        if budget <= 0:
            break
        if _HEADING_RE.match(line):
            continue
        for run in _runs(line):
            run = run[:budget]
            budget -= len(run)
            for i in range(len(run) - REPEAT_N + 1):
                key = " ".join(run[i:i + REPEAT_N])
                where.setdefault(key, set()).add(li)
                order.append((li, pos + i, run[i:i + REPEAT_N]))
            pos += len(run) + 1
            if budget <= 0:
                break
    seen = REPEAT_MAX_TOKENS - max(budget, 0)

    def repeated(words: list[str]) -> bool:
        key = " ".join(words)
        return (len(where[key]) >= 2
                and sum(1 for w in words if w not in FUNCTION_WORDS) >= REPEAT_MIN_CONTENT)

    phrases: list[str] = []
    keys: set[str] = set()
    cur: list[str] = []
    cur_key = ""
    prev = (-1, -2)
    for li, p, words in order:
        if not repeated(words):
            continue
        if prev[0] == li and prev[1] == p - 1 and cur:
            cur.append(words[-1])
        else:
            if cur and cur_key not in keys:
                keys.add(cur_key)
                phrases.append(" ".join(cur))
            cur, cur_key = list(words), " ".join(words)
        prev = (li, p)
    if cur and cur_key not in keys:
        phrases.append(" ".join(cur))
    return RepeatStats(tokens=seen, phrases=phrases)
