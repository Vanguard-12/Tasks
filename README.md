# Assignment Card Extractor

This tiny utility demonstrates how to turn a **single raw assignment description** into a **validated flat data card** using LangChain's structured‑output capabilities and a Pydantic model.

## Features

- **One‑shot processing** – the LLM receives the description and returns JSON/YAML that matches a schema.
- **Pydantic validation** – guarantees correct types (`str`, `list`, optional fields, …).
- **Human‑readable summary** – printed alongside the raw dictionary.

## Prerequisites

```bash
pip install -r requirements.txt python-dotenv
```

You also need an OpenAI API key (or any compatible provider). Put it into a ``.env`` file based on the provided ``.env.example``:

```dotenv
OPENAI_API_KEY=sk-...
```

## Usage

```bash
python parse_assignment.py "Сдайте к пятнице мини-отчёт по LangChain: 2 страницы, упор на агентов. Оценка: за полноту и за пример кода."
```

### Expected output (example)

```
--- Structured data (model_dump) ---
{'title': 'Мини‑отчёт по LangChain', 'subject': 'LangChain', 'deadline_hint': 'к пятнице', 'deliverable_type': 'отчёт', 'grading_hints': ['полнота', 'пример кода']}

--- Summary ---
Мини‑отчёт по LangChain – отчёт, срок: к пятнице, оценка по: полнота, пример к кода.
```

If the LLM returns data that does not conform to the schema, a validation error will be shown.

## How it works

1. **Pydantic model** (`AssignmentCard`) defines the required fields.
2. `PydanticOutputParser` generates format instructions that are injected into the prompt.
3. The prompt asks the model to output **only** the structured data.
4. LangChain chain (`prompt | llm | parser`) runs in a single pass.
5. The resulting `AssignmentCard` instance is printed via `model_dump()` and a short summary.

---

Feel free to adapt the model or prompt for your own educational‑assistant projects.
