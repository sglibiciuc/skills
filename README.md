[English](README.md) | [Русский](README.ru.md)

![Build More Possibilities — a collection of practical tools for people and AI](assets/repo-cover.jpg)

# sglibiciuc/skills

Sasha Glibiciuc's open-source plugins and skills for AI assistants. The repository is also a plugin marketplace named `sglibiciuc`.

## Plugins

| Plugin | What it does |
|--------|--------------|
| [Coordinator](plugins/coordinator/README.md) | For Claude Code and Codex. You agree with one agent on what you want and how it will work, then a team of role agents builds and checks it, and you get a working product. |

## Skills

| Skill | Language | What it does |
|-------|----------|--------------|
| [autonomous-loop-onboarding](skills/autonomous-loop-onboarding/) | EN | Sets up an autonomous task loop: you queue a task, an AI agent does it, checks its work and hands it back for your approval. |
| [clear-writing](skills/clear-writing/) | RU | Writes, edits and reviews business emails and messages using the method of Maxim Ilyakhov and Lyudmila Sarycheva. |
| [mnemaos](skills/mnemaos/) | EN | Builds a personal memory for your AI: a local folder of Markdown files. About it: [docs/mnemaos/](docs/mnemaos/). |
| [mnemaos-mcp](skills/mnemaos-mcp/README.md) | EN | Optional memory server for mnemaos that serves the memory folder to any MCP client. It is a server, not a skill. |
| [thoughts-to-doc](skills/thoughts-to-doc/) | EN, talks in any language | Asks questions one at a time until your idea becomes one plain brief that a person or an AI agent can act on. |

## Install

### Plugins

Add the marketplace once.

Claude Code:

```bash
claude plugin marketplace add sglibiciuc/skills
```

Codex:

```bash
codex plugin marketplace add sglibiciuc/skills
```

Then install the plugin by the steps in its README.

### Standalone skills

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

Start a new session after copying. A skill's own README may give other ways to install it. More for Codex: [docs/README.codex.md](docs/README.codex.md). Gemini CLI: [docs/README.gemini.md](docs/README.gemini.md).

## Bugs and ideas

If you find a bug or have an idea, open an [issue](https://github.com/sglibiciuc/skills/issues) or send a pull request. Rules for contributions: [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
