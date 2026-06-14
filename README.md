# Stream‑mode LangChain agent

This repository already contains a fairly large LangChain demo.  The
assignment for the *Stream‑режим AI‑агента* requires that the agent be executed
with the **streaming** interface (`.stream()`) instead of the one‑shot
`.invoke()` call.

The original scripts (`agent.py`, `shopping_agent.py`, …) used the blocking
`invoke` method, which returns the whole answer only after the LLM finishes its
generation.  To make the response appear token‑by‑token we added a new entry
point – **`agent_stream.py`** – that:

1. Builds the same ReAct‑style agent (the same tools, same system prompt).
2. Calls `executor.stream(..., stream_mode=["messages", "updates"])`.
3. Iterates over the returned chunks and prints them immediately:
   * **`messages`** – prints each token (`print(..., end="")`).
   * **`updates`** – prints tool‑call information when the model finishes a
     step.
4. Inserts a visual separator (`--- --- ---`) whenever the internal
   `langgraph_step` changes, exactly as described in the task.

Running the script:

```bash
python agent_stream.py "Сколько стоит молоко в Казани?"
```

You will see the assistant’s answer flowing in the console, with tool calls
shown in the same format as the previous non‑streaming version.

The rest of the repository (tests, other agents, etc.) remains unchanged.
# Human‑in‑the‑loop (interrupt / resume) demo

This repository contains a minimal example of a **LangGraph** workflow that pauses execution with a custom interrupt, asks the user a question in the console, and then resumes the graph using the provided answer.

## How it works

1. **State definition** – a simple `TypedDict` with a single field `human_value` that will hold the answer supplied by the user.
2. **Interrupt node** – the node calls `interrupt({...})` with a payload containing:
   * `type` – a string identifier (e.g., `"confirm"`).
   * `question` – the text shown to the user.
   * `options` – a list of possible answers.
   When the graph is resumed the same payload (now enriched with an `answer` key) is passed back to the node, which stores the answer in the state.
3. **Graph compilation** – the graph is compiled with an `InMemorySaver` checkpoint so that the execution can be resumed after the interrupt.
4. **Execution loop** – the script streams the graph. When a chunk contains the special key `"__interrupt__"` it extracts the payload, displays the question using `questionary.select`, captures the answer, adds it to the payload, and resumes the graph with `Command(resume=payload)`.
5. **Result** – after the graph finishes, the final state is printed, showing the user‑provided value.

## Run the demo

```bash
pip install -r requirements.txt
python main.py
```

You will see a prompt like:

```
? Are you sure you want to continue? (Use arrow keys)
❯ approve
  reject
```

After selecting an option the script prints the final state, e.g.:

```
Final state: {'human_value': 'approve'}
```

Feel free to adapt the payload, add more nodes, or integrate this pattern into larger LangGraph applications.
