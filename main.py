import json
import os
from typing import List, Dict

from dotenv import load_dotenv
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# ---------------------------------------------------------------------------
# Load environment variables (e.g., OPENAI_API_KEY)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Initialise LLM – using OpenAI's gpt‑4o‑mini as an example.
# ---------------------------------------------------------------------------
from langchain_community.llms import OpenAI

llm = OpenAI(model="gpt-4o-mini", temperature=0)

# ---------------------------------------------------------------------------
# Example tool – a mock weather function.
# Replace with a real implementation if desired.
# ---------------------------------------------------------------------------
@tool
def get_weather(city: str, date: str = "today") -> str:
    """Return a short weather description for *city* on *date*.
    This is a mock implementation used for demonstration purposes.
    """
    return f"Sunny with a high of 22°C in {city} on {date}."

# ---------------------------------------------------------------------------
# Helper functions for displaying interruptions and collecting decisions.
# ---------------------------------------------------------------------------
console = Console()

def display_action_requests(action_requests: List[Dict]):
    table = Table(title="Tool call awaiting confirmation")
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Tool", style="magenta")
    table.add_column("Arguments", style="green")
    for idx, ar in enumerate(action_requests, start=1):
        args_pretty = json.dumps(ar.get("args", {}), ensure_ascii=False, indent=2)
        table.add_row(str(idx), ar.get("name", ""), args_pretty)
    console.print(table)

def collect_decisions(action_requests: List[Dict], review_configs: List[Dict]) -> List[Dict]:
    decisions: List[Dict] = []
    for i, (ar, rc) in enumerate(zip(action_requests, review_configs)):
        # The middleware may provide a list of allowed decisions.
        allowed = rc.get("allowed_decisions", ["approve", "reject", "edit"])
        # For this assignment we only handle approve/reject.
        allowed = [d for d in allowed if d in ("approve", "reject")]
        while True:
            rprint(f"[bold]Action {i+1}[/bold] – tool: [magenta]{ar.get('name')}[/magenta]")
            rprint(f"Arguments: {json.dumps(ar.get('args', {}), ensure_ascii=False, indent=2)}")
            choice = input("Approve (a) / Reject (r): ").strip().lower()
            if choice == "a" and "approve" in allowed:
                decisions.append({"type": "approve"})
                break
            elif choice == "r" and "reject" in allowed:
                msg = input("Reason for rejection (will be sent to the model): ")
                decisions.append({"type": "reject", "message": msg})
                break
            else:
                rprint("[red]Invalid choice. Please enter 'a' for approve or 'r' for reject.[/red]")
    return decisions

# ---------------------------------------------------------------------------
# Core function that runs the agent with a Human‑In‑The‑Loop loop.
# ---------------------------------------------------------------------------
def run_agent(messages: List[Dict], thread_id: str) -> None:
    # Memory checkpoint ensures the pause state is persisted across resumes.
    memory = MemorySaver()

    agent = create_agent(
        model=llm,
        tools=[get_weather],
        system_prompt="Ты полезный ассистент, отвечающий на вопросы о погоде.",
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={"get_weather": True},
                description_prefix="Подтвердите вызов инструмента",
            ),
        ],
        checkpointer=memory,
    )

    config = {"configurable": {"thread_id": thread_id}}

    # Initial invocation with the user's message(s).
    result = agent.invoke({"messages": messages}, config=config)

    # Loop while the middleware signals an interruption.
    while "__interrupt__" in result:
        interrupt = result["__interrupt__"][0].value
        action_requests = interrupt.get("action_requests", [])
        review_configs = interrupt.get("review_configs", [])

        display_action_requests(action_requests)
        decisions = collect_decisions(action_requests, review_configs)

        # Resume execution with the gathered decisions.
        result = agent.invoke(Command(resume={"decisions": decisions}), config=config)

    # No more interruptions – print the final assistant message.
    final_msg = result.get("messages", [])[-1].get("content", "")
    rprint("[bold green]Assistant:[/bold green]", final_msg)

# ---------------------------------------------------------------------------
# Simple REPL – keeps the same thread_id to preserve conversation history.
# ---------------------------------------------------------------------------
def main() -> None:
    thread_id = "session-1"
    rprint("[bold]Human‑in‑the‑Loop Agent Demo[/bold]")
    rprint("Type 'exit' or press Ctrl‑C to quit.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not user_input:
            continue
        run_agent([{"role": "human", "content": user_input}], thread_id)

if __name__ == "__main__":
    main()
