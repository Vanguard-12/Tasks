# LangGraph Comparative Review (Tavily)

## Overview
A LangGraph agent that, given three entities, automatically:
1. Generates 3‑5 comparison criteria via OpenAI LLM.
2. Searches the web for each *entity × criterion* pair using Tavily.
3. Builds a markdown table of findings.
4. Produces a short verdict recommending the best fit.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your TAVILY_API_KEY
```

## Usage
```bash
python main.py            # default comparison of Chroma, FAISS, Qdrant
python main.py --interactive   # enter your own three entities
```
The script prints the generated criteria, each research note, the markdown table, and the final verdict.
