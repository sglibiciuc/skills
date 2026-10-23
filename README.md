[English](README.md) | [Русский](README.ru.md)

![Coordinator — from idea to a working product](assets/coordinator-cover.png)

# sglibiciuc/skills

Sasha Glibiciuc's open-source plugins and skills for AI assistants. The repository is also a plugin marketplace named `sglibiciuc`.

## Coordinator

Coordinator 1.0.0 is a plugin for Claude Code and Codex. You talk to one agent, the Coordinator. It asks what you want and agrees with you how it will work. Then a team of role agents builds the thing and checks it. You get a working product: an automation, a skill, a plugin, a website or an app.

It is for anyone who works in Claude Code or Codex and wants a finished, usable thing rather than a chat answer. You can also bring a ready brief or spec, or ask the Coordinator to check or improve something you already have.

How a task goes:

1. The Coordinator asks questions one at a time and suggests an answer to each. You can reply "you decide".
2. It shows two short documents, "what you want" and "how it will work". You approve each one.
3. It shows the plan and asks whether to start.
4. It builds and checks the result, with one progress line after each finished piece.
5. You get the finished thing and instructions on how to use it.

Your own files are not edited: the work happens in copies, and a copy replaces the working one only after you say "yes".

Requirements: Claude Code or Codex, and Python 3 (check with `python3 --version`).

### Install in Claude Code

1. In a Claude Code session, add the marketplace:

   ```
   /plugin marketplace add sglibiciuc/skills
   ```

2. Install the plugin:

   ```
   /plugin install coordinator@sglibiciuc
   ```

   From the terminal, without a session, the same two steps are:

   ```bash
   claude plugin marketplace add sglibiciuc/skills
   claude plugin install coordinator@sglibiciuc
   ```

3. Check: `claude plugin list` shows `coordinator@sglibiciuc` with status `enabled`.

### Install in Codex

1. Add the marketplace in the terminal:

   ```bash
   codex plugin marketplace add sglibiciuc/skills
   ```

2. Install the plugin:

   ```bash
   codex plugin add coordinator@sglibiciuc
   ```

3. Check: `codex plugin list --marketplace sglibiciuc` shows `coordinator@sglibiciuc` with status `installed, enabled`.

4. Open the terminal in the folder where you want to work on your task and start a new `codex` session; the plugin loads only in a new session. On the first start Codex shows a `Hooks need review` window. Press the Down arrow once to highlight `2. Trust all and continue`, then press Enter. The hooks keep the Coordinator from stopping halfway and bring it back to the task after a break.

### Start working

1. Open the terminal in the folder where you want to work on your task and start `claude` or `codex`.
2. Call the Coordinator and write what you want to get:
   - Claude Code: type `/coordinator:coordinator` and your request, for example `/coordinator:coordinator every morning I want a summary of new emails from clients`.
   - Codex: type `@`, pick `coordinator (coordinator)` in the list and press Enter. The input shows `$coordinator:coordinator`. After a space, write your request.
3. To continue a task later, start Claude Code or Codex in the same folder and write "continue".

The Coordinator keeps each task in its own folder: your answers, the approved documents, the plan, the reports and the backlog. Full plugin guide in English and Russian: [plugins/coordinator/README.md](plugins/coordinator/README.md).

## Skills

Standalone skills in `skills/`. Each folder has its own `SKILL.md` or `README.md` with details.

| Skill | Language | What it does |
|-------|----------|--------------|
| [autonomous-loop-onboarding](skills/autonomous-loop-onboarding/) | EN | Interviews you about your tools and sets up an autonomous task loop: you queue a task in your task manager, an AI agent does it, checks its own work and hands it back for your approval. |
| [clear-writing](skills/clear-writing/) | RU | Writes, edits and reviews business emails and messages using the method of Maxim Ilyakhov and Lyudmila Sarycheva. |
| [mnemaos](skills/mnemaos/) | EN | Interviews you and builds a personal memory for your AI: a local folder of Markdown files it reads at the start of a session and updates at the end. Can start from scratch or adopt an existing folder. Docs: [docs/mnemaos/](docs/mnemaos/). |
| [mnemaos-mcp](skills/mnemaos-mcp/README.md) | EN | Optional memory server for mnemaos. Serves the same memory folder to any MCP client, on your computer or on your own server. Python 3.9+, no dependencies. This is a server, not a skill: set it up by its [README](skills/mnemaos-mcp/README.md). |
| [thoughts-to-doc](skills/thoughts-to-doc/) | EN, talks in any language | Asks you questions one at a time until your idea becomes one plain brief that a person or an AI agent can act on. |

### Install a standalone skill

1. Clone the repository once:

   ```bash
   git clone https://github.com/sglibiciuc/skills.git
   ```

2. From the same folder, copy the skill folder into your assistant's skills folder. Replace `clear-writing` with the skill you need.

Claude Code:

```bash
mkdir -p ~/.claude/skills
cp -r skills/skills/clear-writing ~/.claude/skills/clear-writing
```

Codex:

```bash
mkdir -p ~/.agents/skills
cp -r skills/skills/clear-writing ~/.agents/skills/clear-writing
```

Start a new session after copying. More for Codex: [docs/README.codex.md](docs/README.codex.md). Gemini CLI and chats without skill support are covered only where a skill's own README says so, for example [skills/thoughts-to-doc/README.md](skills/thoughts-to-doc/README.md); standalone skills in Gemini CLI: [docs/README.gemini.md](docs/README.gemini.md).

## Bugs and ideas

If you find a bug or have an idea, open an [issue](https://github.com/sglibiciuc/skills/issues) or send a pull request. Rules for contributions: [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
