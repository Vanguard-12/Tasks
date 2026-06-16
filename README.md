# RAG Agent with Qdrant & Ollama

## Overview

This repository implements a simple Retrieval‑Augmented Generation (RAG) system using:
- **Qdrant** – vector store for semantic search
- **Ollama** – local LLM (`llama3`) and embedding model (`nomic-embed-text`)
- **LangChain** – tools, agents and utilities

The system provides two LangChain tools:
1. `add_to_knowledge_base(content, title)` – splits a document into chunks, creates embeddings and stores them in Qdrant.
2. `search_knowledge_base(query, max_results)` – performs a semantic search and returns the most relevant chunks.

An agent is built that automatically calls these tools when it needs factual information.

## Setup

### 1. Install Ollama models
```bash
ollama pull llama3
ollama pull nomic-embed-text
```
Make sure the Ollama daemon is running (`ollama serve`).

### 2. Run Qdrant (Docker)
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```
The service will be reachable at `localhost:6333`.

### 3. Install Python dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configuration (optional)
Edit **config.yaml** if you need to change host/port or model names.

## Loading documents

Use the helper script to ingest all files from a directory:
```bash
python init_client.py --source_dir ./documents
```
Each file is read, split into chunks (default 1 000 characters) and stored in the Qdrant collection.

## Interactive CLI

Run the REPL to add new files or search the knowledge base on the fly:
```bash
python cli.py
```
Commands:
- `/add <filepath>` – ingest a new document.
- `/search <query>` – retrieve the most relevant chunks.
- `/quit` – exit.

## Using the Agent

You can also interact with the agent directly (it will call the tools automatically):
```bash
python agent.py
```
Type any question; the agent will search the knowledge base when needed and respond.

## Project structure
```
├─ config.yaml               # connection & model settings
├─ requirements.txt          # Python packages
├─ vector_store.py           # Qdrant wrapper + embedding logic
├─ chunker.py                # Text splitter
├─ rag_tools.py              # @tool‑decorated functions
├─ agent.py                  # LangChain agent with system prompt
├─ init_client.py            # Bulk document loader
├─ cli.py                    # Interactive REPL
└─ README.md                 # This file
```

## License

This educational example is provided under the MIT license.
