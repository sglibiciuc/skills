# Standalone skills in Gemini CLI

This page covers only the standalone skills in `skills/<skill-name>/SKILL.md`. The Coordinator plugin supports Claude Code and Codex only and does not run in Gemini CLI.

Each skill states in its own README whether it works in Gemini CLI. Today one skill does: [thoughts-to-doc](../skills/thoughts-to-doc/README.md). `skills/mnemaos-mcp/` is a server with no `SKILL.md`, set up by its [README](../skills/mnemaos-mcp/README.md).

## Install thoughts-to-doc

1. Clone the repository:

   ```bash
   git clone https://github.com/sglibiciuc/skills.git
   ```

2. From the same folder, copy the skill into `.gemini/skills/` inside your project, or into `~/.gemini/skills/` to have it everywhere:

   ```bash
   mkdir -p ~/.gemini/skills
   cp -r skills/skills/thoughts-to-doc ~/.gemini/skills/thoughts-to-doc
   ```

   The skill's README also gives `gemini skills install <repo-url>`. The skill sits in a subfolder of this repository, so add `--path skills/thoughts-to-doc`.

3. Gemini CLI asks you to allow the skill the first time it starts.

4. Gemini CLI starts skills from what you ask, not by name. Say what you need, for example "help me explain what I want".

Details: [skills/thoughts-to-doc/README.md](../skills/thoughts-to-doc/README.md).
