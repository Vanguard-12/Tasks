from __future__ import annotations

import argparse

from vectorstore import create_vectorstore, load_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Load .txt and .md files into ChromaDB.")
    parser.add_argument("directory", nargs="?", default="documents")
    parser.add_argument("--persist-directory", default="./chroma_db")
    args = parser.parse_args()

    vectorstore = create_vectorstore(args.persist_directory)
    count = load_documents(args.directory, vectorstore)
    print(f"Loaded {count} chunks into ChromaDB at {args.persist_directory}")


if __name__ == "__main__":
    main()
