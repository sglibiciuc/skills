[English](README.md) | [Русский](README.ru.md)

![Build More Possibilities: коллекция практичных инструментов для людей и ИИ](assets/repo-cover.jpg)

# sglibiciuc/skills

Открытые плагины и навыки Саши Глибичука для Claude Code и Codex. Репозиторий заодно служит каталогом плагинов (marketplace) с именем `sglibiciuc`.

## Установка

### Claude Code

В терминале:

```bash
claude plugin marketplace add sglibiciuc/skills
claude plugin install coordinator@sglibiciuc
```

### Codex

В терминале:

```bash
codex plugin marketplace add sglibiciuc/skills
codex plugin add coordinator@sglibiciuc
```

Подробные шаги, в том числе как разрешить хуки плагина в Codex, есть в [README Координатора](plugins/coordinator/README.md).

### Отдельные навыки

Скачайте или склонируйте репозиторий и положите папку навыка, например `skills/thoughts-to-doc/`, туда, где ваш инструмент ищет навыки.

**Claude Code**: скопируйте папку в `.claude/skills/` своего проекта или в `~/.claude/skills/`, чтобы навык был доступен везде. Начните новую сессию.

**Codex**: скопируйте папку в `.agents/skills/` своего репозитория или в `~/.agents/skills/`, чтобы навык был доступен везде.

Если у навыка есть свой README, там могут быть другие инструменты и другие способы установки.

## Справочник

### Плагины

- **[Writer](plugins/writer/README.ru.md)**: пишет и редактирует рабочие тексты, уточняет, что вы хотите сказать и пообещать, проверяет черновики на признаки ИИ и запоминает ваш стиль с вашего разрешения.
- **[Координатор](plugins/coordinator/README.md)**: вы договариваетесь с одним агентом в Claude Code или Codex, что нужно и как это будет работать, потом команда агентов собирает и проверяет результат, и вы получаете работающую вещь.

### Навыки

- **[autonomous-loop-onboarding](skills/autonomous-loop-onboarding/)**: настраивает автономный цикл задач, где вы ставите задачу, ИИ-агент её выполняет, сам проверяет и отдаёт вам на одобрение. На английском.
- **[clear-writing](skills/clear-writing/)**: пишет, правит и проверяет деловые письма и сообщения на русском по методу Максима Ильяхова и Людмилы Сарычевой.
- **[mnemaos](skills/mnemaos/)**: собирает личную память для ИИ в виде папки с Markdown-файлами на вашем компьютере, по желанию с сервером памяти по MCP. На английском.
- **[thoughts-to-doc](skills/thoughts-to-doc/)**: задаёт вопросы по одному, пока ваша мысль не сложится в один простой документ, по которому человек или ИИ-агент сможет действовать. На английском, общается на любом языке.

## Ошибки и идеи

Если нашли ошибку или знаете, как сделать лучше, откройте [issue](https://github.com/sglibiciuc/skills/issues) или пришлите pull request. Правила для участников: [CONTRIBUTING.md](CONTRIBUTING.md).

## Лицензия

MIT. Текст лицензии: [LICENSE](LICENSE).
