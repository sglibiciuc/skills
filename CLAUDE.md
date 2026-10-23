# CLAUDE.md — sglibiciuc/skills

## 1. About
Public open-source plugins and skills. Plugins support Claude Code and Codex. Each standalone skill states its supported tools (for example Gemini CLI) in its own README or SKILL.md.

## 2. Stack
- Format: Claude Code and Codex plugin system (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `skills/*/SKILL.md`, `agents/*.md`, `hooks/`)
- Hosting: GitHub (sglibiciuc/skills, public)
- License: MIT

## 3. Structure
- `plugins/` — full plugins (manifests in `.claude-plugin/` and `.codex-plugin/`, plus skills/agents/hooks)
- `skills/` — standalone skills (SKILL.md + optional references/)

## 4. Rules
- README.md in English and README.ru.md in Russian; keep the same facts in both
- English for code, CONTRIBUTING and `docs/` (`docs/mnemaos/` keeps its Russian twins)
- Skill content may be in the language of its target audience
- No proprietary business context
- No API keys or secrets
- Each plugin registered in `.claude-plugin/marketplace.json`
- README.md required for each plugin; SKILL.md required for each skill. Exception: `skills/mnemaos-mcp/` is an MCP server documented by its own README.md, with no SKILL.md
