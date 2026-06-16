# FAQ‑Bot with ChromaDB + a mock MCP‑style tool

This repository contains a minimal **FAQ‑bot** that answers questions about a course using two data sources:

1. **Local markdown FAQ files** – indexed with **ChromaDB** and queried via an embedding model (`nomic‑embed‑text` from Ollama).
2. **Course metadata** – fetched from a mock HTTP endpoint that mimics an MCP (Micro‑service Control Plane) tool.

The bot decides which source to use based on simple keyword routing and always appends a `source:` tag to the answer.

---

## Project structure

```
.
├─ data/                 # 2 markdown FAQ files (faq1.md, faq2.md)
├─ mock_data/            # static JSON served by a simple HTTP server
│   └─ meta.json
├─ chroma_faq/           # persisted Chroma collection (generated at runtime)
├─ load_faq_to_chroma.py # script that loads the markdown files into Chroma
├─ tools.py              # two tools: search_course_docs & fetch_course_meta
├─ agent.py              # routing logic + LLM prompt
├─ cli.py                # demo + interactive REPL
├─ requirements.txt     # Python dependencies
├─ .gitignore            # ignores __pycache__, .env, chroma_faq, etc.
└─ README.md             # you are reading it!
```

---

## Prerequisites

- **Python 3.10+**
- **Ollama** installed and running (see https://ollama.com/). Pull the embedding model:

```bash
ollama pull nomic-embed-text
```

- The required Python packages (see `requirements.txt`).

---

## Setup & usage

1. **Clone the repository** and navigate to the project root.

```bash
git clone <repo‑url>
cd <repo‑directory>
```

2. **Create a virtual environment** and install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Load the FAQ documents into Chroma** (this creates the `chroma_faq/` folder).

```bash
python load_faq_to_chroma.py
```

4. **Start the mock metadata server** in a separate terminal.

```bash
python -m http.server 8000 --directory mock_data
```
   The server will expose `http://localhost:8000/meta.json`.

5. **Run the CLI demo**.

```bash
python cli.py
```
   The script will:
   - Show three preset Q&A pairs (two answered from the FAQ, one from the metadata tool).
   - Enter an interactive REPL where you can ask any question.

---

## How it works

### 1. Loading FAQ data (`load_faq_to_chroma.py`)
- Reads all ``*.md`` files from the ``data`` directory.
- Splits each document into ~1 000‑character chunks (with 200‑character overlap) using LangChain's ``RecursiveCharacterTextSplitter``.
- Embeds the chunks with ``OllamaEmbeddings(model='nomic-embed-text')``.
- Stores the embeddings in a persistent Chroma collection located at ``./chroma_faq``.

### 2. Tools (`tools.py`)
- **`search_course_docs(query, k=3)`** – loads the persisted Chroma collection and returns the top‑k most relevant snippets.
- **`fetch_course_meta(key)`** – performs an HTTP GET against the mock endpoint (``http://localhost:8000/meta.json``) and returns the value for the requested key (e.g., ``schedule``). This mimics an MCP‑style external tool.

### 3. Agent (`agent.py`)
- Contains a tiny routing function that looks for *metadata‑related* keywords (schedule, time, instructor, etc.).
- Depending on the routing decision it calls either ``search_course_docs`` or ``fetch_course_meta``.
- The raw data is fed to an Ollama chat model (``llama3.1:8b`` by default) with a system prompt that instructs the model to format the answer and to add a ``source: chroma`` or ``source: mcp_meta`` line.

### 4. CLI (`cli.py`)
- Demonstrates the bot with three hard‑coded questions.
- Afterwards it starts an interactive loop where you can type any question.

---

## Extending the bot

- **Add more FAQ files** – simply drop additional ``*.md`` files into the ``data`` folder and re‑run ``load_faq_to_chroma.py``.
- **Improve routing** – replace the keyword‑based router with a small classifier model.
- **Real MCP integration** – swap the mock HTTP call in ``fetch_course_meta`` with a real MCP client.

---

## Troubleshooting

- **Embedding model not found** – make sure Ollama is running and the model ``nomic-embed-text`` is pulled.
- **Chroma collection missing** – run ``python load_faq_to_chroma.py`` before using the bot.
- **Metadata server connection error** – ensure the mock server is running on port 8000 (or set the ``META_URL`` environment variable to the correct address).

---

## License

This example project is provided for educational purposes and is released under the MIT License.
