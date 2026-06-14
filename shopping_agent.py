import os
from typing import Any, Dict

from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent

# ---------------------------------------------------------------------------
# Configuration – set the model name that is loaded in LM Studio.
# You can override it with the environment variable LL M_MODEL_NAME.
# ---------------------------------------------------------------------------
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "<model_name>")  # e.g. "mistral-7b-instruct-v0.2"

llm = ChatOpenAI(
    model=MODEL_NAME,
    base_url="http://localhost:1234/v1",
    api_key=SecretStr("fake"),
    temperature=0.7,
)

# ---------------------------------------------------------------------------
# Helper: create a lightweight sub‑agent that only generates a price table.
# ---------------------------------------------------------------------------
def _create_price_subagent(city: str):
    """Return a LangChain agent that produces a markdown price table for a product.

    The sub‑agent has **no tools**, so it cannot call back to the main agent.
    """
    system_prompt = (
        f"You are a price‑estimation assistant for Russian supermarkets in {city}. "
        "Given a product name, return a markdown table with columns: "
        "Продукт, Цена (руб.), Магазин. Use realistic Russian store names (e.g., Магнит, Пятёрочка, Перекрёсток)."
    )
    return create_agent(
        model=llm,
        tools=[],  # no tools – pure generation
        system_prompt=system_prompt,
    )

# ---------------------------------------------------------------------------
# Tool used by the main shopping‑assistant agent.
# ---------------------------------------------------------------------------
@tool
def get_price(product: str, city: str) -> str:
    """Generate a realistic price for *product* in *city*.

    The function creates a sub‑agent that returns a markdown table like:
    | Продукт | Цена (руб.) | Магазин |
    """
    sub_agent = _create_price_subagent(city)
    query = f"Сколько стоит {product} в {city}? Верни результат в виде markdown‑таблицы."
    answer = sub_agent.invoke({"messages": [{"role": "human", "content": query}]})
    # The sub‑agent returns a dict with a `messages` list; the last message holds the table.
    return answer["messages"][-1]["content"]

# ---------------------------------------------------------------------------
# Helper to format any message (human, AI, or tool call) for console output.
# ---------------------------------------------------------------------------
def format_message(msg: Dict[str, Any]) -> str:
    # Human / AI messages have a 'content' field.
    if msg.get("content"):
        return msg["content"]
    # Tool calls are stored under 'tool_calls'. Show a compact representation.
    tool_calls = msg.get("tool_calls") or []
    if tool_calls:
        call = tool_calls[0]
        name = call.get("name")
        args = call.get("args")
        return f"{name}({args})"
    return "<empty message>"

# ---------------------------------------------------------------------------
# Main shopping‑assistant agent.
# ---------------------------------------------------------------------------
main_agent = create_agent(
    model=llm,
    tools=[get_price],
    system_prompt="Ты помощник по планированию покупок.",
)

# ---------------------------------------------------------------------------
# Utility: parse a markdown table and sum numeric price values.
# ---------------------------------------------------------------------------
def compute_total_from_table(table_md: str) -> float:
    """Extract numeric prices from a markdown table and return their sum.

    Supports plain numbers (e.g., "89") and values with units like "120/кг".
    """
    total = 0.0
    for line in table_md.splitlines():
        # Skip header and separator rows.
        stripped = line.strip()
        if stripped.startswith("| Продукт") or stripped.startswith("|---"):
            continue
        # Split the row into cells.
        parts = [p.strip() for p in stripped.strip("| ").split("|")]
        if len(parts) < 3:
            continue
        price_str = parts[1]
        # Keep only digits and decimal point.
        numeric = "".join(ch for ch in price_str if ch.isdigit() or ch == ".")
        if numeric:
            try:
                total += float(numeric)
            except ValueError:
                pass
    return total

# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------
def main():
    user_query = "Помоги составить список покупок: молоко, хлеб, яблоки. Я нахожусь в Казани."
    response = main_agent.invoke({"messages": [{"role": "human", "content": user_query}]})

    # Print the whole chain of messages.
    for msg in response["messages"]:
        print("---")
        print(format_message(msg))

    # If the final message contains a table, compute and display the total.
    final_msg = response["messages"][-1]
    if final_msg.get("content"):
        table_md = final_msg["content"]
        total = compute_total_from_table(table_md)
        if total:
            print("---")
            print(f"**Итого:** {total:.0f} руб.")

if __name__ == "__main__":
    main()
