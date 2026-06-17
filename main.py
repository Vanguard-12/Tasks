from __future__ import annotations
"""Human‑in‑the‑Loop demo using LangChain's HumanInTheLoopMiddleware.

The script creates a simple agent with a dummy ``get_weather`` tool, wraps it with
``HumanInTheLoopMiddleware`` (interrupt_on the tool) and a ``MemorySaver``
checkpointer. When the agent wants to call the tool it pauses, the script prints
the pending action(s) and asks the user to *approve* (``a``) or *reject* (``r``).
The decision(s) are sent back to the agent via ``Command(resume={"decisions": ...})``.
The loop continues until the agent finishes and returns the final assistant
message, which is printed to the console.

Run the script with a query as a command‑line argument or, if omitted, you will
be prompted for one::

    python main.py "Какая погода в Казани сегодня?"
"""


import json
import sys
from typing import Any, Dict, List

# LangChain & LangGraph imports -------------------------------------------------
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from langchain.chat_models import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# -----------------------------------------------------------------------------
# Dummy tool – in a real scenario this would call an external API.
# The tool must accept a ``city`` and ``date`` argument and return a string.
# -----------------------------------------------------------------------------

def get_weather(city: str, date: str) -> str:
    """Return a fake weather description.

    This placeholder is sufficient for the HumanInTheLoop demonstration – the
    actual content is not important, only that the tool exists and can be called
    by the agent.
    """
    return f"Погода в {city} на {date}: солнечно, 20°C."

# -----------------------------------------------------------------------------
# Helper to build the LangChain agent with the required middleware and checkpointer.
# -----------------------------------------------------------------------------

def build_agent() -> Any:
    """Create an agent that uses HumanInTheLoopMiddleware.

    * ``interrupt_on`` – tells the middleware to pause before executing the
      ``get_weather`` tool.
    * ``MemorySaver`` – stores the thread state so that the pause can be
      resumed.
    """
    # LLM – you need an OpenAI API key in the environment for this to work.
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    # Memory checkpoint – required for the middleware to keep the pause.
    memory = MemorySaver()

    # Build the agent.
    agent = create_agent(
        model=llm,
        tools=[get_weather],
        system_prompt="Ты полезный ассистент",
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={"get_weather": True},
                description_prefix="Подтвердите вызов инструмента",
            )
        ],
        checkpointer=memory,
    )
    return agent

# -----------------------------------------------------------------------------
# Core interaction loop – handles __interrupt__ payloads and resumes execution.
# -----------------------------------------------------------------------------

def run_interaction(user_query: str) -> None:
    """Run a single user query through the agent with HITL handling.

    The function:
    1. Sends the initial message to the agent.
    2. While the result contains ``'__interrupt__'`` it extracts the pending
       ``action_requests`` and prints them.
    3. For each request it asks the user to approve (``a``) or reject (``r``).
       If rejected, a free‑form reason is collected and sent back to the model.
    4. The decisions are sent back via ``Command(resume={"decisions": ...})``.
    5. When the agent finishes, the final assistant message is printed.
    """
    agent = build_agent()

    # Every invoke must contain a ``config`` with a unique thread_id so that the
    # MemorySaver can store the state between pauses.
    thread_id = "session-1"
    config = {"configurable": {"thread_id": thread_id}}

    # Initial invoke – user message wrapped as LangChain message dict.
    result = agent.invoke(
        {"messages": [{"role": "human", "content": user_query}]},
        config=config,
    )

    # ---------------------------------------------------------------------
    # Loop while the middleware has paused the execution.
    # ---------------------------------------------------------------------
    while "__interrupt__" in result:
        # The interrupt payload is a list with a single element; its ``value``
        # attribute holds a dict with ``action_requests`` and ``review_configs``.
        interrupt_value = result["__interrupt__"][0].value
        action_requests: List[Dict[str, Any]] = interrupt_value["action_requests"]
        review_configs: Dict[str, Any] = interrupt_value.get("review_configs", {})

        decisions: List[Dict[str, Any]] = []
        print("\n--- Подтверждение действия(й) инструмента ---")
        for idx, request in enumerate(action_requests, start=1):
            name = request.get("name")
            args = request.get("args", {})
            description = request.get("description", "")
            print(f"\nЗапрос {idx}:")
            print(f"  Инструмент : {name}")
            print(f"  Аргументы  : {json.dumps(args, ensure_ascii=False)}")
            if description:
                print(f"  Описание   : {description}")

            # Determine allowed decisions – we only support approve/reject.
            allowed = review_configs.get(name, {}).get("allowed_decisions", ["approve", "reject"])
            # Prompt until a valid choice is entered.
            while True:
                choice = input("  a = approve, r = reject: ").strip().lower()
                if choice == "a" and "approve" in allowed:
                    decisions.append({"type": "approve"})
                    break
                if choice == "r" and "reject" in allowed:
                    reason = input("  Сообщение отказа (будет отправлено модели): ")
                    decisions.append({"type": "reject", "message": reason})
                    break
                print("  Неверный ввод. Пожалуйста, введите 'a' или 'r'.")

        # Resume the agent with the collected decisions.
        result = agent.invoke(Command(resume={"decisions": decisions}), config=config)

    # ---------------------------------------------------------------------
    # No more '__interrupt__' – the agent has produced a final answer.
    # ---------------------------------------------------------------------
    final_message = result.get("messages", [])[-1]
    # ``final_message`` can be a dict (when using the dict‑based interface) or a
    # LangChain ``BaseMessage`` instance. Handle both.
    if isinstance(final_message, dict):
        content = final_message.get("content", "")
    elif isinstance(final_message, BaseMessage):
        content = final_message.content
    else:
        content = str(final_message)

    print("\n--- Ответ агента ---")
    print(content)

# -----------------------------------------------------------------------------
# Entry point – accept a query from the command line or ask interactively.
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Введите ваш запрос: ")
    run_interaction(query)
