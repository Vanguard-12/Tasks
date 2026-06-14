import sys
from typing import Any, Tuple

from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
from langchain.schema import BaseMessage

# Import custom tools – adjust the import if the tool name differs
from tools import get_price_tool

# Configuration values (API key, model name, etc.)
from config import OPENAI_API_KEY, MODEL_NAME


def format_message(message: BaseMessage) -> str:
    """Return a human‑readable representation of a LangChain message.

    For normal AI messages the ``content`` attribute is returned.
    For function‑call messages we format the first tool call as
    ``name(args)``.
    """
    # Regular text response
    if getattr(message, "content", None):
        return str(message.content)
    # Function call response – ``tool_calls`` is a list of dicts
    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        tc = tool_calls[0]
        name = tc.get("name")
        args = tc.get("args")
        return f"{name}({args})"
    return ""


def format_chunk_message(chunk: Tuple[Any, Any], step_state: dict) -> None:
    """Handle a ``messages`` chunk.

    * Prints a separator when the LangGraph step changes.
    * Streams the token contained in ``message.content`` without a newline.
    """
    message, meta = chunk
    # Detect step change and print separator
    current_step = meta.get("langgraph_step")
    if current_step is not None and current_step != step_state.get("step"):
        step_state["step"] = current_step
        print("\n--- --- ---\n")
    # Print token fragment if present
    if getattr(message, "content", None):
        print(message.content, end="", flush=True)


def main() -> None:
    # Obtain user query either from CLI arguments or interactive input
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("Enter your query: ")

    # Initialise the LLM – adjust parameters as needed
    llm = ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENAI_API_KEY,
        temperature=0,
    )

    # Build the LangGraph agent with the custom tool(s)
    agent = create_openai_functions_agent(llm, [get_price_tool])

    # Start streaming with both message tokens and update events
    stream = agent.stream(
        {"messages": [{"role": "human", "content": user_query}]},
        stream_mode=["messages", "updates"],
    )

    step_state = {"step": None}

    for chunk_type, chunk_data in stream:
        if chunk_type == "messages":
            # ``chunk_data`` is a tuple (message, meta)
            format_chunk_message(chunk_data, step_state)
        elif chunk_type == "updates":
            # ``updates`` may contain a ``model`` key with the latest messages
            model_info = chunk_data.get("model")
            if model_info:
                # The last message produced by the model in this step
                last_msg = model_info["messages"][-1]
                print(format_message(last_msg))

    # Ensure the console ends with a newline
    print()


if __name__ == "__main__":
    main()
