"""Contextual observations for an editor, not acceptance gates or AI verdicts."""
import re
from collections import defaultdict
import _text
import _repeats

WORD = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", re.UNICODE)
SENTENCE = re.compile(r"[^.!?\n]+(?:[.!?]+|(?=\n)|$)")
HEDGES = {
    "ru": r"(?<!\w)(?:возможно|вероятно|пожалуй|скорее всего|в некоторых случаях|в определённой степени|может быть|по всей видимости|в целом)(?!\w)",
    "en": r"(?<!\w)(?:perhaps|possibly|probably|arguably|in some cases|to some extent|it seems|might|may)(?!\w)",
}


def collect(text, lang, patterns, compile_pattern, ignore=()):
    starts = _text.line_starts(text)
    result = []
    def add(ident, hint, spans, **extra):
        if ident in ignore or not spans:
            return
        places = []
        for start, end in spans[:4]:
            line, column = _text.line_col(starts, start)
            places.append({"line": line, "column": column,
                           "match": text[start:end].strip()[:180]})
        result.append({"id": ident, "hint": hint, "places": places,
                       "occurrences": len(spans), **extra})
    for p in patterns:
        matches = list(compile_pattern(p).finditer(text))
        if len(matches) >= p.get("min_hits", 1):
            add(p["id"], p["hint"], [(m.start(), m.end()) for m in matches])

    if lang not in HEDGES:
        return result
    sentences = [m for m in SENTENCE.finditer(text) if WORD.search(m.group())]
    for s in sentences:
        hedges = list(re.finditer(HEDGES[lang], s.group(), re.I))
        if len(hedges) >= 3:
            add("obs-hedge-stack", "Several uncertainty markers qualify one sentence. Check whether they repeat the same caution; preserve the uncertainty supported by the source.",
                [(s.start()+h.start(), s.start()+h.end()) for h in hedges])

    # Upstream algorithm has a bounded 600-token window and merges overlapping
    # n-grams. Resolve its normalized phrases back to positions in the original.
    repeats = _repeats.repeat_stats(text)
    for phrase in repeats.phrases[:5]:
        tokens = [re.escape(t).replace("е", "[её]") for t in phrase.split()]
        rx = re.compile(r"(?<!\w)" + r"[\s,]+".join(tokens) + r"(?!\w)", re.I)
        spans = [(m.start(), m.end()) for m in rx.finditer(text)]
        if len(spans) > 1:
            add("obs-repeated-phrase", "The same phrase appears in different paragraphs. Does it add something each time? Keep intentional anaphora, names and necessary reminders.", spans)

    lines = []
    offset = 0
    for line in text.splitlines(True):
        if line.strip():
            lines.append((offset, line.rstrip()))
        offset += len(line)
    openings = defaultdict(list)
    paragraph_lengths = []
    for i, (start, line) in enumerate(lines):
        tokens = list(WORD.finditer(line))
        if not tokens or re.match(r"^\s*(?:#|>|[-*+]\s|\d+[.)]\s)", line):
            continue
        paragraph_lengths.append(len(tokens))
        if len(tokens) >= 5:
            key = tuple(t.group().lower() for t in tokens[:2])
            openings[key].append((start+tokens[0].start(), start+tokens[1].end()))
    for spans in openings.values():
        if len(spans) >= 3:
            add("obs-repeated-opening", "Several paragraphs start alike. Check whether each develops a different thought; deliberate parallelism can stay.", spans)

    for i, (start, line) in enumerate(lines[:-1]):
        heading = re.match(r"^\s*#{1,6}\s+(.+)", line)
        if heading:
            title = [w.lower() for w in WORD.findall(heading.group(1))]
            nxt_start, nxt = lines[i+1]
            first = [w.lower() for w in WORD.findall(nxt)]
            if title and first[:len(title)] == title:
                add("obs-heading-echo", "The paragraph opens by repeating its heading. Does this sentence add useful information for this reader?", [(start, start+len(line)), (nxt_start,nxt_start+min(len(nxt),180))])

    # Sequences on one line, not bullets or dialogue. Their function is judged
    # by the author; a short request or a title is not a rhythm defect.
    for start, line in lines:
        if re.match(r"^\s*(?:#|>|[-–—*+]\s|\d+[.)]\s)", line):
            continue
        run = []
        for s in SENTENCE.finditer(line):
            words = WORD.findall(s.group())
            if 1 <= len(words) <= 3 and s.group().rstrip().endswith("."):
                run.append((start+s.start(), start+s.end()))
            else:
                if len(run) >= 3:
                    add("obs-short-chain", "A chain of very short statements creates a clipped rhythm. Check whether this is intentional emphasis or a thought split into fragments.", run)
                run = []
        if len(run) >= 3:
            add("obs-short-chain", "A chain of very short statements creates a clipped rhythm. Check whether this is intentional emphasis or a thought split into fragments.", run)

    # Descriptive lengths are useful only on longer prose. No score, target,
    # author-origin classification or requirement to change these numbers.
    lengths = [len(WORD.findall(s.group())) for s in sentences]
    if len(lengths) >= 8 and "obs-rhythm" not in ignore:
        result.append({"id":"obs-rhythm", "hint":"Sentence lengths are a reading aid, not a quality target. Look for repeated sentence shapes or overloaded passages only if they hinder this reader.",
                       "sentence_word_lengths":lengths[:60], "scope":"first 60 sentences",
                       "paragraph_word_lengths":paragraph_lengths[:30]})
    return result
