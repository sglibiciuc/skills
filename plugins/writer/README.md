# Writer

![Writer](assets/cover.png)

[Русский](README.ru.md)

Writer helps you put what you mean into words for your reader, whether you’re writing a client email, a post, a brief for a contractor, or a speech. Bring notes, a rough draft, an incoming message, or a description of what you need.

Before writing something new, Writer checks the meaning with you: who it is for, what the reader should understand or do, and what you are willing to promise. An agreed writing profile carries your voice and preferences into future texts. That might mean opening emails with the request, addressing clients by first name, or leaving out promotional adjectives.

It works in Claude Code, Codex, claude.ai, and Cowork.

## Install

In Claude Code and Codex, you need plugin support and Python 3 for the built-in checks. No additional Python libraries are required.

In Claude Code, run:

```text
/plugin marketplace add sglibiciuc/skills
/plugin install writer@sglibiciuc
```

For Codex, run these commands in your terminal:

```sh
codex plugin marketplace add sglibiciuc/skills
codex plugin add writer@sglibiciuc
```

In claude.ai and Cowork, you can install Writer as a skill. Download the [repository](https://github.com/sglibiciuc/skills) and ZIP the entire `plugins/writer/skills/writer` folder. Open Customize, select Skills, click “+,” then choose Create skill and Upload a skill. Upload the archive and enable the skill. In claude.ai, Code execution and file creation must also be enabled.

Start a new chat after installation. Use `/writer:writer` in Claude Code, include `$writer` in your Codex request, or say “Use Writer” in Claude. Then describe the task in ordinary words.

## Your first text

Until you have a profile, Writer offers once in each new chat to set it up now or later. It adds a short line to its usual reply and continues your task. If you only say hello, the offer is part of the introduction.

You could start with:

> Reply to the supplier. I accept the new price from 1 December. I am not agreeing to an annual contract yet. Here is their email…

This gives Writer the reader, your decision, and the boundary of your commitment. It will briefly restate the task and write the reply straight away. If you only say “Reply to the supplier” and attach their proposal, Writer will first ask what you want to accept, decline, or propose instead.

For other new texts with an incomplete brief, it proposes its understanding before drafting. You can confirm or correct it. After your reply, Writer continues the same task. This gives you a chance to catch a misunderstanding before it becomes a persuasive draft.

For an edit, name the problem: “cut this to 300 characters,” “too formal,” or “remove the AI tells.” Writer can then make the change straight away. Ask “assess this without rewriting it” to get comments while keeping the text untouched.

## Tasks to bring

| Task | Example request |
| --- | --- |
| Write from scratch | “Turn these notes into a brief for the contractor” |
| Reply to a message | “Decline the discount politely. Do not offer new terms” |
| Reach a different audience | “Turn this internal memo into a post for customers” |
| Shorten | “Keep this announcement within 500 characters, preserving the dates and address” |
| Explore wording | “Suggest five subject lines for the end-of-sale email” |
| Review | “Show me where the reader cannot tell what I need them to do” |

Writer also handles press releases, speeches, slide text, slogans, and names. You can ask for several texts about the same occasion. Paste the source material into the chat or attach a file. Word, PDF, and Google Docs support depends on the tools available in your environment.

## Make it sound like you

A profile helps when “clear and correct” still does not mean “I like it.” It can hold how you address people, the expressions you use, and your company’s rules, so you do not have to repeat them in every brief.

You can accept the invitation or ask for setup yourself:

> Set up Writer for me. I lead a small team, write to clients, and run a professional newsletter. I want to keep my own voice.

Writer asks who you are and what you write, requests 3–5 of your own texts, and studies your company’s editorial policy if you have one. Your samples help describe your voice. The editorial policy sets company requirements for forms of address, terminology, formatting, and tone. Writer then shows you the whole proposed profile and saves it after you agree. If a profile already exists, it incorporates the new decisions into it.

You can refine preferences while working, too. When you correct a rule about yourself or your company, Writer offers to remember it within a specific boundary: “In client emails, use first names. Remember this?” A detail in one email, such as a new meeting date, should stay specific to that email. An editorial policy supplied with a task is applied to that text, with an offer to save it for future use.

Before writing, editing, or reviewing, Writer reads the available profile. In an environment with persistent files, you can keep a global profile and separate project rules. They live outside the plugin and survive its updates. In claude.ai, Writer gives you the agreed profile or new rule to paste into the project instructions, because files in its working environment do not persist between chats.

## Before you get the result

Writer checks the complete draft for stock phrases, bureaucratic wording, chatbot residue, and any length limit you set. A flagged phrase needs a decision in context: an appropriate quotation or a necessary expression can stay. The check serves the text, so clearing every match is not the goal.

These checks cover wording and length. They do not automatically verify facts against external sources. Writer is instructed to preserve the facts and agreements you supply. Decisions about new commitments remain yours.

You can receive the result in the chat or as a file. When editing a file, Writer keeps the original and saves a separate revision.

You can write in any language. Dedicated language checks cover Russian and English, with common checks used for other languages. Translation, programming, legal review, and prompts for agents are outside Writer’s scope.

Licensed under [MIT](LICENSE). See [NOTICE](NOTICE) for the sources of ideas and acknowledgements.
