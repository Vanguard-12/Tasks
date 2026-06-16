from rich.console import Console
from rich.prompt import Prompt
from typing import Any, Dict, Optional

# Import LangGraph components for memory and checkpointing
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import the example tool
from tools import get_price

console = Console()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Use a single thread_id for this demo. In a real application you might generate
# a unique ID per conversation.
CONFIG = {"configurable": {"thread_id": "conversation-1"}}

# Initialise the memory saver (checkpoint) – required for interrupt handling.
memory = MemorySaver()

# Create a simple LLM wrapper. For the purpose of this sandbox we use the
# OpenAI "gpt-3.5-turbo" model if an API key is available; otherwise we fall back
# to a very small deterministic mock that simply echoes the user input. This
# avoids external network calls during automated tests.
def _create_llm():
    try:
        from openai import OpenAI
        client = OpenAI()
        # Simple wrapper that forwards messages to the OpenAI chat API.
        class OpenAILLM:
            def __init__(self, client):
                self.client = client

            def invoke(self, messages):
                # The OpenAI client expects a list of dicts with role/content.
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                )
                return {"content": response.choices[0].message.content}

        return OpenAILLM(client)
    except Exception:
        # Fallback mock LLM – just returns the last human message prefixed.
        class MockLLM:
            def invoke(self, messages):
                # Find the last human message.
                human_msg = next(
                    (m["content"] for m in reversed(messages) if m["role"] == "human"),
                    "",
                )
                return {"content": f"Echo: {human_msg}"}

        return MockLLM()

llm = _create_llm()

# ---------------------------------------------------------------------------
# Agent creation
# ---------------------------------------------------------------------------
# The agent is built with:
#   * the LLM defined above
#   * a list of tools (currently only `get_price`)
#   * a system prompt that explains its role
#   * the memory saver for checkpointing
#   * `interrupt_before=['tools']` to pause before each tool call
# ---------------------------------------------------------------------------
agent = create_react_agent(
    llm=llm,
    tools=[get_price],
    system_prompt="You are a helpful assistant. Use tools when appropriate.",
    checkpointer=memory,
    interrupt_before=["tools"],
)

# ---------------------------------------------------------------------------
# Helper to display tool calls nicely
# ---------------------------------------------------------------------------
def _format_tool_call(tool_call: Dict[str, Any]) -> str:
    name = tool_call.get("name", "<unknown>")
    args = tool_call.get("args", {})
    return f"{name}({args})"

# ---------------------------------------------------------------------------
# Core interaction loop – handles streaming, interruptions, and user approval
# ---------------------------------------------------------------------------
def ask_and_run(user_input: Optional[Dict[str, Any]], config: Dict[str, Any]):
    """Stream the agent response, handling possible tool‑call interruptions.

    Parameters
    ----------
    user_input:
        The payload to send to the agent. If ``None`` the agent resumes from a
        previously interrupted state.
    config:
        The LangGraph configuration dict (must contain ``thread_id``).
    """
    # ``stream_mode`` ensures we receive both message tokens and update events.
    stream = agent.stream(
        user_input,
        config=config,
        stream_mode=["messages", "updates"],
    )

    for chunk in stream:
        # ``chunk`` is a tuple: (type, data)
        chunk_type, chunk_data = chunk
        state = agent.get_state(config)

        if chunk_type == "messages":
            # ``chunk_data`` contains a list of messages; we print the content
            # token‑by‑token, preserving the original formatting.
            for msg in chunk_data.get("messages", []):
                # The content may be a string or a list of tokens; handle both.
                content = msg.get("content", "")
                if isinstance(content, str):
                    console.print(content, end="")
                else:
                    # Assume an iterable of token strings.
                    for token in content:
                        console.print(token, end="")
            # Ensure a newline after the assistant's reply.
            console.print()

        if chunk_type == "updates":
            # ``updates`` can contain tool call information; we simply log it.
            updates = chunk_data.get("updates", [])
            for upd in updates:
                console.print(f"[yellow]Update:[/] {upd}")

        # Detect an interrupt before a tool call.
        if "__interrupt__" in chunk_data and state.next == ("tools",):
            # Retrieve the pending tool call from the latest assistant message.
            last_msg = state.values["messages"][-1]
            tool_calls = last_msg.tool_calls
            if not tool_calls:
                console.print("[red]Interrupt detected but no tool call found.[/]")
                continue
            tool_call = tool_calls[0]
            console.print(f"[bold]Agent wants to call tool:[/] {_format_tool_call(tool_call)}")
            # Prompt the user for confirmation.
            answer = Prompt.ask("Разрешить? (Y/n)", default="Y")
            if answer.lower().strip() == "y" or answer == "":
                # Resume execution by sending ``None`` as the next input.
                ask_and_run(None, config)
            else:
                console.print("[red]Отменено[/]")
                # Abort the current tool call by resetting the checkpoint.
                # The simplest way is to clear the pending state.
                memory.clear(config)
            # After handling the interrupt we break out of the current stream.
            break

# ---------------------------------------------------------------------------
# Main REPL loop
# ---------------------------------------------------------------------------
def main():
    console.print("[bold green]LangGraph Agent with Memory & HITL Confirmation[/]")
    console.print("Type your message and press Enter. Type 'exit' to quit.\n")
    while True:
        user_text = Prompt.ask("[cyan]Вы[/]")
        if user_text.strip().lower() == "exit":
            console.print("[bold]Goodbye![/]")
            break
        payload = {"messages": [{"role": "human", "content": user_text}]}
        ask_and_run(payload, CONFIG)

if __name__ == "__main__":
    main()

