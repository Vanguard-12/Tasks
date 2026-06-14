import argparse
from pathlib import Path

from rag_tools import add_to_knowledge_base


def _load_file(file_path: Path) -> None:
    """Read a file and add its content to the knowledge base.

    Supports plain text files (``.txt``) and markdown files (``.md``).
    """
    title = file_path.stem
    content = file_path.read_text(encoding="utf-8")
    add_to_knowledge_base(content, title)


def load_documents_from_dir(source_dir: Path) -> None:
    """Recursively walk ``source_dir`` and ingest supported files."""
    for path in source_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            _load_file(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load documents into the RAG knowledge base")
    parser.add_argument("--source_dir", type=str, required=True, help="Directory containing documents to ingest")
    args = parser.parse_args()
    load_documents_from_dir(Path(args.source_dir))


if __name__ == "__main__":
    main()
