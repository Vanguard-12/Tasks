from __future__ import annotations

import json
import re
from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM

# ---------------------------------------------------------------------------
# 1. Состояние
# ---------------------------------------------------------------------------

class PlanningState(TypedDict):
    task: str
    plan: List[str] | None
    current_step: int
    results: List[str]

# ---------------------------------------------------------------------------
# 2. LLM‑инстанс (используем Ollama, модель по умолчанию llama3)
# ---------------------------------------------------------------------------

_llm = OllamaLLM(model="llama3")  # при необходимости замените модель

# ---------------------------------------------------------------------------
# 3. Вспомогательная функция парсинга плана
# ---------------------------------------------------------------------------

def _parse_plan(text: str) -> List[str]:
    """Пытается распарсить план из JSON или нумерованного списка.

    При неудаче возвращает пустой список.
    """
    # Попытка JSON
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "plan" in data:
            plan = data["plan"]
            if isinstance(plan, list):
                return [str(item).strip() for item in plan]
    except json.JSONDecodeError:
        pass

    # Поиск нумерованного списка (1., 2) ...
    lines = text.splitlines()
    plan_items: List[str] = []
    for line in lines:
        match = re.match(r"\s*\d+[\.\)]\s*(.+)", line)
        if match:
            plan_items.append(match.group(1).strip())
    return plan_items

# ---------------------------------------------------------------------------
# 4. Узел планирования
# ---------------------------------------------------------------------------

def planning(state: PlanningState) -> PlanningState:
    """LLM‑узел, который генерирует план из 3‑6 шагов.

    Ожидает, что поле ``task`` уже заполнено.
    """
    task = state["task"]
    prompt = (
        f"Разбей задачу на 3‑6 конкретных шагов и верни их в виде JSON. "
        f"Ответ должен иметь форму {{\"plan\": [\"шаг 1\", \"шаг 2\", ...]}}.\n"
        f"Задача: {task}"
    )
    raw = _llm.invoke(prompt)
    plan = _parse_plan(raw)
    if not plan:
        # fallback – попытка разбора как обычного нумерованного списка
        raw_alt = _llm.invoke(
            f"Представь план задачи в виде нумерованного списка (например, 1. Шаг 1, 2. Шаг 2).\nЗадача: {task}"
        )
        plan = _parse_plan(raw_alt)
    # гарантируем минимум 3 шага, иначе используем простую заглушку
    if len(plan) < 3:
        plan = [f"Шаг {i+1}" for i in range(3)]
    return {"plan": plan, "current_step": 0, "results": []}

# ---------------------------------------------------------------------------
# 5. Узел исполнения одного шага
# ---------------------------------------------------------------------------

def execution(state: PlanningState) -> PlanningState:
    """Выполняет один шаг из ``plan`` и сохраняет результат."""
    idx = state["current_step"]
    step_instruction = state["plan"][idx]
    prompt = (
        f"Выполни следующий шаг и дай краткий ответ.\nШаг: {step_instruction}\n"
    )
    result = _llm.invoke(prompt)
    new_results = state["results"] + [result]
    return {"results": new_results, "current_step": idx + 1}

# ---------------------------------------------------------------------------
# 6. Условие продолжения
# ---------------------------------------------------------------------------

def should_continue(state: PlanningState) -> str:
    """Определяет, есть ли ещё шаги для выполнения.

    Возвращаемые варианты:
    - "execute" – есть ещё шаги, переходим к узлу ``execution``;
    - "finish" – план завершён.
    """
    if state["current_step"] >= len(state["plan"]):
        return "finish"
    return "execute"

# ---------------------------------------------------------------------------
# 6b. Узел‑обёртка для условия (возвращает состояние без изменений)
# ---------------------------------------------------------------------------

def should_continue_node(state: PlanningState) -> PlanningState:
    """Промежуточный узел, необходимый для conditional_edges.
    Он просто передаёт состояние дальше, а функция ``should_continue``
    решает, какой путь выбрать.
    """
    return state

# ---------------------------------------------------------------------------
# 7. Финальный узел (может просто вернуть состояние)
# ---------------------------------------------------------------------------

def finish(state: PlanningState) -> PlanningState:
    """Финальный узел – ничего не делает, просто передаёт состояние дальше."""
    return state

# ---------------------------------------------------------------------------
# 8. Сборка графа
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    graph = StateGraph(PlanningState)
    graph.add_node("planning", planning)
    graph.add_node("execution", execution)
    graph.add_node("should_continue", should_continue_node)
    graph.add_node("finish", finish)

    # Соединяем узлы
    graph.add_edge("planning", "execution")
    graph.add_edge("execution", "should_continue")
    graph.add_conditional_edges(
        "should_continue",
        should_continue,
        {
            "execute": "execution",
            "finish": "finish",
        },
    )
    graph.add_edge("finish", END)
    graph.set_entry_point("planning")
    return graph.compile()

# ---------------------------------------------------------------------------
# 9. Точка входа и демонстрация
# ---------------------------------------------------------------------------

def main() -> None:
    demo_task = "Сравни Python и JavaScript"
    initial_state: PlanningState = {
        "task": demo_task,
        "plan": None,
        "current_step": 0,
        "results": [],
    }

    graph = build_graph()
    final_state = graph.invoke(initial_state)

    # Вывод плана и шагов
    print(f"Задача: {demo_task}\n")
    print("План:")
    for i, step in enumerate(final_state["plan"], start=1):
        print(f"{i}. {step}")
    print()
    for i, res in enumerate(final_state["results"], start=1):
        print(f"[Шаг {i}] {res}")
    print()

    # Финальное резюме – собираем все результаты и просим LLM подытожить
    summary_prompt = (
        "Суммируй результаты ниже в короткий вывод.\n\n"
        + "\n".join(final_state["results"]) 
        + "\n\nИтог:" 
    )
    summary = _llm.invoke(summary_prompt)
    print(f"Итоговый вывод: {summary}")

if __name__ == "__main__":
    main()
