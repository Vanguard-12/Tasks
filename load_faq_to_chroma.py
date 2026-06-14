import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


def load_faq_to_chroma(data_dir: str = "data", persist_dir: str = "chroma_faq"):
    """Load all markdown files from *data_dir* into a Chroma vector store.

    The documents are split into chunks, embedded with the Ollama
    `nomic-embed-text` model, and persisted to *persist_dir*.
    """
    # Gather raw texts
    docs = []
    for path in Path(data_dir).glob("*.md"):
        with open(path, "r", encoding="utf-8") as f:
            docs.append(f.read())
    if not docs:
        print(f"No markdown files found in {data_dir}.")
        return

    # Split into manageable chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text("\n".join(docs))

    # Create embeddings using Ollama
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Build and persist the Chroma collection
    vectordb = Chroma.from_texts(chunks, embeddings, persist_directory=persist_dir)
    vectordb.persist()
    print(f"Loaded {len(chunks)} chunks into Chroma at {persist_dir}")


if __name__ == "__main__":
    load_faq_to_chroma()
