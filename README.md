# Самокорректирующийся агент (LangGraph)

## Описание

Этот проект демонстрирует **LangGraph‑агента**, который выполняет задачу, проверяет результат с помощью LLM (LLM‑as‑judge) и при неудаче повторяет попытку до тех пор, пока не получит `success` или не исчерпает `max_attempts`.

## Стек

- Python 3.10+
- `langgraph`
- `langchain-openai` **или** `langchain-ollama`

## Установка

```bash
# создайте и активируйте виртуальное окружение (по желанию)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# установить зависимости
pip install -r requirements.txt
```

> **Важно:** Для работы `langchain-openai` нужен API‑ключ OpenAI (переменная окружения `OPENAI_API_KEY`).
> Если ключа нет, агент автоматически переключится на локальный Ollama (модель `llama3` по умолчанию).

## Запуск

```bash
python src/main.py
```

Или через модульный запуск:

```bash
python -m src.main
```

## Ожидаемый вывод

```text
Задача: Выполни 2+2
Попытка 1: Error → simulated failure
verify: failed
Попытка 2: result 4
verify: success
Итог: success за 2 попытки
```

Если все попытки закончились неудачей:

```text
Итог: max_attempts reached after 5 попыток
```

## Структура проекта

- `src/agent.py` – определение `AgentState`, узлы графа и функция `build_agent_graph()`.
- `src/tools.py` – тестовый инструмент `unreliable_tool` с ~30 % вероятностью бросить `ValueError`.
- `src/main.py` – CLI‑точка входа, запускает граф и выводит информацию о каждой попытке.
- `requirements.txt` – список зависимостей.
- `README.md` – текущий файл.

## Как работает

1. **execute_task** – вызывает `unreliable_tool`. При успехе сохраняет результат, при ошибке записывает сообщение об ошибке.
2. **verify_result** – отправляет задачу и полученный результат в LLM и просит вернуть только слово `success` или `failed`.
3. **handle_error** – увеличивает счётчик `attempts`, при достижении `max_attempts` переводит статус в `max_attempts`, иначе готовит повтор.
4. Граф построен с помощью `StateGraph` и содержит цикл, описанный в условии задания.

## Лицензия

MIT License
