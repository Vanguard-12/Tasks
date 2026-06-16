from __future__ import annotations
"""Utilities for turning raw log lines into :class:`ApiEvent` objects.

The implementation relies on LangChain's *structured output* feature.  A small
prompt is sent to the LLM together with the ``with_structured_output`` helper
that automatically validates the response against the ``ApiEvent`` discriminated
union defined in :pymod:`event_models`.
"""


import os
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from event_models import ApiEvent

# ---------------------------------------------------------------------------
# LLM configuration
# ---------------------------------------------------------------------------

def _get_llm() -> ChatOpenAI:
    """Create a ChatOpenAI instance.

    The function reads the ``OPENAI_API_KEY`` environment variable (or any other
    configuration that ``langchain-openai`` supports).  Temperature is set to 0
    to obtain deterministic JSON output.
    """

    # ``model`` can be overridden via an env variable if needed.
    model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    return ChatOpenAI(model=model_name, temperature=0)


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that converts a single log line into a JSON object that matches the provided schema. "
            "Return ONLY the JSON object, no extra text.",
        ),
        (
            "human",
            "Log line: {log_line}\n\nReturn the JSON representation of the event.",
        ),
    ]
)


def _parse_one_line(line: str) -> ApiEvent:
    """Parse a single log line using the LLM.

    Parameters
    ----------
    line:
        Raw log line (already stripped).

    Returns
    -------
    ApiEvent
        An instance of either :class:`HttpOkEvent` or :class:`HttpErrorEvent`.
    """

    chain = _PROMPT | _get_llm().with_structured_output(ApiEvent)
    # ``invoke`` returns a validated Pydantic model.
    result: ApiEvent = chain.invoke({"log_line": line})
    return result


def split_log(text: str) -> List[str]:
    """Split raw log text into individual non‑empty lines.

    The assignment mentions that events may be separated by newlines or a
    ``---`` delimiter.  This helper treats both uniformly – it first splits on
    ``---`` and then on newlines, discarding empty fragments.
    """

    # First split on the explicit delimiter, then flatten the result.
    parts = []
    for block in text.split("---"):
        for line in block.splitlines():
            stripped = line.strip()
            if stripped:
                parts.append(stripped)
    return parts


def parse_log(text: str) -> List[ApiEvent]:
    """Parse an entire log (multiple lines) into a list of ``ApiEvent`` objects.
    """

    lines = split_log(text)
    events: List[ApiEvent] = []
    for line in lines:
        try:
            event = _parse_one_line(line)
            events.append(event)
        except Exception as exc:  # pragma: no cover – defensive, not expected in tests
            # In a real‑world tool we would log the error; here we simply skip.
            print(f"[WARN] Failed to parse line: {line!r} – {exc}")
    return events
