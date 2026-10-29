---
description: "should not trigger the writer skill"
tags: [trigger, should-not]
runs: 1
max_turns: 4
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---
Привет! Вот ошибка из pytest: AssertionError: expected 3, got 2 в test_parse_rows. Функция parse_rows пропускает последнюю строку файла. Что поправить в цикле?
