import os

from vectorstore import create_vectorstore, load_documents


def main():
    # Create (or load) the persistent vector store.
    vs = create_vectorstore()
    # Directory that contains the markdown / txt files.
    docs_dir = os.getenv("DOCS_DIR", "documents")
    print(f"Loading documents from '{docs_dir}' into ChromaDB …")
    load_documents(docs_dir, vs)
    print("Done. Documents indexed and persisted.")


if __name__ == "__main__":
    main()
