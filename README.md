# Comparative Review Agent (LangGraph + Tavily)

## Overview

This repository contains a **LangGraph** workflow that, given three entities (e.g., technologies, products, or approaches), automatically:

1. **Generates comparison criteria** using an LLM.
2. **Performs web searches** for every *entity × criterion* pair via the **Tavily** search API.
3. **Aggregates the findings** into a markdown table (rows = criteria, columns = entities).
4. **Produces a concise verdict** – a short recommendation about which entity is best for which use‑case.

The whole process can be executed from the command line.

---

## Setup

1. **Clone the repository** and navigate into it.
   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```

2. **Create a virtual environment** (optional but recommended).
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```

3. **Install dependencies**.
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**.
   ```bash
   cp .env.example .env
   ```
   Edit the newly created ``.env`` file and add your **Tavily API key** (you can obtain one at https://tavily.com).  Optionally set ``OPENAI_MODEL`` if you want to use a model other than the default ``gpt-3.5-turbo``.

5. **(Optional) OpenAI credentials** – the ``langchain-openai`` package reads the standard OpenAI environment variables (``OPENAI_API_KEY`` etc.).  Make sure they are set if you want the LLM parts to work.

---

## Usage

Run the demo with the default entities (Chroma, FAISS, Qdrant):
```bash
python -m src.cli
```

You can also provide your own three entities:
```bash
python -m src.cli "Entity A" "Entity B" "Entity C"
```

The script will output:

* The **generated criteria**.
* The **research notes** for each entity‑criterion pair.
* A **markdown table** summarising the comparison.
* A **verdict** – a short recommendation.

---

## Project Structure

```
src/
├── __init__.py
├── cli.py               # command‑line interface
├── graph.py             # LangGraph workflow definition
├── state.py             # TypedDict defining the workflow state
└── nodes/
    └── compare.py       # implementations of the four nodes
requirements.txt          # Python dependencies
.env.example              # example environment file
README.md                 # this file
```

---

## Error Handling

* **Missing TAVILY_API_KEY** – the program will abort with a clear message.
* **Tavily request failures** – the corresponding note will contain an error description, and the workflow continues.
* **OpenAI errors** – the LLM nodes raise an exception; the CLI catches it and prints a helpful message.

---

## License

This project is provided for educational purposes and is released under the MIT License.
