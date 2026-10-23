---
name: thoughts-to-doc
description: >
  Interviews a person one question at a time until what is in their head becomes
  one plain brief that another person or an AI agent can act on. Use when someone
  says "help me explain what I want", "I can't put my idea into words", "interview
  me and write it up", or "turn my thoughts into a clear document" — in any
  language and on any topic. Do NOT use to build, write or implement the thing
  itself, or to grill a plan the person has already worked out.
license: MIT
compatibility: Python 3 for the log script; without it the log is kept by hand.
metadata:
  version: "1.0"
---

# Thoughts to doc

The person has something in their head and cannot yet say it plainly. Ask, one
question at a time, until it can be said — then say it for them in one short brief,
using only what they told you.

## Language

Write every message, including the explanation of the modes, in the language the
person writes to you in; switch when they switch. A reply with no language of its
own ("B", "ok", a number) or material they paste in another language does not
switch it. If they started you with no text, use the language of the conversation
so far. Write the brief in their language unless they ask for
another one for their reader.

## What the person gets

Two files in a task folder `<YYYY-MM-DD>_<topic-slug>/` (with no topic yet,
`<YYYY-MM-DD>_interview/`), inside the working folder the person named when they
started you, or else the current working directory:

- `interview-log.md` — the raw record: every message of the interview, verbatim and
  in order.
- `brief.md` — the plain document for its reader, built only from the log.

## Two modes

| Mode | What you do |
|---|---|
| **A. Questions only** | You ask and help them put it into words. Every idea comes from them. |
| **B. Questions and suggestions** | You ask, and where they are stuck or it would help, you offer two or three options, each marked as a suggestion. They decide; a suggestion enters the brief only once they accept it. |

The person chooses at the start and can switch at any time.

## Log entries

Every message of the interview goes into the log through `log.py append` (`--help`
lists the kinds): yours once its text is final, after the reread in step 3, and then
sent exactly as logged; theirs as soon as it arrives. The hand-over in step 8 is not
an entry.

- Each of your messages is one entry: `question` (the mode explanation, every
  question, every paraphrase put back to check), `suggestion` (mode B options) or
  `draft` (step 7).
- Each of the person's messages is one entry, copied as typed: `opening` for the
  message that started you, `mode` for any message that picks or switches the mode
  (the whole message, even when it also answers something), `answer` for a reply,
  `draft-feedback` for a reaction to a shown brief.

## How the work goes

1. **Start the log.** Before you say anything, run
   `python3 <skill-dir>/scripts/log.py init --dir <folder>`, where `<skill-dir>` is
   the folder this SKILL.md is in (`${CLAUDE_SKILL_DIR}` in Claude Code; on Windows
   use `py` or `python` if `python3` is missing). Append the opening message, if
   there is one, as `opening`.
2. **Offer the modes.** Explain A and B in two or three plain sentences and ask
   which one they want.
3. **Interview.** Open `references/doc-format.md` before the first question: its
   sections are what the interview must cover, starting with who will read the brief,
   then what they should do with it. Each message asks exactly one question, built on
   the last answer. Before sending, reread it: in mode A it carries no example, no
   choice of answers and no formula of yours; if it asks for two things, keep the
   one the last answer most calls for and save the other for the next turn. A
   paraphrase put back to check is that turn's question. One that only repeats the
   answer needs no confirmation; one that adds or changes something enters the
   brief only once the person's next reply accepts it.
4. **Reader check.** Before drafting, picture the named reader about to do their
   action with nothing but the brief. List what they would have to come back and
   ask. Put each point to the person as an interview question, by step 3's rules;
   whatever stays unsettled is an open question. The interview is done when the log answers the required sections
   of `references/doc-format.md` and every point on that list is answered or open.
5. **Draft.** Write `brief.md` by `references/doc-format.md`.
6. **Independent check.** Hand the draft to a fresh agent with a clean context (a
   subagent) by `references/verifier.md`, and act on its verdict as that file says.
7. **Show.** Give the person the brief in the chat, headed by the checker's last
   verdict, any discrepancy it still reports, and the note that the check was not
   independent where it was not. Log this message as `draft`, then their reaction as
   `draft-feedback`. Any change to the brief — theirs or yours, however small — goes
   through step 6 and is shown again.
8. **Hand over.** Where the person cannot open the task folder (a web app), give
   them both files in the chat to download. Passing the brief on is theirs.

If a fact is in material the person pointed you to, read it rather than ask — then
confirm it with them in a question, so the log holds it.

## Pitfalls

- **Tidying the log.** Typos, half-sentences and "um, actually no" stay as typed.
  The checker can only catch an invented detail if the original is untouched.
- **Filling gaps.** "The reader probably also wants…" is your guess, not their
  answer. An unanswered point goes into open questions.
- **Stacking questions.** The log can no longer show which answer belongs to which
  question.
- **Sliding into the solution.** Once the idea is clear you will be tempted to
  design it. Stop at describing it.

## When the environment is limited

- **No file access** (a plain chat): keep the log in the conversation as you go, in
  the same entry format, and give both documents in full at the end, log first.
- **No Python:** append to `interview-log.md` by hand in the same entry format.
- **No way to start a separate agent with a clean context** (no such tool): do the
  check yourself as a separate pass by `references/verifier.md`, and tell the person plainly that the check was not
  independent. They can get an independent one by pasting the checker task from
  that file and both documents into a fresh chat.

## Done when

- Both files are in the task folder.
- The log holds every message of the interview, shown drafts included, verbatim
  and in order.
- The checker's last verdict on the current brief is `PASS`, or the person has seen
  every remaining discrepancy.
- The text in `brief.md` is the text the person last confirmed says what they mean.
- The person has both files: in their working folder, or to download in the chat.

Until all of this is true, keep going; you stop only for the mode choice, each
interview question and showing the draft.

## Hard limits

- The brief holds only what the person said or accepted — it speaks for them, and
  an invented detail becomes their commitment.
- The log only grows at the end — earlier entries are the evidence the checker and
  the person rely on, so they stay as written.
