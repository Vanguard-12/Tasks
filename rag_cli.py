import argparse

from rag_agent import get_agent
from rag_tools import add_to_knowledge_base, search_knowledge_base


def _interactive_loop() -> None:
    agent = get_agent()
    print("RAG CLI – type /add <title>, /search <query>, or just ask a question. Use /quit to exit.")
    while True:
        try:
            user_input = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input:
            continue
        if user_input.lower() == "/quit":
            print("Goodbye!")
            break
        if user_input.startswith("/add"):
            parts = user_input.split(maxsplit=1)
            title = parts[1] if len(parts) > 1 else "Untitled"
            print("Enter the document content. Finish with a line containing only 'END':")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            content = "\n".join(lines)
            result = add_to_knowledge_base(content, title)
            print(result)
        elif user_input.startswith("/search"):
            query = user_input[len("/search"):].strip()
            results = search_knowledge_base(query, max_results=5)
            if not results:
                print("No results found.")
                continue
            for i, doc in enumerate(results, 1):
                title = doc.metadata.get("title", "(no title)")
                snippet = doc.page_content[:200].replace("\n", " ")
                print(f"{i}. [{title}] {snippet}...")
        else:
            # Normal question – let the agent decide whether to use tools.
            response = agent.run(user_input)
            print(response)


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive RAG CLI")
    parser.parse_args()  # No custom arguments for now.
    _interactive_loop()


if __name__ == "__main__":
    main()
