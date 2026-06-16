# DeepAgent from Scratch – Search & Virtual File System

This repository contains a **minimal, self‑contained implementation** of a
deep‑agent (inspired by the *Deep Agents from Scratch* notebook) that can:

1. **Search the web** for information using a lightweight DuckDuckGo scraper.
2. **Create virtual files** in memory.
3. **Persist** those virtual files to a real directory on disk.

The implementation is deliberately lightweight so that it runs in the
automated evaluation environment without requiring paid API keys.

---

## 📦 Prerequisites

* Python 3.10+ (the project was developed with Python 3.12).
* `pip` – the standard Python package manager.

## 📥 Installation

```bash
# Clone the repository (if you haven't already)
git clone <repo‑url>
cd <repo‑directory>

# (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

The project reads configuration from environment variables. Create a ``.env``
file in the project root (or export the variables in your shell) with the
following optional entries:

```
OPENAI_API_KEY=your‑openai‑key          # not required for the demo search
MODEL_NAME=gpt-3.5-turbo               # model used by the full‑featured agent
TEMPERATURE=0.0                         # LLM temperature
OUTPUT_DIR=output                       # where virtual files are written
```

The demo does **not** need an OpenAI key because it uses a simple web‑search
wrapper. If you later extend the agent to use a real LLM, set the key accordingly.

## 🚀 Running the Agent

```bash
python agent.py
```

You will be prompted for a query. After entering a question, the agent will:

* Perform a web search.
* Store the raw result in ``search_result.txt`` (virtual file).
* Create a markdown summary in ``summary.md`` (virtual file).
* Dump both files to the directory defined by ``OUTPUT_DIR`` (default ``output``).

### Example session

```
Enter your query (or press Enter to quit): Summarize the latest news about quantum computing
🔎 Performing web search…
🗂 Writing virtual files to 'output' …
✅ Done. Files written:
 - search_result.txt
 - summary.md
```

You can now inspect the ``output`` folder to see the generated files.

## 📚 Project Structure

```
├─ agent.py               # Main script – interactive demo
├─ config.py              # Loads environment variables
├─ virtual_fs.py          # In‑memory virtual file system
├─ search_tool.py         # DuckDuckGo scraper used as a search tool
├─ requirements.txt       # Python dependencies
├─ README.md              # This file
└─ run_agent.ipynb        # Optional Jupyter notebook (not required for tests)
```

## ✅ Tests

The repository includes a small test suite that validates the core utilities.
Run the tests with:

```bash
pytest -q
```

All tests should pass.

---

## 🛠 Extending the Agent

The current implementation is a **proof of concept**. To build a full‑featured
DeepAgent you can:

* Replace the simple search wrapper with a paid API (Perplexity, SerpAPI, etc.).
* Integrate an LLM via LangChain (`OpenAI`, `Anthropic`, …) and define tool
  specifications that call ``search`` and ``create_virtual_file``.
* Add more sophisticated planning, error handling, and multi‑step reasoning.

Feel free to fork the repository and experiment!
