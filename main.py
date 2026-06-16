import json
import os
import sys
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# ---------------------------------------------------------------------------
# Load environment variables (e.g. OPENAI_API_KEY) – optional but convenient.
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# 1. Define a simple tool (replace with a real implementation if desired).
# ---------------------------------------------------------------------------
@tool
def get_weather(city: str, date: str = "today") -> str:
    """Return a fake weather forecast for a given city and date."""
    return f"The weather in {city} on {date} is sunny with a temperature of 20°C."

# ---------------------------------------------------------------------------
# 2. Initialise the LLM, memory and the Human‑In‑The‑Loop middleware.
# ---------------------------------------------------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

memory = MemorySaver()

middleware = [
    HumanInTheLoopMiddleware(
        interrupt_on={"get_weather": True},  # pause on every call to get_weather
        description_prefix="Please confirm the tool call",
    )
]

# ---------------------------------------------------------------------------
# 3. Build the agent.
# ---------------------------------------------------------------------------
agent = create_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="You are a helpful assistant.",
    middleware=middleware,
    checkpointer=memory,
)

# ---------------------------------------------------------------------------
# 4. Helper to extract the interrupt payload (different LangGraph versions may
#    wrap the payload in a list containing a StateSnapshot with a .value attr).
# ---------------------------------------------------------------------------
def _extract_interrupt(result: Dict[str, Any]) -> Dict[str, Any]:
    """Return the dictionary inside the '__interrupt__' payload.

    The payload format used by HumanInTheLoopMiddleware is:
        result["__interrupt__"][0].value -> {"action_requests": ..., "review_configs": ...}
    """
    interrupt_wrapper = result["__interrupt__"][0]
    # Some versions expose the value directly, others via .value attribute.
    if isinstance(interrupt_wrapper, dict) and "value" in interrupt_wrapper:
        return interrupt_wrapper["value"]
    # Assume an object with a .value attribute.
    return getattr(interrupt_wrapper, "value")

# ---------------------------------------------------------------------------
# 5. Core loop that handles one user query, resolves all interruptions and
#    finally prints the assistant's answer.
# ---------------------------------------------------------------------------
CONFIG = {"configurable": {"thread_id": "session-1"}}

def run_query(user_message: str) -> None:
    # First call – the agent receives the user's message.
    result = agent.invoke({"messages": [{"role": "human", "content": user_message}]}, config=CONFIG)

    # Keep handling interruptions until the agent finishes.
    while "__interrupt__" in result:
        interrupt_payload = _extract_interrupt(result)
        action_requests: List[Dict[str, Any]] = interrupt_payload.get("action_requests", [])
        review_configs: List[Dict[str, Any]] = interrupt_payload.get("review_configs", [])

        decisions: List[Dict[str, Any]] = []
        print("\n--- Human‑in‑the‑Loop Confirmation ---")
        for idx, action in enumerate(action_requests):
            name = action.get("name")
            args = action.get("args", {})
            description = action.get("description", "")
            allowed = review_configs[idx].get("allowed_decisions", ["approve", "reject"])

            print(f"\nAction #{idx + 1}:")
            print(f"  Tool       : {name}")
            print(f"  Arguments  : {json.dumps(args, ensure_ascii=False, indent=2)}")
            if description:
                print(f"  Description: {description}")
            print(f"  Allowed decisions: {', '.join(allowed)}")

            # Prompt the user until a valid decision is given.
            while True:
                choice = input("  Decision (a = approve, r = reject): ").strip().lower()
                if choice == "a" and "approve" in allowed:
                    decisions.append({"type": "approve"})
                    break
                if choice == "r" and "reject" in allowed:
                    msg = input("  Reason for rejection (will be sent to the model): ").strip()
                    decisions.append({"type": "reject", "message": msg})
                    break
                print("  Invalid input. Please enter 'a' or 'r' according to allowed decisions.")

        # Resume the agent with the collected decisions.
        result = agent.invoke(Command(resume={"decisions": decisions}), config=CONFIG)

    # When the loop exits there is no '__interrupt__' – the agent finished.
    final_message = result.get("messages", [])[-1].get("content", "")
    print("\n=== Assistant Response ===")
    print(final_message)

# ---------------------------------------------------------------------------
# 6. Simple REPL so the user can ask multiple questions while keeping the
#    same thread_id (conversation history).
# ---------------------------------------------------------------------------
def main() -> None:
    print("Human‑in‑the‑Loop LangChain Demo (type 'exit' or Ctrl‑D to quit)\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("\nGoodbye!")
            break
        run_query(user_input)

if __name__ == "__main__":
    main()
