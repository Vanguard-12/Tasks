from rich.console import Console
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent, tool

# Dummy tool implementation
@tool(name="get_price")
def get_price(city: str, date: str) -> str:
    """Return a dummy price for a given city and date."""
    return f"Price for {city} on {date} is 1000 RUB"

# Initialize memory saver and console
memory = MemorySaver()
console = Console()

# Create the agent with memory and interrupt before tool calls
agent = create_react_agent(
    model="gpt-4o-mini",  # Replace with your actual model identifier if needed
    tools=[get_price],
    checkpointer=memory,
    interrupt_before=["tools"],
)

# Configuration with a thread_id to keep conversation history
config = {"configurable": {"thread_id": "conversation-1"}}

def ask_and_run(user_input, config):
    """Stream the agent response, handling tool‑call interruptions.

    Args:
        user_input: Either a dict with a ``messages`` key (for new user input)
                    or ``None`` to resume after an interruption.
        config: The LangGraph configuration containing the ``thread_id``.
    """
    for chunk in agent.stream(user_input, config=config, stream_mode=["messages", "updates"]):
        state = agent.get_state(config)
        chunk_type, chunk_data = chunk

        # Streamed assistant messages
        if chunk_type == "messages":
            # ``chunk_data`` is a list of message dicts
            for msg in chunk_data:
                if "content" in msg:
                    # Preserve streaming behaviour (no extra newline)
                    console.print(msg["content"], end="")

        # Updates (e.g., tool call information) – can be extended if needed
        if chunk_type == "updates":
            pass  # No special handling required for this assignment

        # Detect interruption before a tool call
        if "__interrupt__" in chunk_data and getattr(state, "next", None) == ("tools",):
            # Extract the pending tool call from the latest assistant message
            last_msg = state.values["messages"][-1]
            tool_call = last_msg.tool_calls[0]
            name = tool_call["name"]
            args = tool_call["args"]
            console.print(f"\nAgent wants to call {name}({args})")
            answer = input("Разрешить? (Y/n): ")
            if answer.lower().strip() == "y":
                # Resume execution from the interruption point
                ask_and_run(None, config)
            else:
                console.print("Отменено")
                break

def main():
    while True:
        user_input = input("\nВы: ")
        if user_input.strip().lower() == "exit":
            break
        ask_and_run({"messages": [{"role": "human", "content": user_input}]}, config)

if __name__ == "__main__":
    main()
