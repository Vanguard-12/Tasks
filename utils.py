from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

# Load environment variables from a .env file if present.
load_dotenv()


def get_llm() -> Any:
    """Create and return an LLM instance.

    Preference order:
    1. If ``OPENAI_API_KEY`` is set, use OpenAI's ChatOpenAI.
    2. Otherwise, if ``OLLAMA_BASE_URL`` and ``OLLAMA_MODEL`` are set, use Ollama.
    3. If neither is configured, raise a clear error.
    """

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        # The default model works for most quick demos.
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    ollama_url = os.getenv("OLLAMA_BASE_URL")
    ollama_model = os.getenv("OLLAMA_MODEL")
    if ollama_url and ollama_model:
        return Ollama(base_url=ollama_url, model=ollama_model, temperature=0)

    raise EnvironmentError(
        "No LLM configuration found. Set OPENAI_API_KEY for OpenAI or "
        "OLLAMA_BASE_URL and OLLAMA_MODEL for a local Ollama server."
    )
