import os
from pathlib import Path
from typing import List

from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document


def create_vectorstore(persist_directory: str = "./chroma_db"):
    """Create (or load) a Chroma vector store with Ollama embeddings.

    The store persists to ``persist_directory`` so that documents are kept
    between program runs.
    """
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(
        collection_name="documents",
        embedding_function=embedding,
        persist_directory=persist_directory,
    )
    return vectorstore


def load_documents(directory: str, vectorstore: Chroma):
    """Read ``.txt`` and ``.md`` files from *directory*, split them into chunks
    and add them to *vectorstore*.

    The function uses a ``RecursiveCharacterTextSplitter`` with a chunk size of
    1000 characters and an overlap of 200 characters – a reasonable default for
    most short‑form documents.
    """
    path_obj = Path(directory)
    if not path_obj.is_dir():
        raise ValueError(f"Directory '{directory}' does not exist.")

    raw_docs: List[Document] = []
    for file_path in path_obj.rglob("*"):
        if file_path.suffix.lower() in {".txt", ".md"} and file_path.is_file():
            try:
                text = file_path.read_text(encoding="utf-8")
            except Exception as exc:
                raise RuntimeError(f"Failed to read {file_path}: {exc}")
            raw_docs.append(Document(page_content=text, metadata={"source": str(file_path)}))

    if not raw_docs:
        # Nothing to load – silently return.
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(raw_docs)
    vectorstore.add_documents(split_docs)
    # Persist the collection so that it survives restarts.
    vectorstore.persist()
