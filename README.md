# RAG Agent With ChromaDB And Tavily

LangChain agent with local ChromaDB retrieval, Ollama LLM/embeddings, and Tavily web search.

## Setup

```bash
ollama pull llama3
ollama pull nomic-embed-text
pip install -r requirements.txt
```

Create `.env`:

```text
TAVILY_API_KEY=your_key
```

## Load Documents

```bash
python load_documents_cli.py documents
```

## Run

```bash
python main.py
```

The agent uses `search_local_kb` for local documents and `web_search` for current web facts. Final answers include `Источник: chromadb` or `Источник: tavily`.
