# Самокорректирующийся агент (LangGraph)

## Описание

Этот проект демонстрирует простого агента, построенного на **LangGraph**, который:

1. Выполняет задачу через «ненадёжный» инструмент.
2. Автоматически проверяет результат с помощью LLM‑judge (OpenAI).
3. При неудачной проверке повторяет попытку до достижения `max_attempts`.

## Установка

```bash
# Клонирование репозитория
git clone <repo-url>
cd <repo-dir>

# Создаём виртуальное окружение и активируем его
python -m venv .venv
source .venv/bin/activate   # Windows: .\\venv\\Scripts\\activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env` на основе `.env.example` и укажите ваш **OpenAI API key**:

```dotenv
OPENAI_API_KEY=sk-...
```

## Запуск

```bash
python -m src.main "Вычисли 2+2"
```

Пример вывода (может отличаться из‑за случайных ошибок инструмента):

```
Задача: Вычисли 2+2
Попытка 1: Error(ValueError('Tool failed')) → verify: failed
Попытка 2: результат 4 → verify: success
Итог: success за 2 попытки
```

## Структура проекта

- `src/agent_state.py` – определение состояния графа (`AgentState`).
- `src/tools.py` – ненадёжный инструмент `unreliable_tool`.
- `src/nodes.py` – функции‑узлы графа (`execute_task`, `verify_result`, `handle_error`).
- `src/graph.py` – построение `StateGraph` с циклом повторов.
- `src/main.py` – CLI‑обёртка, запускающая граф и выводящая прогресс.

## Лицензия

MIT License