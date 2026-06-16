import os
import yaml
from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from langchain_ollama import OllamaEmbeddings

# Load configuration ----------------------------------------------------------
CONFIG_PATH = os.getenv("RAG_CONFIG", "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

qdrant_cfg = cfg.get("qdrant", {})
host = qdrant_cfg.get("host", "localhost")
port = qdrant_cfg.get("port", 6333)
collection_name = qdrant_cfg.get("collection_name", "rag_collection")

ollama_cfg = cfg.get("ollama", {})
embedding_model = ollama_cfg.get("embedding_model", "nomic-embed-text")

# Initialise Qdrant client ---------------------------------------------------
client = QdrantClient(host=host, port=port)

# Ensure collection exists ----------------------------------------------------
# We lazily determine the vector size by creating a dummy embedding.
embeddings = OllamaEmbeddings(model=embedding_model)
_dummy_vec = embeddings.embed_query("dummy")
vector_size = len(_dummy_vec)

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=qdrant_models.VectorParams(size=vector_size, distance=qdrant_models.Distance.COSINE),
    )

# Helper functions ------------------------------------------------------------

def _embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using Ollama."""
    return embeddings.embed_documents(texts)


def add_documents(docs: List[Dict]):
    """Add a list of documents (chunks) to the Qdrant collection.

    Each document dict must contain:
        - "content": the text chunk
        - "metadata": a dict with at least a "title" and "chunk_index"
    """
    if not docs:
        return
    texts = [doc["content"] for doc in docs]
    vectors = _embed_texts(texts)
    payloads = [doc.get("metadata", {}) for doc in docs]
    client.upload_collection(
        collection_name=collection_name,
        vectors=vectors,
        payload=payloads,
        ids=None,  # let Qdrant generate IDs
    )


def search(query: str, top_k: int = 5) -> List[Dict]:
    """Perform a semantic search and return the most relevant documents.

    Returns a list of dicts with keys "content" and "metadata".
    """
    query_vec = embeddings.embed_query(query)
    hits = client.search(
        collection_name=collection_name,
        query_vector=query_vec,
        limit=top_k,
        with_payload=True,
        with_vectors=False,
    )
    results = []
    for hit in hits:
        payload = hit.payload or {}
        results.append({
            "content": hit.payload.get("content", "") if isinstance(hit.payload, dict) else "",
            "metadata": payload,
        })
    return results
