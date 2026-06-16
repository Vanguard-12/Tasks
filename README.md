# RAG Agent with ChromaDB & Tavily

## Overview

This repository contains a minimal **LangChain** based Retrieval‑Augmented Generation (RAG) agent that can:

1. **Search a local knowledge base** stored in **ChromaDB** (semantic vector store).
2. **Search the web** via the **Tavily** API.
3. **Automatically decide** which source to use for a given user query and include a clear source tag in the answer.

The implementation follows the exam specification:
* `vectorstore.py` – creates a persistent ChromaDB store with Ollama embeddings and loads documents from `documents/`.
* `tools.py` – two LangChain tools (`search_local_kb` and `web_search`).
* `agent.py` – builds a Zero‑Shot ReAct agent that routes queries to the appropriate tool.
* `main.py` – a simple REPL CLI.

---

## Prerequisites

* **Python 3.10+**
* **Ollama** installed and running locally (see https://ollama.com/).
* Pull the required Ollama models:

```bash
ollama pull llama3
ollama pull nomic-embed-text
```
* Obtain a **Tavily** API key – sign up at https://tavily.com/.

---

## Installation

```bash
# Clone the repo
git clone <repo_url>
cd <repo_dir>

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

Create a `.env` file from the example and add your Tavily key:

```bash
cp .env.example .env
# edit .env and replace the placeholder with your real key
```

---

## Indexing your documents

Place any ``.txt`` or ``.md`` files you want the agent to know about inside the `documents/` folder.
Then run the initialisation script:

```bash
python -m vectorstore init   # or: python vectorstore.py --dir documents
```

The script will:
* read all text/markdown files recursively,
* split them into 1 000‑character chunks (200‑character overlap),
* embed the chunks with Ollama's `nomic-embed-text` model,
* store the vectors in `./chroma_db` (persistent across runs).

---

## Running the interactive CLI

```bash
python main.py
```

You will see a prompt like:

```
RAG Agent Demo (type 'exit' or 'quit' to stop)
You:
```

Type any question. Examples:

* **Local knowledge** – "What does our lecture note say about LangGraph?"
* **Web‑search** – "What are the latest news about AI agents?"

The agent will automatically call the appropriate tool and print the answer, e.g.:

```
Agent: ... (answer)
[Source: chromadb]
```

or

```
Agent: ... (answer)
[Source: tavily]
```

---

## Troubleshooting

* **Ollama not running** – make sure the Ollama daemon is active (`ollama serve`).
* **Missing TAVILY_API_KEY** – the web‑search tool will raise an error; set the variable in `.env`.
* **Permission errors on `./chroma_db`** – ensure the directory is writable.
* **No results** – verify that your documents folder contains `.txt`/`.md` files and that they were indexed (`python -m vectorstore init`).

---

## License

This project is provided for educational purposes and is released under the MIT License.
