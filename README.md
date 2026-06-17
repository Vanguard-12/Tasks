# Structured Output – Union of API Events

## Description

This small project demonstrates how to parse a raw log (multiple lines of different formats) into a list of **typed API event objects** using **Pydantic v2** and **LangChain structured output**.  The solution showcases:

* Discriminated Union with `kind` field (`"ok"` / `"error"`).
* Automatic parsing of each log line via an LLM (OpenAI or Ollama) using `PydanticOutputParser`.
* A command‑line interface that prints the parsed events in a nice table.

## Installation

```bash
pip install -r requirements.txt
```

> **Note**: To use the OpenAI model you need an `OPENAI_API_KEY` environment variable.  If it is not set the code falls back to an Ollama model (default `llama3`) or a tiny dummy LLM that works without any external service.

## Usage

```bash
# Run the CLI with the built‑in example log
python -m event_cli

# Provide your own log text (as a single argument or via stdin)
python -m event_cli "GET /api/users 200 123ms\nPOST /api/items 404 Not Found"
```

The CLI prints a table similar to:

```
kind   path          status   duration_ms   error_message
------ ------------- ------- ------------- --------------------------
ok     /api/users    200      123
error  /api/items    404                     Not Found
```

## Project Structure

* `event_models.py` – Pydantic models (`HttpOkEvent`, `HttpErrorEvent`) and the discriminated Union `ApiEvent`.
* `event_parser.py` – Functions to split the raw log and parse each block using LangChain structured output.
* `event_cli.py` – CLI entry point that ties everything together.
* `requirements.txt` – Required third‑party packages.
* `README.md` – This documentation.
