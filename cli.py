import sys
from tools import add_to_knowledge_base, search_knowledge_base


def main():
    print("Welcome to the RAG Agent CLI. Commands: /add <title> <content>, /search <query>, /quit")
    while True:
        try:
            inp = input("> ")
        except EOFError:
            break

        if inp.strip() == "/quit":
            print("Goodbye!")
            break

        if inp.startswith("/add "):
            parts = inp.split(" ", 2)
            if len(parts) < 3:
                print("Usage: /add <title> <content>")
                continue
            title, content = parts[1], parts[2]
            print(add_to_knowledge_base(content, title))
            continue

        if inp.startswith("/search "):
            query = inp[len("/search "):].strip()
            print(search_knowledge_base(query, max_results=5))
            continue

        print("Unknown command. Use /add, /search, or /quit.")


if __name__ == "__main__":
    main()
