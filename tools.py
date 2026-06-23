from langchain.tools import tool
from vector_store import VectorStore

vector_store = VectorStore()

@tool("Search the knowledge base")
def search_knowledge_base(query: str, max_results: int = 5) -> str:
    """Return the top documents for a query."""
    results = vector_store.search(query, k=max_results)
    return "\n".join([
        f"{i+1}. {r.metadata.get('title', 'Untitled')}\n{r.page_content}"
        for i, r in enumerate(results)
    ])

@tool("Add a document to the knowledge base")
def add_to_knowledge_base(content: str, title: str) -> str:
    """Add a new document to the knowledge base."""
    vector_store.add_documents([content], [title])
    return f"Document '{title}' added successfully."
