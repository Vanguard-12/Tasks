import os
import argparse

from rag_tools import add_to_knowledge_base, search_knowledge_base


def repl():
    print("RAG CLI – commands: /add <filepath>, /search <query>, /quit")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line.startswith("/add"):
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                print("Usage: /add <filepath>")
                continue
            path = parts[1]
            if not os.path.isfile(path):
                print(f"File not found: {path}")
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                title = os.path.splitext(os.path.basename(path))[0]
                result = add_to_knowledge_base(content, title)
                print(result)
            except Exception as e:
                print(f"Error adding file: {e}")
        elif line.startswith("/search"):
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                print("Usage: /search <query>")
                continue
            query = parts[1]
            try:
                result = search_knowledge_base(query)
                print(result)
            except Exception as e:
                print(f"Search error: {e}")
        elif line in ("/quit", "/exit"):
            break
        else:
            print("Unknown command. Available: /add, /search, /quit")


if __name__ == "__main__":
    repl()
