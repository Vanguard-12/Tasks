# FAQ‑Bot with ChromaDB + MCP‑style tool

This repository contains a minimal **FAQ‑bot** that answers questions about a course using two data sources:

1. **Local markdown FAQ files** stored in a persistent **ChromaDB** vector store.
2. A **mock MCP‑style HTTP tool** that returns schedule / metadata information.

The bot decides which source to use based on simple keyword routing and always appends a line `source: chroma` or `source: mcp_meta` to the answer.

---

## Prerequisites

- Python **3.10+**
- **Ollama** installed and running (required for the `nomic-embed-text` embedding model). See https://ollama.com/ for installation instructions.
- The Ollama model must be pulled:

```bash
ollama pull nomic-embed-text
```

## Setup

```bash
# Clone the repo and navigate into it
git clone <repo-url>
cd <repo-directory>

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 1. Load the FAQ data into Chroma

```bash
python load_faq_to_chroma.py
```

This script reads all ``*.md`` files from the ``data/`` directory, splits them into chunks, creates embeddings with Ollama's ``nomic-embed-text`` model and persists the vector store to ``chroma_faq/``.

## 2. Start the mock MCP server

The mock server simply serves a static JSON file with schedule information.

```bash
python -m http.server --directory mock_server 8000 &
# The server will be reachable at http://localhost:8000/metadata.json
```

## 3. Run the CLI

```bash
python cli.py
```

The CLI will:

1. Ask three preset questions (two should hit the Chroma FAQ, one should hit the MCP tool).
2. Enter an interactive REPL where you can type arbitrary questions.

Each answer ends with a ``source:`` line indicating which backend was used.

---

## Project structure

```
├─ data/                     # Sample markdown FAQ files
│   ├─ faq1.md
│   ├─ faq2.md
│   └─ faq3.md
├─ mock_server/              # Static JSON served by the mock HTTP server
│   └─ metadata.json
├─ load_faq_to_chroma.py     # Loads markdown into ChromaDB
├─ tools.py                  # Wrapper around Chroma search and MCP mock tool
├─ agent.py                  # Simple routing logic and answer formatter
├─ cli.py                    # Command‑line interface
├─ requirements.txt          # Python dependencies
└─ README.md                 # This file
```

---

## Dependencies

The main packages are listed in ``requirements.txt``:

```
langchain
langchain-chroma
langchain-ollama
chromadb
httpx
python-dotenv
```

Feel free to add any additional packages you need.

---

## License

This project is provided for educational purposes and is released under the MIT License.
