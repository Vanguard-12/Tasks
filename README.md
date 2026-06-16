# Human‑in‑the‑Loop (custom interrupt) demo

This repository contains a minimal example that demonstrates how to use **LangGraph**'s
custom interrupt / resume mechanism together with an interactive console prompt
(`questionary`).

## How it works

1. A `StateGraph` is built with a single node (`ask`).
2. The node raises a custom interrupt by calling `interrupt(payload)` where the
   payload contains:
   * `type` – a string identifying the interrupt type.
   * `question` – the text shown to the user.
   * `allow_responses` – a list of possible answers.
3. The script streams the graph. When a chunk with the key `__interrupt__` is
   received, the payload is extracted and presented to the user via
   `questionary.select`.
4. The chosen answer is added to the payload (`payload["answer"] = …`) and the
   graph is resumed with `Command(resume=payload)` using the same `thread_id`.
5. After resumption the node stores the answer in the graph state (`human_value`)
   and the workflow finishes. The final state is printed to the console.

## Running the demo

```bash
# Install dependencies (preferably in a virtual environment)
pip install -r requirements.txt

# Execute the example
python hitl_demo.py
```

You will see a prompt similar to:

```
? Are you sure you want to continue? (Use arrow keys)
❯ approve
  reject
```

After selecting an option the script prints the final state, e.g.:

```
--- Graph finished ---
Final state: {'human_value': 'approve'}
```

Feel free to adapt the payload, add more nodes, or integrate the pattern into a
larger LangGraph application.
# LangGraph Agent with Memory and Human‑in‑the‑Loop Confirmation

This repository contains a minimal scaffold for a LangGraph agent that demonstrates:

1. **Conversation memory** using `MemorySaver` with a configurable `thread_id`.
2. **Human‑in‑the‑loop (HITL) confirmation** before each tool invocation (`interrupt_before=['tools']`).
3. **Rich console output** for a nicer user experience.

## Files

- `app.py` – Entry point. Sets up the console and contains a placeholder `main` function. Replace the placeholder with the full agent implementation described in the assignment.
- `tools.py` – Example tool (`get_price`) that the agent can call. Extend with real logic as needed.
- `requirements.txt` – Project dependencies (`rich`, `langgraph`, `openai`).

## How to run

```bash
pip install -r requirements.txt
python app.py
```

The script currently prints a welcome message. Implement the full agent logic (memory, interrupt handling, streaming) inside `app.py` following the assignment instructions.
