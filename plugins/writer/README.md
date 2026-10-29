# Writer

[Русская версия](README.ru.md)

Writer helps you write any work text simply, clearly and with care for the reader. The text does its job: the reader understands it on the first read and does what you need, and you don't have to redo it or worry that something was lost or something extra slipped in.

It works in Claude Code, Cowork, Codex and claude.ai, in any language.

In Codex, we recommend GPT-6.1 Terra. GPT-6.1 Sol also passed the targeted reply checks. GPT-6 Luna added unapproved offers of work or calls in three tested reply scenarios, including after clarification. For replies involving commitments, use Terra or Sol.

## Install

**Claude Code.** In the terminal, one command at a time:

```bash
claude plugin marketplace add sglibiciuc/skills
claude plugin install writer@sglibiciuc
```

**Codex:**

```bash
codex plugin marketplace add sglibiciuc/skills
codex plugin add writer@sglibiciuc
```

Then start a new session. Updates reach everyone through the catalog.

In Codex, review and trust Writer's hooks when prompted, or through `/hooks`. The hooks analyze private drafts and return findings to the writing agent before it delivers the text. Your own hooks and settings are kept as they are. Without active hooks, Writer uses the same bundled analysis during draft preparation.

**claude.ai.** Zip the `skills/writer` folder and upload it in Settings → Capabilities → Skills ("Upload skill"). Code execution must be on.

## How to use

Ask the way you would ask a colleague:

- "Reply to Marta at the supplier: we accept the new prices, the contract term is still open"
- "Write a post for tourists from this memo"
- "Make this letter shorter, the client won't read it"
- "Cut it to 600 characters"
- "This sounds like a robot, make it human"
- "Give me five subject lines"
- "What's wrong with this letter?" (you get a review, the text stays as it is)

If you ask to edit a text without saying what's wrong, Writer asks what bothers you first.

You can paste text or attach a file: a document, a PDF, a Google Doc. Your file stays as it is. A plain-text file (md, txt) gets a new version saved next to it; for a Word document, a PDF or a Google Doc you get the result in that format through your assistant's own tools.

## "Here's how I understood it"

Before a new text, Writer tells you in a few lines who will read it, what the text will say, what it will promise on your behalf, and what it assumes, for example: "The dates were her example, I won't confirm them. Right?" Answer "yes" or correct it. This takes a few seconds and saves a rewrite: a model on its own tends to fill gaps with guesses, such as dates and money you never agreed to.

When replying to someone else's request, if you have not said what you want to accept, decline or propose, Writer asks for your decision directly before drafting the reply.

If your request already says who the text is for, what to say, and what not to promise or what to keep quiet about, Writer writes at once and puts that one line above the text.

## Your profile

Say "set it up for me": Writer asks who you are and what you write, takes 3–5 of your texts for your voice, and reads your company's editorial policy if you have one. It saves the profile after your "yes".

When you correct something about yourself or your company (signature, how you address people, words you never use), Writer asks once "Remember this?" and shows where the rule applies, for example "in emails to clients". Nothing is saved without your "yes".

The profile is kept outside the plugin, so updates don't touch it: in `~/.writer` in Claude Code, in `.writer/` in your working folder in Cowork and Codex. In claude.ai Writer gives you a ready block to paste into your project instructions.

## If another skill answers instead

Other writing skills you have installed may catch the request first. Switch them off, or call Writer directly: `/writer:writer` in Claude Code, `$writer` in Codex.

## License

MIT, see [LICENSE](LICENSE). Collected from books by various authors, retold in our own words. The repositories behind the AI-tell patterns are credited in [NOTICE](NOTICE).
