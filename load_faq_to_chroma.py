import os
from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

DATA_DIR = Path(__file__).parent / "data"
CHROMA_DIR = Path(__file__).parent / "chroma_faq"


def load_faq_to_chroma() -> Chroma:
    """Load all markdown files from the ``data`` directory, split them into chunks,
    embed them with the Ollama ``nomic-embed-text`` model and persist a Chroma collection.

    Returns:
        The instantiated :class:`~langchain_community.vectorstores.Chroma` object.
    """
    # Gather markdown files
    md_files = list(DATA_DIR.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No markdown files found in {DATA_DIR}")

    # Read and concatenate content
    docs = []
    for file_path in md_files:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            docs.append(text)

    # Split into manageable chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.create_documents(docs)

    # Create embeddings (requires Ollama server with the model pulled)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Initialise / persist Chroma collection
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    # Ensure persistence on disk
    vectorstore.persist()
    return vectorstore


if __name__ == "__main__":
    print("Loading FAQ documents into Chroma...")
    store = load_faq_to_chroma()
    print(f"Chroma collection persisted at: {CHROMA_DIR}")
    print(f"Number of vectors stored: {store._collection.count()}")
