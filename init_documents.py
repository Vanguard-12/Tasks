import yaml
from utils import read_directory, chunk_text
from vector_store import VectorStore


def main():
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    vs = VectorStore()

    docs = read_directory("docs")
    for content, title in docs:
        chunks = chunk_text(content, chunk_size=500, chunk_overlap=100)
        vs.add_documents(chunks, [title] * len(chunks))


if __name__ == "__main__":
    main()
