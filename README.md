# Structured Output – Union Events Demo

This repository contains a small command‑line tool that demonstrates **structured
output with a discriminated Union** using **Pydantic v2** and **LangChain ≥1.0**.

## What it does

* Takes a raw HTTP log (multiple lines, each possibly of a different format).
* Sends each line to an LLM (OpenAI Chat model) with `with_structured_output` so the
  model returns JSON that matches one of the two Pydantic schemas:
  * `HttpOkEvent` – successful request (`status` = 200).
  * `HttpErrorEvent` – error request (4xx/5xx).
* The returned JSON is validated against a **discriminated Union** (`ApiEvent`).
* The CLI prints a tidy table showing the parsed events.

## Project structure

```
├─ main.py          # CLI entry point
├─ models.py        # Pydantic models + discriminated Union
├─ parser.py        # Splitting log, invoking LLM, validation
├─ requirements.txt # Dependencies
├─ README.md        # This file
└─ .env (optional) # Store your OpenAI API key
```

## Setup

1. **Clone the repository** and navigate into it.
2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Provide an OpenAI API key** (or configure an Ollama endpoint).  The simplest
   way is to create a `.env` file in the project root:
   ```dotenv
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   The `python-dotenv` package automatically loads this file.

## Usage

Run the CLI without arguments to parse the built‑in example log:

```bash
python main.py
```

You can also supply your own log text via the `--log` flag:

```bash
python main.py --log "GET /api/users 200 duration=120ms\nPOST /api/orders 500 error='DB failure'"
```

### Expected output (example)

```
| kind   | path          | status   | duration_ms   | error_message          |
|--------|---------------|----------|---------------|------------------------|
| ok     | /api/users    | 200      | 123           | -                      |
| error  | /api/orders   | 500      | -             | Internal Server Error |
| ok     | /health       | 200      | 5             | -                      |
```

## How it works

* **`models.py`** defines two concrete Pydantic models (`HttpOkEvent` and
  `HttpErrorEvent`) and combines them into a discriminated Union `ApiEvent`
  using `Field(discriminator="kind")`.
* **`parser.py`** splits the raw log, creates a `ChatOpenAI` instance, decorates it
  with `with_structured_output(ApiEvent)`, and invokes the model for each block.
  The LLM response is automatically parsed into the appropriate Pydantic class.
* **`main.py`** orchestrates the flow, handling errors gracefully and printing a
  table with the `tabulate` library.

## Notes & troubleshooting

* **Missing API key** – the program will exit with a clear message asking you to
  set `OPENAI_API_KEY`.
* **LLM validation errors** – if the model returns JSON that does not match the
  schema (e.g., missing `kind`), a `RuntimeError` with details is raised.
* **Running locally without OpenAI** – you can replace `ChatOpenAI` with a
  compatible local model (e.g., `ChatOllama`) by editing `parser._get_llm()`.

---

Enjoy experimenting with structured output and discriminated unions!
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
