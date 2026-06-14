# Structured Output Extraction with LangChain & Pydantic

## Overview

This repository contains a small command‑line tool that demonstrates **structured output** extraction using **LangChain** (>= 1.0) and **Pydantic**.  Given a single raw text, the tool automatically decides whether the text describes a **person** or a **meeting**, extracts the relevant information via a LangChain chain (`PromptTemplate → LLM → PydanticOutputParser`), and prints a validated Pydantic model.

## Features

- Two Pydantic models (`PersonInfo` and `MeetingNotes`) with field‑level `Field(description=…)`.
- Heuristic router that selects the appropriate schema based on keyword scoring.
- LangChain chain built with `PydanticOutputParser` (no manual string parsing).
- CLI (`structured_cli.py`) that works with built‑in examples or piped/stdin input.
- Pretty‑printed JSON output (`model_dump()`) and a short human‑readable summary.

## Installation

```bash
# Clone the repository
git clone <repo_url>
cd <repo_dir>

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

The tool uses the OpenAI chat models via `langchain-openai`.  You need an OpenAI API key set in the environment:

```bash
export OPENAI_API_KEY='sk-...'
```

Alternatively, you can switch to an Ollama‑compatible model by editing `structured_output/extractor.py`.

## Usage

### Run with built‑in examples

```bash
python structured_cli.py
```
You will be prompted to choose between a *person* example and a *meeting* example.

### Pipe custom text

```bash
echo "Иван, 35 лет, Data‑Scientist. Навыки: Pandas, NumPy, TensorFlow." | python structured_cli.py
```
Or simply run the script and paste your text when prompted.

### Expected output (person example)

```json
{
  "name": "Анна",
  "age": 28,
  "profession": "Python-разработчик",
  "skills": [
    "FastAPI",
    "Docker"
  ]
}

Summary: Анна (28), Python-разработчик, skills: FastAPI, Docker
```

## Project Structure

```
structured_output/
├── models.py          # Pydantic models
├── prompts.py         # PromptTemplate builder
├── extractor.py       # Chain builder (Prompt → LLM → Parser)
├── router.py          # Heuristic schema selector

structured_cli.py      # CLI entry point
README.md
requirements.txt
```

## Dependencies

- `langchain-core`
- `langchain-openai` (or `langchain-ollama` if you prefer a local model)
- `pydantic`
- `python-dotenv` (optional, for loading `.env` files)

All versions are compatible with Python 3.10+.

## License

This project is provided for educational purposes and is licensed under the MIT License.
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
