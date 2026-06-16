import os
from pathlib import Path
from typing import List

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader


def create_vectorstore(persist_directory: str = "./chroma_db"):
    """Create (or load) a Chroma vector store using Ollama embeddings.

    The store is persisted to ``persist_directory`` so that data survives
    across program runs.
    """
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    return vectorstore


def _load_files_from_directory(directory: str) -> List:
    """Read *.txt and *.md files from *directory* and return a list of Documents."""
    docs = []
    path_obj = Path(directory)
    for file_path in path_obj.rglob("*"):
        if file_path.suffix.lower() == ".txt":
            loader = TextLoader(str(file_path))
        elif file_path.suffix.lower() == ".md":
            loader = UnstructuredMarkdownLoader(str(file_path))
        else:
            continue
        docs.extend(loader.load())
    return docs


def load_documents(directory: str, vectorstore: Chroma) -> None:
    """Load documents from *directory* into *vectorstore*.

    The function performs recursive character splitting (chunk size 1000, overlap 200)
    before adding the chunks to the vector store. After insertion the store is
    persisted to disk.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Directory '{directory}' does not exist.")

    raw_docs = _load_files_from_directory(directory)
    if not raw_docs:
        print(f"No .txt or .md files found in '{directory}'.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(raw_docs)
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    print(f"Loaded {len(chunks)} chunks from '{directory}' into ChromaDB.")


if __name__ == "__main__":
    # Simple CLI to initialise the vector store with documents.
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Initialise ChromaDB with documents.")
    subparsers = parser.add_subparsers(dest="command")

    # "init" command – load documents from a directory into the vector store.
    init_parser = subparsers.add_parser("init", help="Load documents into ChromaDB")
    init_parser.add_argument(
        "--dir",
        type=str,
        default="documents",
        help="Directory containing .txt/.md files to index.",
    )

    # If no subcommand is provided, show help and exit.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if args.command == "init":
        store = create_vectorstore()
        load_documents(args.dir, store)
