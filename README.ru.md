[English](README.md) | [Русский](README.ru.md)

![Build More Possibilities: коллекция практичных инструментов для людей и ИИ](assets/repo-cover.jpg)

# sglibiciuc/skills

Открытые плагины и навыки Саши Глибичука для ИИ-ассистентов. Репозиторий заодно служит каталогом плагинов (marketplace) с именем `sglibiciuc`.

## Плагины

| Плагин | Что делает |
|--------|------------|
| [Координатор](plugins/coordinator/README.md) | Для Claude Code и Codex. Вы договариваетесь с одним агентом, что нужно и как это будет работать. Потом команда агентов собирает и проверяет результат, и вы получаете работающую вещь. |

## Навыки

| Навык | Язык | Что делает |
|-------|------|------------|
| [autonomous-loop-onboarding](skills/autonomous-loop-onboarding/) | EN | Настраивает автономный цикл задач: вы ставите задачу, ИИ-агент её выполняет, сам проверяет и отдаёт вам на одобрение. |
| [clear-writing](skills/clear-writing/) | RU | Пишет, правит и проверяет деловые письма и сообщения по методу Максима Ильяхова и Людмилы Сарычевой. |
| [mnemaos](skills/mnemaos/) | EN | Собирает личную память для ИИ: папку с Markdown-файлами на вашем компьютере. Описание: [docs/mnemaos/](docs/mnemaos/). |
| [mnemaos-mcp](skills/mnemaos-mcp/README.md) | EN | Дополнительный сервер памяти для mnemaos, отдаёт папку памяти любому MCP-клиенту. Это сервер, а не навык. |
| [thoughts-to-doc](skills/thoughts-to-doc/) | EN, говорит на любом языке | Задаёт вопросы по одному, пока ваша мысль не сложится в один простой документ, по которому человек или ИИ-агент сможет действовать. |

## Установка

### Плагины

Один раз подключите каталог.

Claude Code:

```bash
claude plugin marketplace add sglibiciuc/skills
```

Codex:

```bash
codex plugin marketplace add sglibiciuc/skills
```

Дальше ставьте плагин по шагам из его README.

### Отдельные навыки

1. Один раз скачайте репозиторий:

   ```bash
   git clone https://github.com/sglibiciuc/skills.git
   ```

2. Из той же папки скопируйте папку навыка туда, где ваш ассистент ищет навыки. Вместо `clear-writing` подставьте нужный навык.

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

После копирования начните новый сеанс. Если у навыка есть свой README, там могут быть и другие способы установки. Подробнее про Codex: [docs/README.codex.md](docs/README.codex.md). Про Gemini CLI: [docs/README.gemini.md](docs/README.gemini.md).

## Ошибки и идеи

Если нашли ошибку или знаете, как сделать лучше, откройте [issue](https://github.com/sglibiciuc/skills/issues) или пришлите pull request. Правила для участников: [CONTRIBUTING.md](CONTRIBUTING.md).

## Лицензия

MIT. Текст лицензии: [LICENSE](LICENSE).
