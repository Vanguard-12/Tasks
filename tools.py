import json
import os
from pathlib import Path
from typing import List

import httpx
from langchain.schema import Document
from langchain_chroma import Chroma

# Assume the vectorstore has already been created by load_faq_to_chroma.py
CHROMA_DIR = "./chroma_faq"
VECTORSTORE = None


def _get_vectorstore() -> Chroma:
    global VECTORSTORE
    if VECTORSTORE is None:
        from langchain_ollama import OllamaEmbeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        VECTORSTORE = Chroma(
            collection_name="faq_collection",
            embedding_function=embeddings,
            persist_directory=CHROMA_DIR,
        )
    return VECTORSTORE


def search_course_docs(query: str, k: int = 3) -> List[Document]:
    """Search the persisted Chroma collection and return up to *k* documents."""
    vectorstore = _get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever.get_relevant_documents(query)


def fetch_course_meta(query: str) -> dict:
    """Mimic an MCP call.

    Tries to GET a local mock server; if it fails, falls back to reading ``mock_meta.json``.
    """
    url = "http://localhost:8000/mock_meta.json"
    try:
        resp = httpx.get(url, timeout=2.0)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        # fallback to static file
        path = Path(__file__).parent / "mock_meta.json"
        if path.is_file():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"error": "metadata not available"}
