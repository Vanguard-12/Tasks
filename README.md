# Research Brief Agent (LangGraph)

This repository contains a small **LangGraph**‑based agent that builds a short research brief for a student‑provided topic.

## What the agent does
1. **Outline generation** – an LLM creates a 4‑5 item outline for the topic.
2. **Iterative research** – for each outline point the agent performs **one** Tavily web‑search and summarises the results into a 5‑8 sentence note.
3. **Synthesis** – all notes are combined into a coherent brief (≈½‑1 page) with headings.

The whole pipeline is demonstrated by the `brief_agent.py` script.

---

## Installation
```bash
git clone <repo‑url>
cd <repo‑directory>
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration
Create a `.env` file in the project root with the required API keys:
```
TAVILY_API_KEY=your_tavily_key_here
OPENAI_API_KEY=your_openai_key_here   # optional if you use OpenAI
```
If you prefer a local LLM (e.g., Ollama) you can adjust the `ChatOpenAI`
initialisation in `brief/nodes.py`.

## Running the demo
```bash
python brief_agent.py
```
The script prints:
* the generated outline,
* each research note prefixed with its step number,
* the final synthesized brief.

You can change the topic by setting the environment variable `BRIEF_TOPIC` before running the script:
```bash
BRIEF_TOPIC="Your custom topic" python brief_agent.py
```

---

## Project structure
```
brief/                # package containing the LangGraph workflow
│   state.py          # TypedDict defining the workflow state
│   nodes.py          # LLM & Tavily node implementations
│   graph.py          # construction of the StateGraph
brief_agent.py        # entry‑point script that runs the graph
requirements.txt      # Python dependencies
README.md              # this file
```

## Notes & troubleshooting
* **Missing API keys** – the script will raise an error if `TAVILY_API_KEY` (or `OPENAI_API_KEY` when using OpenAI) is not set.
* **Rate limits** – Tavily imposes rate limits; if you hit them, wait a few seconds and retry.
* **LLM model** – the code uses `gpt-3.5-turbo`. You can switch to another model by changing the `model` argument in `ChatOpenAI` calls.

---

## License
This example code is provided for educational purposes and is released under the MIT License.
