import os
from pathlib import Path


def read_directory(directory: str) -> list[tuple[str, str]]:
    """Return list of (content, title) tuples for all text files in directory."""
    docs = []
    for path in Path(directory).rglob("*.txt"):
        with open(path, "r", encoding="utf-8") as f:
            docs.append((f.read(), path.stem))
    return docs


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> list[str]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)
