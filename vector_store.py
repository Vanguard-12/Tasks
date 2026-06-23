import yaml
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings

class VectorStore:
    def __init__(self, config_path: str = "config.yaml") -> None:
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)

        qdrant_cfg = cfg["qdrant"]
        self.store = QdrantVectorStore.from_params(
            url=f"{qdrant_cfg['host']}:{qdrant_cfg['port']}",
            collection_name=qdrant_cfg["collection_name"],
            embedding=OllamaEmbeddings(
                model=cfg["embedding_model"],
                base_url=cfg["ollama"]["host"],
            ),
        )

    def add_documents(self, documents: list[str], titles: list[str]) -> None:
        metadatas = [{"title": t} for t in titles]
        self.store.add_texts(documents, metadatas=metadatas)

    def search(self, query: str, k: int = 5) -> list[object]:
        return self.store.similarity_search(query, k=k)
