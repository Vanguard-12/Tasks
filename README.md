# Interactive LLM‑Powered Adventure Game

This repository contains a minimal **choose‑your‑own‑adventure** console application that demonstrates

* calling an LLM (via **LangChain** / **ChatOpenAI**) to generate a story hook and three possible actions,
* pausing execution with a **LangGraph interrupt**,
* letting a human pick an option using **questionary**, and
* resuming the graph to let the LLM write a short ending.

## How it works

1. **State definition** – `StoryState` (theme, hook, options, user_choice, ending).
2. **Graph node** – a single node (`story_node`) that:
   * on the first call generates the hook & options and returns `interrupt(payload)`;
   * on resume receives the payload with the user's answer, stores it, calls the LLM again and returns the updated state.
3. **Checkpointing** – the graph is compiled with `InMemorySaver` so the thread can be resumed after the interrupt.
4. **Execution loop** – `adventure_main.py` starts the stream, detects the `__interrupt__` chunk, shows the question via `questionary.select`, adds the answer to the payload and resumes the graph.
5. **Result** – after the graph finishes the final state is printed: hook → chosen action → generated ending.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your OpenAI API key
```

## Running the adventure

```bash
python adventure_main.py
```

You will be asked for a theme (default *space cat*). The LLM will produce a short hook and three actions. Choose one, and the LLM will finish the story.

## Dependencies

- `langgraph`
- `langchain`
- `langchain-openai`
- `questionary`
- `python-dotenv` (optional, for loading the API key from `.env`)

Make sure the environment variable `OPENAI_API_KEY` is set (either in your shell or in the `.env` file).
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