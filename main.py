import os
import sys
import asyncio
from dotenv import load_dotenv

from state import ReflectState
from graph import build_graph

load_dotenv()  # loads OPENAI_API_KEY from .env if present

async def run_agent(question: str, max_rounds: int = 2):
    # Initialise the graph
    graph = build_graph(max_rounds=max_rounds)
    compiled = graph.compile()

    # Initial state
    state: ReflectState = {
        "question": question,
        "draft": "",
        "critique": "",
        "verdict": "",
        "round": 0,
        "max_rounds": max_rounds,
    }

    print("\n=== Starting Reflection Agent ===\n")
    async for event in compiled.stream(state):
        node = event.get("next")
        cur_state = event.get("state")
        if node == "draft":
            print(f"--- Draft (round {cur_state['round']}) ---")
            print(cur_state["draft"])
            print()
        elif node == "reflect":
            print(f"--- Critique (round {cur_state['round']}) ---")
            print(cur_state["critique"])
            print(f"Verdict: {cur_state['verdict']}")
            print()
        elif node == "rewrite":
            print(f"--- Rewritten Draft (round {cur_state['round']}) ---")
            print(cur_state["draft"])
            print()
    # After the stream finishes, the final state is the last emitted state
    final_state = event.get("state") if event else state
    print("=== Final Answer ===")
    print(final_state.get("draft", "[No answer generated]"))

def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Enter the question: ")
    asyncio.run(run_agent(question))

if __name__ == "__main__":
    main()
