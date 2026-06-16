import os
import json
from typing import TypedDict, List, Any, Literal

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# ---------------------------------------------------------------------------
# Load environment variables (API keys, Ollama URL, etc.)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# 1. Состояние
# ---------------------------------------------------------------------------
class PlanningState(TypedDict):
    """State used by the LangGraph planning agent."""

    task: str
    plan: List[str] | None
    current_step: int
    results: List[str]

# ---------------------------------------------------------------------------
# 2. LLM‑клиент
# ---------------------------------------------------------------------------
# При наличии переменной OLLAMA_BASE_URL будем использовать Ollama, иначе – OpenAI.
if os.getenv("OLLAMA_BASE_URL"):
    # Ollama использует тот же API‑интерфейс, что и OpenAI, поэтому можно задать
    # базовый URL через параметр `base_url`.
    llm = ChatOpenAI(
        model="llama3.1",
        temperature=0.0,
        base_url=os.getenv("OLLAMA_BASE_URL"),
        api_key="ollama",  # dummy, Ollama не требует ключа
    )
else:
    # Ожидаем, что пользователь задаст OPENAI_API_KEY в окружении.
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

# ---------------------------------------------------------------------------
# 3. Узел планирования
# ---------------------------------------------------------------------------
def planning(state: PlanningState) -> PlanningState:
    """Ask the LLM to split the task into 3‑6 concrete steps.

    The LLM is asked to return a JSON array of strings for reliable parsing.
    """
    task = state["task"]
    prompt = (
        f"You are a helpful assistant. Split the following task into a list of 3‑6 concrete steps. "
        f"Return ONLY a JSON array of strings.\nTask: {task}"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()
    try:
        plan = json.loads(raw)
        if not isinstance(plan, list) or not all(isinstance(i, str) for i in plan):
            raise ValueError
    except Exception:
        # Fallback: try to parse a numbered list like "1. step".
        plan = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            # Remove leading numbers and punctuation.
            if line[0].isdigit():
                # Find first dot or parenthesis after the number.
                sep_idx = line.find('.')
                if sep_idx == -1:
                    sep_idx = line.find(')')
                if sep_idx != -1:
                    line = line[sep_idx + 1 :].strip()
            plan.append(line)
        if not plan:
            raise RuntimeError("Failed to parse plan from LLM response.")

    # Initialise the rest of the state.
    state["plan"] = plan
    state["current_step"] = 0
    state["results"] = []

    # Выводим план для пользователя.
    print("\nПлан:")
    for idx, step in enumerate(plan, 1):
        print(f"{idx}. {step}")
    return state

# ---------------------------------------------------------------------------
# 4. Узел выполнения одного шага
# ---------------------------------------------------------------------------
def execution(state: PlanningState) -> PlanningState:
    """Execute a single step from the plan and store the result."""
    plan = state["plan"]
    idx = state["current_step"]
    if plan is None or idx >= len(plan):
        raise RuntimeError("Execution called with invalid step index.")

    step_description = plan[idx]
    prompt = (
        f"You are executing the following step as part of a larger task. "
        f"Provide a concise answer that fulfills the step.\nStep: {step_description}"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    result = response.content.strip()

    # Сохраняем результат и увеличиваем счётчик.
    state["results"].append(result)
    state["current_step"] = idx + 1

    print(f"\n[Шаг {idx + 1}] {result}")
    return state

# ---------------------------------------------------------------------------
# 5. Условный переход – продолжаем ли выполнять шаги?
# ---------------------------------------------------------------------------
def should_continue(state: PlanningState) -> Literal["execute", "finish"]:
    plan = state["plan"]
    if plan is None:
        raise RuntimeError("Plan is not initialized.")
    return "finish" if state["current_step"] >= len(plan) else "execute"

# ---------------------------------------------------------------------------
# 6. Финальный узел – суммируем результаты
# ---------------------------------------------------------------------------
def finish(state: PlanningState) -> PlanningState:
    """Generate a final summary from all step results."""
    if not state["results"]:
        summary = "No results were generated."
    else:
        joined = "\n\n".join(state["results"])
        prompt = (
            "You are given the results of several steps that together answer a task. "
            "Summarize them into a concise final answer.\n\nResults:\n"
            f"{joined}\n\nFinal answer:"
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        summary = response.content.strip()

    print("\nИтог: " + summary)
    return state

# ---------------------------------------------------------------------------
# 7. Сборка графа
# ---------------------------------------------------------------------------
def build_graph() -> StateGraph:
    graph = StateGraph(PlanningState)
    graph.add_node("planning", planning)
    graph.add_node("execution", execution)
    graph.add_node("finish", finish)

    graph.add_edge(START, "planning")
    graph.add_edge("planning", "execution")
    graph.add_conditional_edges(
        "execution",
        should_continue,
        {"execute": "execution", "finish": "finish"},
    )
    graph.add_edge("finish", END)
    return graph.compile()

# ---------------------------------------------------------------------------
# 8. Точка входа – демонстрация работы агента
# ---------------------------------------------------------------------------
def main() -> None:
    default_task = os.getenv("DEFAULT_TASK", "Сравни Python и JavaScript")
    print(f"Задача: {default_task}\n")

    graph = build_graph()
    # Начальное состояние содержит только задачу; остальные поля будут заполнены узлом planning.
    initial_state: PlanningState = {
        "task": default_task,
        "plan": None,
        "current_step": 0,
        "results": [],
    }
    graph.invoke(initial_state)


if __name__ == "__main__":
    main()
