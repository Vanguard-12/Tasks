# Simple Hierarchical AI Agent with LangChain

This repository contains a minimal example of a **hierarchical AI agent** built with LangChain.

## What it does
- Accepts a user request for a shopping list.
- For each product it calls a tool `get_price`.
- `get_price` creates a **sub‑agent** that generates a realistic price (as a Markdown table) using a local LLM (LM Studio).
- The main agent aggregates the results and prints a final table with the total cost.

## Prerequisites
- **LM Studio** running locally and exposing an OpenAI‑compatible API at `http://localhost:1234/v1`.
- Python 3.10+.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the script
```bash
python agent.py
```
You should see a sequence of tool calls followed by a final answer, e.g.:
```
get_price({'product': 'молоко', 'city': 'Казань'})
get_price({'product': 'хлеб', 'city': 'Казань'})
get_price({'product': 'яблоки', 'city': 'Казань'})
| Продукт | Цена (руб.) | Магазин |
|---------|-------------|---------|
| Молоко  | 89          | Магнит  |
| Хлеб    | 45          | Пятёрочка |
| Яблоки  | 120/кг      | Перекрёсток |
**Итого:** ~254 руб.
```

If the LLM server is not reachable, the script will print a clear error message and exit gracefully.
