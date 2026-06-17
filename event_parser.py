from __future__ import annotations

import json
import os
from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

# Try to import LLM classes; fall back to a dummy implementation if no API key is present.
try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover
    ChatOpenAI = None

try:
    from langchain_ollama import ChatOllama
except Exception:  # pragma: no cover
    ChatOllama = None

from event_models import ApiEvent


class DummyLLM:
    """A very small stand‑in LLM that creates JSON based on simple heuristics.

    This class exists so that the package can be used without an external LLM service.
    It does **not** use regular expressions for status detection – it simply checks for
    the presence of the string ``"200"`` to decide the kind.
    """

    def invoke(self, prompt: str) -> str:
        # The prompt contains the original log line after a marker "<<LOG>>".
        # Extract the line.
        marker = "<<LOG>>"
        if marker in prompt:
            line = prompt.split(marker, 1)[1].strip()
        else:
            line = prompt.strip()

        # Very naive parsing – split by spaces.
        parts = line.split()
        # Expect something like: METHOD PATH STATUS [optional extra]
        # Find the first part that looks like a status code (numeric).
        status = None
        path = None
        for i, part in enumerate(parts):
            if part.isdigit():
                status = int(part)
                if i > 0:
                    path = parts[i - 1]
                break
        if status is None:
            # default to error with status 0
            status = 0
            path = parts[1] if len(parts) > 1 else "/"

        if status == 200:
            # ok event – try to get duration (look for a number followed by 'ms')
            duration = 0
            for part in parts:
                if part.endswith("ms") and part[:-2].isdigit():
                    duration = int(part[:-2])
                    break
            result = {
                "kind": "ok",
                "status": 200,
                "path": path,
                "duration_ms": duration,
            }
        else:
            # error event – everything after status is the message
            msg_index = parts.index(str(status)) + 1
            error_message = " ".join(parts[msg_index:]) if msg_index < len(parts) else ""
            result = {
                "kind": "error",
                "status": status,
                "path": path,
                "error_message": error_message,
            }
        return json.dumps(result)


def _get_llm():
    """Return an LLM instance.

    Preference order:
    1. OpenAI (requires ``OPENAI_API_KEY``)
    2. Ollama (local model, defaults to ``llama3``)
    3. DummyLLM (no external service)
    """
    if ChatOpenAI is not None and os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-3.5-turbo")
    if ChatOllama is not None:
        # Ollama runs locally; we use the default model.
        return ChatOllama(model="llama3")
    return DummyLLM()


# Prompt that tells the LLM to output JSON matching the ApiEvent schema.
_PROMPT_TEMPLATE = PromptTemplate.from_template(
    """You are given a raw log line. Extract the information and output a JSON object that conforms to the following Pydantic schema:\n\n{schema}\n\nLog line (after the marker):\n<<LOG>>\n{log_line}\n"""
)


def _parse_block(block: str, llm) -> ApiEvent:
    """Parse a single log block into an ``ApiEvent`` using LangChain structured output.

    The function builds a prompt with the block, calls the LLM, and then uses
    ``PydanticOutputParser`` to convert the JSON string into a typed model.
    """
    # Build the prompt – we embed the schema for clarity.
    schema_str = ApiEvent.__doc__ or ""
    prompt = _PROMPT_TEMPLATE.format(schema=str(ApiEvent), log_line=block)
    raw_output = llm.invoke(prompt)
    parser = PydanticOutputParser(ApiEvent)
    return parser.parse(raw_output)


def split_blocks(text: str) -> List[str]:
    """Split the raw log text into individual blocks.

    Blocks are separated by newlines; empty lines are ignored.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines


def parse_events(text: str) -> List[ApiEvent]:
    """Parse the entire log text into a list of ``ApiEvent`` objects.

    The function:
    1. Splits the text into blocks.
    2. Parses each block with the LLM + ``PydanticOutputParser``.
    3. Returns the list of typed events.
    """
    llm = _get_llm()
    blocks = split_blocks(text)
    events: List[ApiEvent] = []
    for block in blocks:
        try:
            event = _parse_block(block, llm)
            events.append(event)
        except Exception as exc:  # pragma: no cover
            # If parsing fails, we skip the block but keep the process alive.
            print(f"Failed to parse block: {block!r}. Error: {exc}")
    return events
