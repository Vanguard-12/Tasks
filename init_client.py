import argparse
import os

from rag_tools import add_to_knowledge_base


def load_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description="Load documents from a directory into the RAG knowledge base.")
    parser.add_argument("--source_dir", type=str, required=True, help="Directory containing text documents to ingest.")
    args = parser.parse_args()

    for root, _, files in os.walk(args.source_dir):
        for file_name in files:
            if file_name.startswith('.'):
                continue
            file_path = os.path.join(root, file_name)
            try:
                content = load_file(file_path)
                title = os.path.splitext(file_name)[0]
                result = add_to_knowledge_base(content, title)
                print(f"[+] {file_path}: {result}")
            except Exception as exc:
                print(f"[!] Failed to load {file_path}: {exc}")

if __name__ == "__main__":
    main()
