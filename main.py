from __future__ import annotations

from dotenv import load_dotenv

from agent import ask_agent


def main() -> None:
    load_dotenv()
    print("RAG agent is ready. Type 'exit' to quit.")
    while True:
        question = input("Запрос: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if question:
            print(ask_agent(question))
            print()


if __name__ == "__main__":
    main()
