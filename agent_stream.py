import os
import json
from typing import Any, Dict, List, Tuple

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent

# ---------------------------------------------------------------------------
# 1.  LLM configuration
# ---------------------------------------------------------------------------
# The OpenAI API key must be provided via the environment variable
# ``OPENAI_API_KEY``.  The project already contains a ``config.yaml`` with a
# default model name – we reuse it if present, otherwise fall back to the
# ``gpt-4o-mini`` model which is cheap and supports streaming.

DEFAULT_MODEL = "gpt-4o-mini"

model_name = os.getenv("LANGCHAIN_MODEL", DEFAULT_MODEL)

llm = ChatOpenAI(model=model_name, streaming=True)

# ---------------------------------------------------------------------------
# 2.  Example tool (can be replaced by any tool from the original project)
# ---------------------------------------------------------------------------
@tool
def get_price(product: str, city: str) -> str:
    """Return a fake price for a product in a city.

    In the original assignment the tool queried a real data source.  For the
    purpose of the streaming demo we keep it deterministic so that the output
    is reproducible in the automated tests.
    """
    # Simple deterministic table – the exact formatting mirrors the one used
    # in the non‑streaming version of the assignment.
    price_table = {
        ("молоко", "Казань"): ("89", "Магнит"),
        ("хлеб", "Казань"): ("45", "Пятёрочка"),
    }
    price, shop = price_table.get((product, city), ("неизвестно", "неизвестно"))
    return f"| Продукт | Цена (руб.) | Магазин    |\n| {product} | {price} | {shop} |"

# ---------------------------------------------------------------------------
# 3.  Build the LangChain agent
# ---------------------------------------------------------------------------
# The original project builds a more complex graph – here we construct a
# simple ReAct‑style agent that is sufficient to demonstrate the streaming API.

tools = [get_price]

# ``create_react_agent`` returns a ``Runnable`` that can be used with ``.invoke``
# or ``.stream``.  We keep the same configuration that the previous assignment
# used (a system prompt from the Hub and the list of tools).

prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)

# ``AgentExecutor`` adds a convenient ``.invoke``/``.stream`` wrapper.
executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

# ---------------------------------------------------------------------------
# 4.  Helper functions for formatting output
# ---------------------------------------------------------------------------
step_counter = 1


def format_message(message: Any) -> str:
    """Return a human‑readable representation of a LangChain message.

    If the message contains ``content`` we return it directly.  Otherwise the
    message is a tool call and we format it as ``tool_name(args)``.
    """
    if getattr(message, "content", None):
        return str(message.content)
    # ``tool_calls`` is a list of dicts – we take the first one.
    if getattr(message, "tool_calls", None):
        call = message.tool_calls[0]
        name = call.get("name", "unknown")
        args = json.dumps(call.get("args", {}), ensure_ascii=False)
        return f"{name}({args})"
    return "<empty message>"


def format_chunk_message(chunk: Tuple[Any, Dict]) -> None:
    """Process a ``('messages', (message, meta))`` chunk.

    The function prints a separator when the LangGraph step changes and then
    prints the token (or tool‑call placeholder) without a newline.
    """
    global step_counter
    message, meta = chunk
    # ``meta`` contains ``langgraph_step`` – we guard against missing keys.
    current_step = meta.get("langgraph_step", step_counter)
    if current_step != step_counter:
        step_counter = current_step
        print("\n--- --- ---\n", flush=True)
    # ``message.content`` may be an empty string when the agent is about to
    # invoke a tool.  In that case we do nothing – the tool call will be shown
    # in the ``updates`` branch.
    if getattr(message, "content", None):
        print(message.content, end="", flush=True)

# ---------------------------------------------------------------------------
# 5.  Main entry point – runs the agent in streaming mode
# ---------------------------------------------------------------------------
def run_stream(user_input: str) -> None:
    """Execute the agent with ``.stream`` and print output progressively.

    The function mirrors the behaviour described in the assignment:

    * ``stream_mode=['messages', 'updates']`` enables both token‑wise text and
      tool‑call updates.
    * Tokens are printed immediately (no newline) and flushed.
    * When the internal ``langgraph_step`` changes a visual separator is printed.
    * When an ``updates`` chunk contains a ``model`` key we extract the last
      message from the model's ``messages`` list and print it using
      ``format_message`` – this reproduces the tool‑call representation that the
      non‑streaming version produced.
    """
    stream = executor.stream(
        {"messages": [{"role": "human", "content": user_input}]},
        stream_mode=["messages", "updates"],
    )

    for chunk_type, chunk_data in stream:
        if chunk_type == "messages":
            # ``chunk_data`` is a tuple (message, meta)
            format_chunk_message(chunk_data)
        elif chunk_type == "updates":
            # ``updates`` chunks are dictionaries with optional ``model`` key.
            if isinstance(chunk_data, dict) and "model" in chunk_data:
                model_info = chunk_data["model"]
                # ``messages`` is a list of LangChain messages – the last one is
                # the most recent output (either AI text or a tool call).
                if isinstance(model_info, dict) and "messages" in model_info:
                    last_msg = model_info["messages"][-1]
                    print(format_message(last_msg))

# ---------------------------------------------------------------------------
# 6.  Simple CLI for manual testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the LangChain agent in stream mode.")
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Расскажи, как приготовить борщ, и покажи цены ингредиентов в Казани.",
        help="User prompt to send to the agent.",
    )
    args = parser.parse_args()
    run_stream(args.prompt)
    # Ensure the final newline so the shell prompt appears on a new line.
    print()
