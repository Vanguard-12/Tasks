"""Utility functions for splitting raw logs and parsing them into structured events.

The parsing relies on LangChain's ``with_structured_output`` helper which wraps an LLM
so that it returns a Pydantic model (our ``ApiEvent`` discriminated union).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from models import ApiEvent


def split_log(text: str) -> List[str]:
    """Split a raw log string into individual event blocks.

    The function treats a blank line or a line consisting solely of ``---`` as a
    delimiter.  It also strips surrounding whitespace from each block and discards
    empty blocks.
    """
    lines = text.splitlines()
    blocks: List[str] = []
    current: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "" or stripped == "---":
            if current:
                blocks.append("\n".join(current).strip())
                current = []
            continue
        current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return blocks


def _get_llm() -> ChatOpenAI:
    """Create a ChatOpenAI instance.

    The function reads the ``OPENAI_API_KEY`` environment variable.  If the variable
    is missing, a clear ``RuntimeError`` is raised so that the CLI can present a
    helpful message to the user.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found in environment. Please set it in a .env file or the shell."
        )
    # ``temperature=0`` makes the model deterministic which is useful for parsing.
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)


def parse_block(block: str, llm: ChatOpenAI) -> ApiEvent | None:
    """Parse a single log block into an ``ApiEvent``.

    The function uses ``llm.with_structured_output`` to enforce the Pydantic schema.
    If validation fails, the error is logged and ``None`` is returned.
    """
    structured_llm = llm.with_structured_output(ApiEvent)
    try:
        # The LLM expects a dictionary of inputs; we provide the raw block under the key ``input``.
        result = structured_llm.invoke({"input": block})
        return result  # type: ignore[return-value]
    except ValidationError as ve:
        # Validation errors mean the LLM output didn't match the schema.
        print(f"[validation error] Could not parse block:\n{block}\nError: {ve}")
        return None
    except Exception as exc:  # pragma: no cover – generic safeguard
        print(f"[llm error] Unexpected error while parsing block:\n{block}\nError: {exc}")
        return None


def parse_log(text: str) -> List[ApiEvent]:
    """Parse an entire raw log into a list of ``ApiEvent`` objects.

    Empty or unparsable blocks are skipped, but a warning is printed for each.
    """
    llm = _get_llm()
    blocks = split_log(text)
    events: List[ApiEvent] = []
    for block in blocks:
        event = parse_block(block, llm)
        if event:
            events.append(event)
    return events
