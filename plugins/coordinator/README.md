![Coordinator — from idea to a working product](../../assets/coordinator-cover.png)

# Координатор

[English below](#coordinator-english)

Плагин для Claude Code и Codex. Вы говорите с одним собеседником — Координатором. Он расспрашивает, чего вы хотите, договаривается с вами, как всё будет работать, и отдаёт работу команде помощников. На выходе — готовая вещь, которой можно пользоваться: автоматизация, навык, плагин, сайт, приложение.

## Что вы увидите

1. Координатор одной-двумя фразами скажет, как пойдёт работа.
2. Будет задавать вопросы по одному и к каждому предлагать ответ. Можно ответить «решай сам».
3. Покажет короткий документ «чего вы хотите», потом «как это будет работать». Вы согласуете каждый.
4. Покажет план списком и спросит, начинать ли.
5. Дальше собирает сам и после каждого готового куска пишет одну строку прогресса.
6. В конце — готовая вещь, инструкция и одно сообщение, как ей пользоваться.

Простую задачу Координатор предложит сделать сразу, без документов. Можно прийти с готовым описанием, попросить проверить или доработать то, что уже есть. Ваши файлы не правятся: работа идёт в копиях, рабочей копия становится только после вашего «да».

## Что нужно

- Claude Code или Codex в терминале.
- Python 3 на компьютере. На Mac он обычно уже есть. Проверить: в терминале набрать `python3 --version`.

## Установка в Claude Code

Команды набираются в терминале по одной.

1. Подключите каталог плагинов Саши:

   ```bash
   claude plugin marketplace add sglibiciuc/skills
   ```

   Ответ: `Successfully added marketplace: sglibiciuc`.

2. Установите Координатора:

   ```bash
   claude plugin install coordinator@sglibiciuc
   ```

   Ответ: `Successfully installed plugin: coordinator@sglibiciuc`.

3. Откройте терминал в папке, где хотите работать над своей задачей, и запустите `claude`.
4. Вызовите Координатора: наберите `/coordinator:coordinator` и через пробел напишите, что хотите получить, например: `/coordinator:coordinator хочу каждое утро получать сводку новых писем от клиентов`.

## Установка в Codex

Команды набираются в терминале по одной.

1. Подключите каталог плагинов Саши:

   ```bash
   codex plugin marketplace add sglibiciuc/skills
   ```

   Ответ: `Added marketplace sglibiciuc …`.

2. Установите Координатора:

   ```bash
   codex plugin add coordinator@sglibiciuc
   ```

   Ответ: `Added plugin coordinator from marketplace sglibiciuc.`

3. Откройте терминал в папке, где хотите работать над своей задачей, и запустите новый сеанс: `codex`. Плагин подхватывается только в новом сеансе.
4. Разрешите хуки Координатора. Это проверки, которые не дают ему закончить работу на полпути и возвращают его к задаче после перерыва. При первом запуске Codex покажет окно `Hooks need review`. Курсор в нём стоит на первом пункте: нажмите один раз стрелку вниз, чтобы выделился пункт `2. Trust all and continue`, и нажмите Enter.
5. Вызовите Координатора: наберите `@`, выберите в появившемся списке строку `coordinator (coordinator)` (стрелками вверх и вниз) и нажмите Enter. В поле ввода появится `$coordinator:coordinator`. Через пробел напишите, что хотите получить, например: «хочу каждое утро получать сводку новых писем от клиентов».

## Как продолжить в другой раз

Откройте терминал в той же папке, запустите Claude Code или Codex и напишите «продолжай». Повторять ничего не нужно.

## Как понять, что всё работает

- Claude Code: команда `claude plugin list` показывает `coordinator@sglibiciuc` со статусом `enabled`.
- Codex: команда `codex plugin list --marketplace sglibiciuc` показывает `coordinator@sglibiciuc` со статусом `installed, enabled`.

## Где лежат ваши материалы

Для каждой задачи Координатор создаёт отдельную папку: ответы на вопросы, согласованные документы, план, отчёты помощников и бэклог — список того, что можно сделать потом. То, что Координатор знает о вашей среде (подписка, доступные модели), он хранит в `~/.coordinator/environment.md`, чтобы не спрашивать заново.

---

# Coordinator (English)

A plugin for Claude Code and Codex. You talk to one partner, the Coordinator. It asks what you want, agrees with you how everything will work, and hands the work to a team of helpers. What you get is a finished thing you can use: an automation, a skill, a plugin, a website, an app.

## What you will see

1. The Coordinator tells you in a sentence or two how the work will go.
2. It asks questions one at a time and suggests an answer to each. You can reply "you decide".
3. It shows a short document "what you want", then "how it will work". You approve each one.
4. It shows the plan as a list and asks whether to start.
5. Then it builds on its own and writes one progress line after each finished piece.
6. At the end you get the finished thing, instructions and one message on how to use it.

For a simple task the Coordinator offers to do it right away, without documents. You can also come with a ready description, or ask to check or improve something you already have. Your files are never edited: the work happens in copies, and a copy becomes the working one only after your "yes".

## What you need

- Claude Code or Codex in the terminal.
- Python 3 on your computer. A Mac usually has it already. To check, type `python3 --version` in the terminal.

## Install in Claude Code

Type the commands in the terminal one at a time.

1. Connect Sasha's plugin catalog:

   ```bash
   claude plugin marketplace add sglibiciuc/skills
   ```

   Reply: `Successfully added marketplace: sglibiciuc`.

2. Install the Coordinator:

   ```bash
   claude plugin install coordinator@sglibiciuc
   ```

   Reply: `Successfully installed plugin: coordinator@sglibiciuc`.

3. Open the terminal in the folder where you want to work on your task and run `claude`.
4. Call the Coordinator: type `/coordinator:coordinator`, a space and what you want to get, for example: `/coordinator:coordinator every morning I want a summary of new emails from clients`.

## Install in Codex

Type the commands in the terminal one at a time.

1. Connect Sasha's plugin catalog:

   ```bash
   codex plugin marketplace add sglibiciuc/skills
   ```

   Reply: `Added marketplace sglibiciuc …`.

2. Install the Coordinator:

   ```bash
   codex plugin add coordinator@sglibiciuc
   ```

   Reply: `Added plugin coordinator from marketplace sglibiciuc.`

3. Open the terminal in the folder where you want to work on your task and start a new session: `codex`. The plugin is picked up only in a new session.
4. Allow the Coordinator's hooks. These are checks that keep it from stopping halfway and bring it back to the task after a break. On the first start Codex shows a `Hooks need review` window. The cursor starts on the first option: press the Down arrow key once so that `2. Trust all and continue` is highlighted, then press Enter.
5. Call the Coordinator: type `@`, pick the line `coordinator (coordinator)` in the list that appears (with the Up and Down arrow keys) and press Enter. The input then shows `$coordinator:coordinator`. After a space, write what you want to get, for example: "every morning I want a summary of new emails from clients".

## How to continue another time

Open the terminal in the same folder, start Claude Code or Codex and write "continue". You don't need to repeat anything.

## How to know it works

- Claude Code: `claude plugin list` shows `coordinator@sglibiciuc` as `enabled`.
- Codex: `codex plugin list --marketplace sglibiciuc` shows `coordinator@sglibiciuc` as `installed, enabled`.

## Where your materials live

For each task the Coordinator creates its own folder: your answers, the agreed documents, the plan, the helpers' reports and the backlog, a list of what can be done later. What the Coordinator knows about your environment (subscription, available models) it keeps in `~/.coordinator/environment.md`, so it does not ask again.
