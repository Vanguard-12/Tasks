from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_text(text: str, title: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
    """Split *text* into chunks and attach metadata.

    Each returned dict has the shape:
        {
            "content": <chunk string>,
            "metadata": {"title": <title>, "chunk_index": <int>}
        }
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(text)
    return [
        {
            "content": chunk,
            "metadata": {"title": title, "chunk_index": idx},
        }
        for idx, chunk in enumerate(chunks)
    ]
