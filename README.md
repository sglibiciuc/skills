[English](README.md) | [Русский](README.ru.md)

![Build More Possibilities — a collection of practical tools for people and AI](assets/repo-cover.jpg)

# sglibiciuc/skills

Sasha Glibiciuc's open-source plugins and skills for Claude Code and Codex. The repository is also a plugin marketplace named `sglibiciuc`.

## Installation

### Claude Code

In a terminal:

```bash
claude plugin marketplace add sglibiciuc/skills
claude plugin install coordinator@sglibiciuc
```

### Codex

In a terminal:

```bash
codex plugin marketplace add sglibiciuc/skills
codex plugin add coordinator@sglibiciuc
```

Full steps, including how to allow the plugin's hooks in Codex, are in the [Coordinator README](plugins/coordinator/README.md).

### Standalone skills

Download or clone this repository, then put the skill folder, for example `skills/thoughts-to-doc/`, where your tool looks for skills.

**Claude Code**: copy the folder into `.claude/skills/` in your project, or into `~/.claude/skills/` to have it everywhere. Start a new session.

**Codex**: copy the folder into `.agents/skills/` in your repository, or into `~/.agents/skills/` to have it everywhere.

If a skill has its own README, it may list other tools and other ways to install it.

## Reference

### Plugins

- **[Writer](plugins/writer/README.md)**: writes and edits work texts, checks what you want to say and promise, analyzes drafts for AI tells, and remembers your style with your permission.
- **[Coordinator](plugins/coordinator/README.md)**: you agree with one agent in Claude Code or Codex on what you want and how it will work, then a team of role agents builds and checks it, and you get a working product.

### Skills

- **[autonomous-loop-onboarding](skills/autonomous-loop-onboarding/)**: sets up an autonomous task loop where you queue a task, an AI agent does it, checks its work and hands it back for your approval. In English.
- **[clear-writing](skills/clear-writing/)**: writes, edits and reviews business emails and messages in Russian using the method of Maxim Ilyakhov and Lyudmila Sarycheva.
- **[mnemaos](skills/mnemaos/)**: builds a personal memory for your AI as a local folder of Markdown files, with an optional memory server over MCP. In English.
- **[thoughts-to-doc](skills/thoughts-to-doc/)**: asks questions one at a time until your idea becomes one plain brief that a person or an AI agent can act on. In English, talks in any language.

## Bugs and ideas

If you find a bug or have an idea, open an [issue](https://github.com/sglibiciuc/skills/issues) or send a pull request. Rules for contributions: [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
