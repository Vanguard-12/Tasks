import os

from vectorstore import create_vectorstore, load_documents
from tools import set_vectorstore, search_local_kb, web_search


def _needs_web(query: str) -> bool:
    """Very small heuristic to decide whether a query likely requires up‑to‑date web info.
    The list contains Russian and English keywords that commonly indicate a need for
    current information (news, latest, etc.).
    """
    keywords = [
        "новости",
        "актуальн",
        "сегодня",
        "последн",
        "latest",
        "news",
        "current",
        "today",
    ]
    lowered = query.lower()
    return any(word in lowered for word in keywords)


def main():
    # Initialise (or load) the persistent Chroma vector store.
    vectorstore = create_vectorstore()
    # Make the vectorstore available to the tool functions.
    set_vectorstore(vectorstore)

    # If the store is empty, try to load documents from the default folder.
    try:
        # ``_collection`` is an internal attribute of Chroma; we use it only to
        # check whether any documents are already present.
        if getattr(vectorstore, "_collection", None) is None or vectorstore._collection.count() == 0:
            docs_dir = os.getenv("DOCS_DIR", "documents")
            if os.path.isdir(docs_dir):
                print("Vector store empty – loading documents …")
                load_documents(docs_dir, vectorstore)
    except Exception as exc:
        # If the check fails we simply continue; the tools will raise a clear
        # error if they are used without data.
        print(f"Warning while checking vector store contents: {exc}")

    print("AI‑assistant ready. Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("\nЗапрос: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Good‑bye!")
            break
        if not user_input:
            continue

        if _needs_web(user_input):
            answer = web_search(user_input)
            source = "tavily"
        else:
            answer = search_local_kb(user_input)
            source = "chromadb"

        print("\nОтвет:")
        print(answer)
        print(f"\nИсточник: {source}")


if __name__ == "__main__":
    main()
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
