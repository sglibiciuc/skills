# Contributing

Thank you for your interest in contributing to sglibiciuc/skills!

## Plugins

Plugins in this marketplace support Claude Code and Codex. Each plugin lives in `plugins/your-plugin-name/`, laid out like `plugins/coordinator/`:

```
your-plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Claude Code manifest (required)
├── .codex-plugin/
│   └── plugin.json      # Codex manifest (required for Codex)
├── README.md            # Documentation (required)
├── skills/              # Skills (SKILL.md files)
│   └── your-skill/
│       └── SKILL.md
├── agents/              # Agent definitions (optional)
│   └── your-agent.md
└── hooks/               # Hooks (optional)
    └── hooks.json
```

### .claude-plugin/plugin.json

```json
{
  "name": "your-plugin-name",
  "displayName": "Your Plugin Name",
  "version": "1.0.0",
  "description": "Brief description",
  "author": {
    "name": "Your Name"
  },
  "keywords": ["your-keyword"]
}
```

Claude Code finds `skills/`, `agents/` and `hooks/hooks.json` in their default places, so the manifest does not list them.

### .codex-plugin/plugin.json

```json
{
  "name": "your-plugin-name",
  "version": "1.0.0",
  "description": "Brief description",
  "author": {
    "name": "Your Name"
  },
  "keywords": ["your-keyword"],
  "skills": "./skills/",
  "interface": {
    "displayName": "Your Plugin Name",
    "shortDescription": "One line for the plugin list",
    "longDescription": "Brief description",
    "developerName": "Your Name",
    "category": "Productivity",
    "capabilities": ["Interactive", "Write"]
  }
}
```

Keep `name`, `version` and `description` the same in both manifests and in the plugin's entry in `.claude-plugin/marketplace.json`. Check the plugin with `claude plugin validate plugins/your-plugin-name --strict`.

## Standalone Skills

Skills that don't need a full plugin live in `skills/your-skill-name/`:

```
your-skill-name/
├── SKILL.md             # Skill definition with YAML frontmatter (required)
└── references/          # Supporting materials (optional)
    └── topic.md
```

Exception: `skills/mnemaos-mcp/` is an MCP server, not a skill. It has no `SKILL.md` and is documented by its own `README.md`.

### SKILL.md frontmatter

```yaml
---
name: your-skill-name
description: "Brief description of what the skill does and when to activate it"
allowed-tools: Read, Grep, Glob
---
```

## Guidelines

1. **One plugin per folder** in `plugins/`, one skill per folder in `skills/`
2. **Register plugins** in `.claude-plugin/marketplace.json`
3. **Include a README** for plugins; skills are self-documented via SKILL.md (a skill may add its own README)
4. **Name supported tools per skill**: if a standalone skill works in Gemini CLI or another tool, say so and how to install it in the skill's own README or SKILL.md
5. **MIT license** for all contributions
6. **No secrets or API keys** in the repository
7. **Languages**: English for code and docs. The root README exists in English (`README.md`) and Russian (`README.ru.md`): change both together and keep the same facts. Skill content may be in other languages

## Submitting

1. Fork this repository
2. Create your plugin in `plugins/your-plugin-name/` or skill in `skills/your-skill-name/`
3. For plugins: add entry to `.claude-plugin/marketplace.json`
4. Submit a pull request

We review PRs for quality, security, and usefulness.
