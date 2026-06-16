import json
from typing import Any


def format_message(message: Any) -> str:
    """Convert a LangChain message (dict or object) to a readable string.

    If the message contains plain text, return it.
    If it contains a tool call, format it as ``tool_name(args)``.
    """
    # Message as a dict (result of .invoke())
    if isinstance(message, dict):
        if message.get("content"):
            return message["content"]
        if message.get("tool_calls"):
            call = message["tool_calls"][0]
            name = call.get("name")
            args = json.dumps(call.get("args", {}), ensure_ascii=False)
            return f"{name}({args})"
        return str(message)

    # Message as a LangChain Message object
    content = getattr(message, "content", None)
    if content:
        return content
    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        call = tool_calls[0]
        name = getattr(call, "name", None)
        args = getattr(call, "args", {})
        return f"{name}({json.dumps(args, ensure_ascii=False)})"
    return str(message)


def format_chunk_message(chunk: Any, step_state: dict) -> None:
    """Handle a ``messages`` chunk from ``agent.stream``.

    ``chunk`` is a tuple ``(message, meta)`` where ``meta`` contains the
    ``langgraph_step`` number. ``step_state`` is a mutable dict storing the
    current step (e.g. ``{"step": 1}``).
    """
    message, meta = chunk
    current_step = meta.get("langgraph_step")
    if current_step is None:
        # Fallback – just print the content if available.
        if getattr(message, "content", None):
            print(message.content, end="", flush=True)
        return

    if current_step != step_state["step"]:
        step_state["step"] = current_step
        print("\n --- --- --- \n")

    # ``message.content`` may be empty when the agent is about to call a tool.
    if getattr(message, "content", None):
        print(message.content, end="", flush=True)
