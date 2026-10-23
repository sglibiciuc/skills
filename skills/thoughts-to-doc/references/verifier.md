# The checker

## Handing over

Give it exactly three things: the text of the section "Task for the checker" below,
the path to `interview-log.md` and the path to `brief.md` (or their full text where
there are no files). Keep everything else out of its context: no summary of the
conversation, no notes on why the draft says what it says, no earlier verdicts.

## After the verdict

- `PASS`: show the draft.
- `FIX`: correct the draft for each item, taking the wording from the log entries
  the item cites and changing nothing else; then send the new draft to a new
  checker. If an item is wrong because the checker misread the log, leave the draft
  as it is and say why in one line when you show it.
- A `gap` item cannot be fixed from the log: put it to the person as an interview
  question (SKILL.md step 3), then write their answer into the brief, or the point
  into open questions if it stays unsettled.
- After three `FIX` rounds, show the draft with the remaining items listed under it.
  Where the checker and you read an answer differently, put the question to the
  person; the log is the evidence, the person is the judge.

## Task for the checker

You are checking a document against the interview it came from. You have two files:

- `interview-log.md` — numbered entries, each marked with its kind and who spoke:
  `opening`, `mode`, `answer` and `draft-feedback` are the person's words;
  `question`, `suggestion` and `draft` are the interviewer's.
- `brief.md` — the document written from this interview.

The brief may contain only what the person said or accepted. Read the log this way:

- An `opening`, `mode`, `answer` or `draft-feedback` entry is the person's position.
- A `suggestion`, or a paraphrase inside a `question` that adds to or changes what
  the person said, counts only if the person's next reply accepts it. Silence or a
  change of subject is not acceptance. A paraphrase that only repeats an answer
  needs no acceptance.
- A `draft` entry is the interviewer's text and supports nothing in the brief; a
  `draft-feedback` counts only for what it says itself.
- When the person changes their mind, the later entry wins.
- Facts from files count only once the person has confirmed them in the log.
- Rewording, shortening and reordering are fine as long as the meaning is the same.

Work in two passes.

**Pass 1 — everything left open.** Go through the log entry by entry and list every
point the person left undecided, unsure, conditional or for later ("not decided",
"don't know", "leave it open", "not until I say"). For each, find where the brief
puts it. It belongs in the open questions; anywhere else it is a `changed` item
(stated as decided, or listed as excluded) or a `missing` item (absent).

**Pass 2 — the whole brief against the whole log.** Check four things:

1. **missing** — something the person said or accepted that is absent from the
   brief.
2. **added** — a statement in the brief with no basis in the log: a detail, number,
   name, reason, priority or decision the person never gave or accepted.
3. **changed** — a statement that is in the log but means something different in the
   brief: softened, strengthened, generalised, or turned from open into decided.
4. **gap** — read the brief as its named reader about to do its stated action: a
   question you would have to come back and ask before starting, which the brief
   neither answers nor lists as open. What the person came with (the `opening` and
   the first answers) is always such a question until the brief settles it or lists
   it as open.

Reply in this format and nothing else:

```
VERDICT: PASS | FIX
OPEN IN LOG:
- <entry number>: <the point> → <open questions | stated as decided | listed as excluded | absent>
ITEMS:
- type: missing | added | changed | gap
  brief: "<exact quote from brief.md, or — for missing or gap>"
  log: <entry numbers, or — for added or gap>
  note: <one line: what is wrong>
```

`PASS` means no items. Any item means `FIX`.
