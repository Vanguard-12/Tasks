# Structured Output CLI Demo

This repository contains a small command‑line tool that demonstrates **structured output** extraction using **LangChain** and **Pydantic**.

## What it does

- Accepts a raw text describing either a **person** or a **meeting**.
- Automatically decides which schema fits the input.
- Uses a LangChain chain (`PromptTemplate → LLM → PydanticOutputParser`) to let the LLM generate a **validated** Pydantic object – no manual string parsing.
- Prints the object's `model_dump()` (pretty JSON) and a short human‑readable summary.

## Features required by the assignment

| Requirement | Implemented |
|-------------|-------------|
| Two Pydantic models with `Field(description=…)` | ✅ (`models.py`) |
| Extraction via `PydanticOutputParser` / `with_structured_output` | ✅ (`cli.py`) |
| Routing logic (person vs meeting) | ✅ (`router.py`) |
| CLI with built‑in examples and custom input | ✅ (`cli.py`) |
| Works with LangChain ≥ 1.0 | ✅ (`requirements.txt`) |

## Installation

```bash
# Clone the repo and cd into it
git clone <repo-url>
cd <repo-dir>

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy the example env file and add your OpenAI key (or configure Ollama)
cp .env.example .env
# edit .env and set OPENAI_API_KEY=your‑key
```

## Usage

```bash
# Run the interactive demo (shows two examples and lets you type your own text)
python cli.py

# Or pass a raw text directly as a command‑line argument
python cli.py "Анна, 28 лет, Python‑разработчик. Навыки: FastAPI, Docker."
```

The script will output something like:

```json
{
  "name": "Анна",
  "age": 28,
  "profession": "Python‑разработчик",
  "skills": ["FastAPI", "Docker"]
}
```

and a short summary:

```
Person: Анна, 28 y, Python‑разработчик, skills: FastAPI, Docker
```

## Files overview

- **models.py** – defines `PersonInfo` and `MeetingNotes`.
- **prompt_templates.py** – builds `PromptTemplate` objects that embed the parser's format instructions.
- **router.py** – simple keyword‑based router that selects the appropriate schema.
- **utils.py** – helper to create the LLM client from environment variables.
- **cli.py** – entry point, handles examples, argument parsing, routing, chain execution, and output.
- **requirements.txt** – required Python packages.
- **.env.example** – shows which environment variables are needed.

## Notes

- The LLM used is **OpenAI's `gpt-3.5‑turbo`** by default. If you prefer a local Ollama model, set `OLLAMA_BASE_URL` and `OLLAMA_MODEL` in `.env`.
- The router is deliberately simple (keyword heuristic) to keep the solution deterministic and fast.
- All fields in the Pydantic models have a `Field(description=…)` as required.
- Errors from the LLM (e.g., malformed JSON) are caught and displayed, allowing the user to retry with a different input.

---

© 2026 Generated for the exam task "Структурированный вывод (Pydantic)".
