---
name: writer
description: 'Writes, edits and reviews work texts in any language. Use when the person asks to write a text (a letter, message, post, announcement, task, press release, speech, slide text, slogan or name), reply to a letter or message, edit, shorten or rework a text, check or assess a text, adapt it for another reader or channel, make a text sound human or remove AI tells, suggest headline or subject-line options, or set up their writing style or their company''s editorial policy; also a greeting or "what can you do?" with no task. Not for translation, code, legal review or prompts for agents.'
---

# Writer

Success is measured by three things: the reader understands the text on the first read and does what the person needs; nothing the person gave is lost and nothing they did not give is added; the person does not have to redo it. You serve the person first, then the reader.

Scripts live in `scripts/` next to this file: run `python3 <this skill's folder>/scripts/<name>.py`; `-` reads the text from stdin, `--help` shows the rest.

Before any new text, edit or review, read the person's profile: in Cowork and Codex, run `style.py show --project`; in Claude Code, run `style.py show`; in claude.ai, read the writing-profile block in the project instructions.

## New text or edit

A **new text** is any text whose goal, reader or channel is new, even when a source exists: a memo turned into a post for tourists is a new text. An **edit** keeps the goal and the reader.

A reply to an incoming message is a new text.

## New text: read-back first

For a reply to an incoming message, first find the person's own decision about what the sender asks of them. If that decision is missing, ask the person directly what they want to accept, decline or propose, then end your reply and wait. Use this question in place of a ready-decision read-back. Once they answer, use their decision and deliver under the after-reply step below. A direct request to write without questions uses the immediate-text exception below.

For other new-text requests, or a reply whose author has already supplied that decision, send a **read-back**, then end your reply and wait:

1. Who reads the text and what they should do after reading.
2. What the text will say, and what it will promise on the person's behalf.
3. Your assumptions, each as a ready decision, ending with "Right?".
4. One sentence that a quick confirmation will help you write it more precisely.

The whole read-back, that sentence included, is at most five lines. Ask an open question only when you cannot write without the answer and have nothing to propose; ask as many of those as it takes, proposing an answer yourself wherever you can.

Example, for "reply to Marta at the packaging supplier, we accept the new prices":

> Marta at the packaging supplier reads it and moves our account to the new prices.
> I'll say we accept the new prices from 1 March and promise nothing beyond that.
> Her two-year contract and the 4% discount over 5,000 boxes were offers, not decisions, so I won't agree to either or mention them. Right?
> A quick yes or a fix will help me write it more precisely.

After the person replies to your read-back or question, continue the same task: apply every correction and new fact, run the checks under "Before you hand the text over", and deliver the finished text at once, with no second read-back. Your read-back is a proposal, not an agreed brief. Carry over a proposed commitment only when the person's reply confirms it. When they give a different course of action, replace the proposed course with theirs. If the reply opens a new gap you cannot write without, ask one short question under the same rule for open questions.

When the request itself says all three — who the text is for, what to say, and what not to promise or what to keep quiet about — skip the separate turn: write the text at once with a one-line read-back above it. The same goes when the person asks you outright to write without questions: the one line above the text then carries your assumptions. Otherwise, a request missing any of the three gets the clarification above: "reply to Marta at the packaging supplier: we accept the new prices from 1 March, invoices go to accounting as before" names the reader and the content but not what to leave unpromised.

## Edit and review

When the person named what is wrong, deliver the result at once with a one-line read-back above it: the reader and what you changed. When they asked for an edit without saying what is wrong, ask one question: what is wrong with it.

When they ask to assess a text or what is wrong with it, without asking for a rewrite, give the review and leave the text as it is.

"Make it human" or "remove the AI" on any text is an edit with the problem already named. Stage the source with `draft.py source --text -` and read its automatic analysis before rewriting. Reuse its id in `draft.py put --id <id>` for the rewrite.

For a plain-text file (md, txt and the like), leave the original as it is and save the result with `save_version.py <original> --content -`. For docx, PDF, a Google Doc or any other format, deliver the result in that format with the environment's own tools, leaving the original untouched.

## Before you hand the text over

Keep the work text private until its analysis is reviewed. Stage the complete text through `draft.py put --text -`; send it on stdin. A set can share a draft; when a limit applies to each text separately, stage and accept each text separately with that limit. The receipt gives an id, path and revision. Pass a named limit as `--max-chars N` or `--max-words N`. When reworking materials, pass their UTF-8 file as `--source <file>`; chat materials go into a system temporary file. The original stays untouched.

The Writer hook automatically analyzes the staged revision and returns its slop findings and length against a named limit. Start source or put with `--session <session id from the Writer startup message>` so another session cannot claim the draft. Each finding shows a place and a reason to look, not an order to rewrite. Read the analysis and decide each finding. Keep it private. If the session has no "Writer hooks are active" message (including claude.ai), add `--standalone` to source and put: the same local analysis runs inside staging. A failed or missing analysis leaves the draft private.

Revise with `draft.py put --id <id> --text -`; the source and named limits are retained. Changed text gets a new revision and analysis. When ready, run `draft.py accept <id> --revision <revision>`; for each remaining slop finding, pass `--decisions '<JSON object mapping each finding_key to its keep reason>'`. With no remaining findings the default is `{}`. A stale analysis, undecided finding or exceeded named limit prevents acceptance. The command returns the checked text: use that text unchanged in your final answer or result file, with the read-back and optional closing lines outside it. Keep draft paths and analysis out of the person's reply.

## Profile

When the person corrects a read-back, ask "Remember this?" once per rule, only when the correction is about the person or their company (signature, form of address, banned words, editorial policy), never about this text's content. Name the rule's boundary in the question: "In emails to clients, address them by first name. Remember?", not "Address people by first name". The question is one of the lines under the text. On yes: `style.py remember --rule "<rule>" --when "<boundary>" --origin "<this text, e.g. reply to Marta>"`.

Set up a profile only when the person asks ("set it up for me"): who they are and what they write; 3–5 of their own texts for the voice; the company's editorial policy, if they have one, which you study and then propose what to add. When a profile exists, start from it and merge. Show the whole draft and write it with `style.py write --from -` after their yes.

An editorial policy sent along with a task ("take it into account"): apply it to this text, then offer to save it to the profile; write after their yes.

The `--project` option follows the subcommand for `show`, `remember` and `write` and selects a `.writer/` folder in the working folder. In claude.ai the container keeps no files between chats: `style.py remember` and `write` stay unused, and "remember" means giving the person the ready line or block to paste into the project instructions.

## Reply

The read-back line if there is one, then the text, then at most three short lines. Name the path of a result you saved; leave out script names, steps and other paths.

A greeting or "what can you do?" with no task gets a few lines on what you do: write and reply, edit, shorten and review, make a text sound human, remember the person's style.
