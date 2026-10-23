# sglibiciuc/skills for Codex

This repository is a plugin marketplace named `sglibiciuc`. Codex installs plugins from it with `codex plugin`. Standalone skills from `skills/` are installed by copying their folder.

## Coordinator plugin

You need Codex and Python 3 (check with `python3 --version`). Run the commands in the terminal one at a time.

1. Add the marketplace:

   ```bash
   codex plugin marketplace add sglibiciuc/skills
   ```

2. Install the plugin:

   ```bash
   codex plugin add coordinator@sglibiciuc
   ```

3. Check: `codex plugin list --marketplace sglibiciuc` shows `coordinator@sglibiciuc` with status `installed, enabled`.

4. Open the terminal in the folder where you want to work on your task and start a new session with `codex`. The plugin loads only in a new session.

5. Allow the plugin's hooks. On the first start Codex shows a `Hooks need review` window with the cursor on the first option. Press the Down arrow once to highlight `2. Trust all and continue`, then press Enter. The hooks keep the Coordinator from stopping halfway and bring it back to the task after a break.

6. Call the Coordinator: type `@`, pick `coordinator (coordinator)` in the list and press Enter. The input shows `$coordinator:coordinator`. After a space, write what you want to get.

To continue a task later, start `codex` in the same folder and write "continue". Full guide: [plugins/coordinator/README.md](../plugins/coordinator/README.md).

## Standalone skills

Each skill in `skills/<skill-name>/` is a folder with a `SKILL.md` file. `skills/mnemaos-mcp/` is an exception: it is a server with no `SKILL.md`, set up by its [README](../skills/mnemaos-mcp/README.md).

1. Clone the repository:

   ```bash
   git clone https://github.com/sglibiciuc/skills.git
   ```

2. From the same folder, copy the skill into `~/.agents/skills/` to have it in every project, or into `.agents/skills/` inside one repository. Replace `thoughts-to-doc` with the skill you need:

   ```bash
   mkdir -p ~/.agents/skills
   cp -r skills/skills/thoughts-to-doc ~/.agents/skills/thoughts-to-doc
   ```

3. Start a new `codex` session. Call the skill by name with `$`, for example `$thoughts-to-doc`, or pick it from `/skills`.

Without copying, you can also point Codex at a skill file from your `AGENTS.md`. Use the path to your clone:

```
Follow the instructions in <path-to-clone>/skills/<skill-name>/SKILL.md
```
