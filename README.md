# LangGraph Code Review Reflection

LangGraph workflow that writes a Python code review, asks an LLM critic for one overall verdict, and rewrites the review when the verdict is `needs_revision`.

## Setup

```bash
pip install -r requirements.txt
```

Create `.env`:

```text
OPENAI_API_KEY=your_key
```

Optional:

```text
OPENAI_MODEL=gpt-4o-mini
```

## Run

```bash
python main.py
```

The demo reviews:

```python
def sort_numbers(arr):
    return sorted(arr)
```

The output shows the initial draft, the overall verdict, the critic feedback, and any rewritten review round.
