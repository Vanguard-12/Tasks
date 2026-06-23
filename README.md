# FAQ Bot with ChromaDB and a mock MCP tool

## Overview

This repository contains a minimal FAQ‑bot that answers questions about a course using two sources:

1. **Course documents** stored in a local ChromaDB vector store.
2. **Course metadata** (schedule, instructor, contact) fetched via a mock MCP‑style HTTP endpoint.

The bot decides which source to use automatically and always returns a JSON response that includes a `source` field (`"chroma"` or `"mcp_meta"`).

## Setup

```bash
# Python 3.10+ is required
pip install -r requirements.txt

# Pull the embedding model for Ollama
ollama pull nomic-embed-text
```

### Load the FAQ documents into ChromaDB

```bash
python -c "import load_faq_to_chroma; load_faq_to_chroma.load_faq_to_chroma()"
```

This will create a persisted Chroma collection in `./chroma_faq`.

### Run the mock MCP server (optional)

You can serve the static `mock_meta.json` with a simple HTTP server:

```bash
python -m http.server 8000 &
```

If the server is not running, the tool will fall back to reading the JSON file directly.

## Running the bot

```bash
python cli.py
```

The CLI will first answer three preset questions (two from the document store, one from the metadata tool) and then enter an interactive mode. Type `exit` or `quit` to stop.

## Production note

In a real‑world scenario the `fetch_course_meta` function would call an actual MCP server that provides course metadata. Here we use a static JSON file or a local mock HTTP endpoint for demonstration purposes.
