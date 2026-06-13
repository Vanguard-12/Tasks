# LangGraph Comparative Review Demo (Tavily)

This repository contains a small **LangGraph**‑based agent that, given three
entities (technologies, products, approaches, …), automatically:

1. **Generates** 3‑5 comparison criteria using an LLM.
2. **Researches** each *entity × criterion* pair with a real web search via the
   **Tavily** API.
3. **Aggregates** the short notes into a markdown table (rows = criteria,
   columns = entities).
4. **Produces** a concise verdict – a 2‑4 sentence recommendation that tells
   which entity is best for which typical use‑case.

The whole workflow is expressed as a LangGraph state machine with a looping
node that iterates over all entity‑criterion combinations.

---

## Quickstart

```bash
# 1. Clone the repo and cd into it
git clone <repo-url>
cd <repo-directory>

# 2. Install dependencies (Python 3.10+ required)
python -m pip install -r requirements.txt

# 3. Create a .env file from the example and add your keys
cp .env.example .env
# edit .env and set TAVILY_API_KEY and OPENAI_API_KEY

# 4. Run the demo (default entities: Chroma, FAISS, Qdrant)
python -m cli
```

### Custom entities

You can compare any three items of your choice:

```bash
python -m cli --custom "Entity A" "Entity B" "Entity C"
```

---

## How it works

### State model (`compare_state.py`)
```python
class CompareState(TypedDict):
    entities: List[str]          # three names to compare
    criteria: List[str]          # generated comparison criteria
    findings: Dict[str, List[str]]  # entity -> list of notes (one per criterion)
    current_pair: int            # index of the next (entity, criterion) pair
    final_table: Optional[str]
    verdict: Optional[str]
```

### Nodes (`nodes.py`)
| Node | Purpose |
|------|---------|
| `plan_criteria` | Calls an LLM (OpenAI) to produce a JSON list of criteria. |
| `research_entity` | For the current pair builds a query, calls **Tavily**, extracts a short snippet and stores it. |
| `build_table` | Turns the collected notes into a markdown table. |
| `verdict` | Sends the table back to the LLM and receives a short recommendation. |

### Graph (`graph.py`)
The graph is a simple state machine:
```
START → plan_criteria → research_entity (loop) → build_table → verdict → END
```
The loop continues while ``current_pair < len(entities) * len(criteria)``.

---

## Project structure
```
compare_state.py   # TypedDict definition
nodes.py           # All node functions
graph.py           # LangGraph assembly
cli.py             # Command‑line interface
requirements.txt   # Dependencies
.env.example       # Example environment file
README.md          # This file
```

---

## License

This demo is provided under the MIT License.
