import os
from typing import Any


def get_env_var(name: str, default: Any = None) -> Any:
    """Utility to fetch an environment variable with a helpful error.

    Args:
        name: Name of the variable.
        default: Value to return if the variable is missing. If ``None`` and the
            variable is missing, a ``RuntimeError`` is raised.
    """
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Environment variable '{name}' is required but not set.")
    return value
import os
import json
from typing import Any
from dotenv import load_dotenv

# Load .env automatically when this module is imported
load_dotenv()


def get_env_var(name: str) -> str | None:
    """Return the value of an environment variable or ``None`` if not set."""
    return os.getenv(name)


def get_llm():
    """Create a LangChain chat model based on available credentials.

    Preference order:
    1. ``OPENAI_API_KEY`` → ``ChatOpenAI``
    2. ``OLLAMA_BASE_URL`` → ``ChatOllama``
    Raises a clear ``RuntimeError`` if neither is configured.
    """
    from langchain_openai import ChatOpenAI
    from langchain_ollama import ChatOllama

    openai_key = get_env_var("OPENAI_API_KEY")
    ollama_url = get_env_var("OLLAMA_BASE_URL")

    if openai_key:
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    elif ollama_url:
        return ChatOllama(base_url=ollama_url, model="llama3.1:8b", temperature=0.2)
    else:
        raise RuntimeError(
            "No LLM configuration found. Set either OPENAI_API_KEY or OLLAMA_BASE_URL in .env"
        )


def safe_json_parse(text: str) -> Any:
    """Parse *text* as JSON, raising a helpful error if it fails.

    The LLM sometimes returns stray backticks or markdown fences – we strip them.
    """
    # Remove common markdown fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse JSON from LLM output: {exc}\nOriginal output: {text}")
