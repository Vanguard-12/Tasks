from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    return Chroma(
        collection_name="local_knowledge_base",
        embedding_function=OllamaEmbeddings(model="nomic-embed-text"),
        persist_directory=persist_directory,
    )


def load_documents(directory: str, vectorstore: Chroma) -> int:
    root = Path(directory)
    if not root.exists():
        raise FileNotFoundError(f"Documents directory does not exist: {directory}")

    documents: list[Document] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                documents.append(Document(page_content=text, metadata={"source": str(path)}))

    if not documents:
        return 0

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(documents)
    vectorstore.add_documents(chunks)
    return len(chunks)
