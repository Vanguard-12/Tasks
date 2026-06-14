import os
from typing import List, Tuple

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


def _get_llm() -> ChatOpenAI:
    """Create a ChatOpenAI instance using the OPENAI_API_KEY from the environment.
    The function isolates model creation so it can be reused in both generation steps.
    """
    # The model name can be adjusted; we use a cheap, fast model for the demo.
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)


def generate_scene(theme: str) -> Tuple[str, List[str]]:
    """Generate a short story hook and exactly three action options.

    The LLM is prompted to return the result in a strict format so that parsing is reliable.
    Expected format:
        Hook: <hook text>
        Options:
        1) <option 1>
        2) <option 2>
        3) <option 3>
    """
    llm = _get_llm()
    prompt = (
        f"Theme: {theme}\n"
        "Create a short story hook (2‑3 sentences) and exactly three possible actions for the hero. "
        "Respond in the following format:\n"
        "Hook: <hook text>\n"
        "Options:\n"
        "1) <option 1>\n"
        "2) <option 2>\n"
        "3) <option 3>"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    text = response.content

    # Parse the response.
    hook = ""
    options: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("hook:"):
            hook = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("1)") or stripped.startswith("2)") or stripped.startswith("3)"):
            # Remove the leading number and parenthesis.
            option = stripped.split(")", 1)[1].strip()
            options.append(option)
    # Fallback parsing if the strict format was not respected.
    if not hook or len(options) != 3:
        parts = [p.strip() for p in text.split("\n") if p.strip()]
        hook = parts[0] if parts else ""
        options = parts[1:4] if len(parts) >= 4 else []
    return hook, options


def generate_ending(hook: str, choice: str) -> str:
    """Generate a short ending based on the hook and the user's choice."""
    llm = _get_llm()
    prompt = (
        f"Hook: {hook}\n"
        f"User chose: {choice}\n"
        "Write a short ending (2‑3 sentences) that follows from this choice."
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()
