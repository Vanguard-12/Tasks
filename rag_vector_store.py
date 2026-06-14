import os
from typing import List

from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain.schema import Document


def _get_qdrant_client() -> QdrantClient:
    """Create a Qdrant client using environment variables or defaults."""
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    return QdrantClient(host=host, port=port)


def get_vector_store() -> QdrantVectorStore:
    """Initialize (or retrieve) the Qdrant vector store.

    The collection will be created automatically if it does not exist.
    """
    client = _get_qdrant_client()
    collection_name = os.getenv("QDRANT_COLLECTION", "rag_collection")
    embedding_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    embeddings = OllamaEmbeddings(model=embedding_model)
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embeddings=embeddings,
    )
    return vector_store


def add_documents(docs: List[Document]) -> None:
    """Add a list of Document objects to the vector store."""
    store = get_vector_store()
    store.add_documents(docs)


def search(query: str, k: int = 5) -> List[Document]:
    """Perform a similarity search in the vector store.

    Returns a list of Document objects ordered by relevance.
    """
    store = get_vector_store()
    return store.similarity_search(query, k=k)
