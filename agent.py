import sys
import re
import random
from typing import List

from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent

# ---------------------------------------------------------------------------
# Configuration – adjust the model name if needed.
# ---------------------------------------------------------------------------
MODEL_NAME = "local-model"  # replace with the exact model name used in LM Studio
BASE_URL = "http://localhost:1234/v1"
API_KEY = SecretStr("fake")  # LM Studio does not require a real key

# ---------------------------------------------------------------------------
# Initialise the LLM wrapper.
# ---------------------------------------------------------------------------
try:
    llm = ChatOpenAI(
        model=MODEL_NAME,
        base_url=BASE_URL,
        api_key=API_KEY,
        temperature=0.7,
    )
except Exception as exc:  # pragma: no cover – catches connection errors early
    print(
        f"Unable to initialise LLM at {BASE_URL}.\n"
        "Please ensure LM Studio is running and the model name is correct."
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Sub‑agent tool: generate a price table for a single product.
# ---------------------------------------------------------------------------
@tool
def get_price(product: str, city: str) -> str:
    """Generate a markdown table with a realistic price for *product* in *city*.

    The function creates a **sub‑agent** that asks the LLM to produce a table:
    ````markdown
    | Продукт | Цена (руб.) | Магазин |
    |---------|-------------|---------|
    | <product> | <price> | <store> |
    ````
    The returned string is the raw markdown table.
    """
    # Create a lightweight sub‑agent that has no tools – it only generates text.
    sub_agent = create_agent(
        model=llm,
        tools=[],
        system_prompt=(
            "You are a price generator. Provide a markdown table with columns "
            "'Продукт', 'Цена (руб.)', and 'Магазин' for the given product and city. "
            "The price should be realistic for a Russian market."
        ),
    )

    # Prompt the sub‑agent.
    prompt = f"Provide a price for '{product}' in the city '{city}'."
    try:
        response = sub_agent.invoke({"messages": [{"role": "human", "content": prompt}]})
    except Exception as exc:  # pragma: no cover – network / LLM errors
        return f"| Продукт | Цена (руб.) | Магазин |\n| {product} | Ошибка получения цены | - |"

    # Extract the last message content (the markdown table).
    try:
        table = response["messages"][-1]["content"]
    except Exception:
        # Fallback – generate a simple table locally if LLM response is unexpected.
        price = random.randint(30, 150)
        store = random.choice(["Магнит", "Пятёрочка", "Перекрёсток", "Ашан"])
        table = (
            "| Продукт | Цена (руб.) | Магазин |\n"
            "|---------|-------------|---------|\n"
            f"| {product} | {price} | {store} |"
        )
    return table

# ---------------------------------------------------------------------------
# Main agent – orchestrates the shopping list.
# ---------------------------------------------------------------------------
main_agent = create_agent(
    model=llm,
    tools=[get_price],
    system_prompt="Ты помощник по планированию покупок.",
)

# ---------------------------------------------------------------------------
# Helper utilities.
# ---------------------------------------------------------------------------
def format_message(msg) -> str:
    """Return a human‑readable representation of a LangChain message."""
    if "content" in msg and msg["content"]:
        return msg["content"]
    # Tool call representation
    if "tool_calls" in msg and msg["tool_calls"]:
        call = msg["tool_calls"][0]
        name = call.get("name", "unknown")
        args = call.get("args", {})
        return f"{name}({args})"
    return "<empty message>"

def extract_prices_from_table(table: str) -> List[float]:
    """Parse a markdown price table and return numeric price values.

    Rows with non‑numeric price formats (e.g., "120/кг") are ignored for the sum.
    """
    prices = []
    lines = table.splitlines()
    for line in lines:
        # Skip header and separator lines
        if line.startswith("|") and not line.startswith("| Продукт"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2:
                price_str = parts[1]
                # Extract leading number if present
                match = re.search(r"(\d+(?:[.,]\d*)?)", price_str)
                if match:
                    try:
                        price = float(match.group(1).replace(",", "."))
                        prices.append(price)
                    except ValueError:
                        continue
    return prices

# ---------------------------------------------------------------------------
# Execution entry point.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    user_query = (
        "Помоги составить список покупок: молоко, хлеб, яблоки. "
        "Я нахожусь в Казани."
    )
    try:
        result = main_agent.invoke({"messages": [{"role": "human", "content": user_query}]})
    except Exception as exc:  # pragma: no cover – unexpected LLM errors
        print(f"Error invoking main agent: {exc}")
        sys.exit(1)

    messages = result.get("messages", [])
    total_price = 0.0
    print("--- Interaction Log ---")
    for msg in messages:
        formatted = format_message(msg)
        print(formatted)
        # If the message looks like a price table, try to extract numbers.
        if "| Продукт" in formatted:
            total_price += sum(extract_prices_from_table(formatted))
    # Print total if we managed to parse any numbers.
    if total_price:
        print(f"\n**Итого:** ~{int(total_price)} руб.")
    else:
        print("\nНе удалось вычислить итоговую стоимость.")
