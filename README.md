# Deep Agent with Web Search and Virtual File System

This repository contains a **self‑contained DeepAgent** built from the *Deep Agents from Scratch* tutorial. The agent can:

1. Perform a web search using a simple DuckDuckGo scraper.
2. Create **virtual files** in an in‑memory file system.
3. When the agent decides it is finished, it flushes all virtual files to a real `output/` directory on disk.

## Setup

```bash
# Clone the repo and cd into it
git clone <repo-url>
cd <repo-dir>

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -U pip setuptools wheel
pip install -r requirements.txt
```

You need an **OpenAI API key** for the LLM. Create a `.env` file in the project root (or set the environment variable directly):

```
OPENAI_API_KEY=sk-...
```

The agent uses the OpenAI `gpt-4o-mini` model by default. You can change the model in `config.py`.

## Running the Agent

```bash
python agent.py "Summarize recent advances in quantum computing and save the summary to a file"
```

The script will:

- Initialise the DeepAgent.
- Perform a web search.
- Ask the LLM to write the summary to a virtual file.
- When the LLM calls the special `finalize` tool, the virtual files are written to the `output/` folder.

You should see a new file inside `output/` containing the generated summary.

## Project Structure

- `agent.py` – entry point that builds and runs the DeepAgent.
- `virtual_file_system.py` – in‑memory file system implementation.
- `search_tool.py` – lightweight DuckDuckGo scraper used as the `search` tool.
- `config.py` – configuration constants and environment loading.
- `tests/` – unit tests for the VFS and the search wrapper.

## Tests

```bash
pytest -q
```

All tests should pass.

## Security Notes

- The virtual file system sanitises paths and only allows writing inside the designated `output/` directory.
- No external files are touched unless they are inside `output/`.

---

*This project is a minimal, educational implementation of a DeepAgent. For production use you would replace the simple DuckDuckGo scraper with a proper search API (SerpAPI, Bing, Perplexity, etc.) and add more robust error handling.*