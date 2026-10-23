# Thoughts to doc

A skill that asks you questions until what is in your head becomes one plain
document someone else can act on.

You have an idea, a picture of how something should work, a process you run on
instinct — and when you try to explain it, it comes out tangled. Thoughts to doc
interviews you one question at a time, each question built on your last answer,
and then writes down what you want in a short document for whoever needs to read
it: your manager, a contractor, your team, or an AI agent.

It does not build the thing. It does not write the website, the campaign or the
code. It helps you say what you want, clearly.

## What you get

Two files in a new folder inside the working folder you started the skill in; in a
web app, the skill gives you both files in the chat to download:

- **`brief.md`** — the plain document: who it is for, what you want in one sentence,
  why, what exactly, and what is still open.
- **`interview-log.md`** — every question and every answer, word for word. Nothing in
  it is corrected. It is your record of what you actually said.

Before you see the brief, a separate checker that was not part of the conversation
compares it against the log: nothing you said may be missing, and nothing you did
not say may be added. If your tool cannot start such a checker, the skill tells you
so.

The skill is done when you have read the brief and confirmed it says what you mean.
If anything in it changes after that, you see it again.

## Two modes

At the start you choose how the interview goes:

- **Questions only.** The skill asks and helps you put things into words. Every idea
  in the document is yours.
- **Questions and suggestions.** Where you are stuck, the skill offers two or three
  options, clearly marked. Only the ones you accept go into the document.

You can switch modes at any point.

## Any language

The skill's instructions are in English, but it talks to you in the language you
write in, and writes the brief in that language too, unless you ask for another.

## Install

Download or clone the `thoughts-to-doc/` folder, then put it where your tool looks
for skills.

**Claude Code** — copy the folder into `.claude/skills/` in your project, or into
`~/.claude/skills/` to have it everywhere. Start a new session.

**Claude apps** — zip the folder and upload it as a skill in your settings.

**OpenAI Codex** — copy the folder into `.agents/skills/` in your repository, or into
`~/.agents/skills/` to have it everywhere.

**Gemini CLI** — copy the folder into `.gemini/skills/` in your project, or into
`~/.gemini/skills/`; or install it from its repository with
`gemini skills install <repo-url>` (add `--path <folder>` if the skill sits in a
subfolder of the repository). Gemini asks you to allow
the skill the first time it starts.

**Other agents** — copy the folder into your project and add one line to the
instructions file your agent reads at start-up (for example `AGENTS.md`), saying
that "help me explain what I want" requests go through `thoughts-to-doc/SKILL.md`.

**A chat without skill support** — paste `SKILL.md` and both files from
`references/` at the start of the conversation, then say what you want to explain.
The skill keeps the log in the chat and gives you both documents at the end.

The log is kept by a small Python 3 script (standard library only). Without Python
the skill keeps the log by hand in the same format.

## How to call it

Type the skill's name, optionally followed by whatever you already have:

- Claude Code: `/thoughts-to-doc I want a website for my practice but don't know what should be on it`
- Codex: `$thoughts-to-doc …` (or pick it from `/skills`)

Or just say it — this is also the way in Gemini CLI, which starts skills from what
you ask rather than by name:

> "help me explain what I want"
> "I see this mechanic in my head but can't describe it to my boss"
> "interview me and write it up"

## Your data

The skill keeps both documents in your task folder, or in the chat where there are
no files. Passing the brief on is up to you.

## License

MIT
