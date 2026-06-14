from __future__ import annotations
"""Utilities for turning a raw log string into a list of ``ApiEvent`` objects.

The implementation relies on LangChain's *structured output* feature.  For each
log line (or block) we invoke an LLM that is instructed to return JSON matching
the ``ApiEvent`` discriminated union defined in :pymod:`models`.

If the LLM cannot be reached (missing API key, network error, etc.) a clear
exception is raised – the CLI catches this and prints a friendly message.
"""


import os
from typing import List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from models import ApiEvent

# Load environment variables from a ``.env`` file if present.
load_dotenv()


def _get_llm() -> ChatOpenAI:
    """Create a ``ChatOpenAI`` instance.

    The function reads ``OPENAI_API_KEY`` from the environment.  If the key is not
    set we raise a ``RuntimeError`` with an explanatory message – this keeps the
    rest of the code clean and makes the failure mode obvious to the user.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set.  Please create a .env file with your OpenAI "
            "API key or export the variable before running the CLI."
        )
    # ``model`` defaults to gpt‑3.5‑turbo which is sufficient for the simple schema.
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


def _split_log(log_text: str) -> List[str]:
    """Split the raw log into individual blocks.

    The assignment allows splitting by newline or by a ``---`` separator.  We
    treat both uniformly: first split on ``---`` and then on newlines, discarding
    empty fragments.
    """
    # Normalise line endings and split on the explicit separator.
    parts = log_text.replace("\r\n", "\n").split("---")
    blocks: List[str] = []
    for part in parts:
        for line in part.strip().split("\n"):
            line = line.strip()
            if line:
                blocks.append(line)
    return blocks


def parse_log(log_text: str) -> List[ApiEvent]:
    """Parse *log_text* and return a list of validated ``ApiEvent`` objects.

    The function:

    1. Splits the input into separate lines/blocks.
    2. Sends each block to the LLM using ``with_structured_output``.
    3. Validates the LLM response against the ``ApiEvent`` union.
    4. Returns the collection of successfully parsed events.
    """
    llm = _get_llm()
    # ``with_structured_output`` decorates the LLM so that it returns a Pydantic model.
    structured_llm = llm.with_structured_output(ApiEvent)

    events: List[ApiEvent] = []
    for block in _split_log(log_text):
        try:
            # The LLM expects a prompt – we simply pass the raw log line.
            result = structured_llm.invoke(block)
            # ``result`` is already an instance of ``ApiEvent`` thanks to the
            # structured output wrapper.
            events.append(result)
        except ValidationError as ve:
            # If the LLM output does not conform to the schema we surface a
            # readable error but continue processing the remaining blocks.
            raise RuntimeError(
                f"Validation failed for block: {block!r}\nDetails: {ve}\n"
                "Ensure the LLM returns a JSON object with a correct 'kind' field."
            ) from ve
        except Exception as exc:
            # Catch any other LangChain / network errors.
            raise RuntimeError(
                f"Failed to process block: {block!r}.\nError: {exc}"
            ) from exc
    return events
