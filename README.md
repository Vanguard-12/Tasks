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
