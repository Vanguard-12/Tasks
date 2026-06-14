from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


def chunk_document(content: str, title: str) -> List[Document]:
    """Split raw text into manageable chunks and attach metadata.

    Each chunk becomes a ``Document`` with a ``title`` metadata field.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    # ``create_documents`` expects a list of strings and a list of metadata dicts.
    docs = splitter.create_documents([content], metadatas=[{"title": title}])
    return docs
