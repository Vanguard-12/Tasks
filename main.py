import argparse
import asyncio
import os
from dotenv import load_dotenv
from graph import graph
from state import CompareState

DEFAULT_ENTITIES = ["Chroma", "FAISS", "Qdrant"]

async def run_compare(entities: list[str]):
    # initial state
    state: CompareState = {
        "entities": entities,
        "criteria": [],
        "findings": {},
        "final_table": None,
        "verdict": None,
        "_pending_pairs": []
    }
    result = await graph.ainvoke(state)
    # Print outputs
    print("\n=== Generated Criteria ===")
    for c in result["criteria"]:
        print(f"- {c}")
    print("\n=== Research Notes ===")
    for ent, notes in result["findings"].items():
        for idx, note in enumerate(notes):
            crit = result["criteria"][idx]
            print(f"[{ent} × {crit}] -> {note}")
    print("\n=== Comparison Table ===")
    print(result["final_table"])
    print("\n=== Verdict ===")
    print(result["verdict"])

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="LangGraph comparative review using Tavily")
    parser.add_argument("--interactive", action="store_true", help="Enter custom three entities")
    args = parser.parse_args()
    if args.interactive:
        entities = []
        for i in range(3):
            ent = input(f"Enter entity #{i+1}: ")
            entities.append(ent.strip())
    else:
        entities = DEFAULT_ENTITIES
    asyncio.run(run_compare(entities))

if __name__ == "__main__":
    main()
