import os
from pathlib import Path
from typing import List

from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader

CHROMA_DIR = "./chroma_faq"
DATA_DIR = Path(__file__).parent / "data"


def _load_documents() -> List:
    docs = []
    for md_path in DATA_DIR.glob("*.md"):
        loader = TextLoader(str(md_path))
        docs.extend(loader.load())
    return docs


def load_faq_to_chroma() -> Chroma:
    """Load markdown FAQ files, split, embed with Ollama and persist to ChromaDB."""
    os.makedirs(CHROMA_DIR, exist_ok=True)
    documents = _load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(
        collection_name="faq_collection",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    return vectorstore
