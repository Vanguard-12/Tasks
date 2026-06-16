from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from langchain_core.output_parsers import PydanticOutputParser

from models import PersonInfo, MeetingNotes
from prompt_templates import PERSON_TEMPLATE, MEETING_TEMPLATE
from router import choose_schema
from utils import get_llm

EXAMPLE_PERSON = (
    "Анна, 28 лет, Python‑разработчик. Навыки: FastAPI, Docker."
)
EXAMPLE_MEETING = (
    "Встреча 2024‑11‑02. Участники: Иван, Мария, Олег. Темы: план продукта, бюджет. "
    "Решения: утвердить дорожную карту. Следующие шаги: подготовить прототип, "
    "согласовать сроки."
)


def build_chain(text: str, schema: str) -> Any:
    """Create a LangChain runnable chain for the given schema.

    Parameters
    ----------
    text: str
        Raw input text.
    schema: "person" | "meeting"
        Which Pydantic model to use.
    """

    llm = get_llm()
    if schema == "person":
        parser = PydanticOutputParser(pydantic_object=PersonInfo)
        prompt = PERSON_TEMPLATE
    else:
        parser = PydanticOutputParser(pydantic_object=MeetingNotes)
        prompt = MEETING_TEMPLATE

    # The prompt expects the format instructions and the raw text.
    chain = (
        prompt
        | llm
        | parser
    )
    return chain


def summarize(obj: Any) -> str:
    """Return a short human‑readable summary for the given Pydantic object."""
    if isinstance(obj, PersonInfo):
        skills = ", ".join(obj.skills)
        age_part = f", {obj.age} y" if obj.age is not None else ""
        return f"Person: {obj.name}{age_part}, {obj.profession}, skills: {skills}"
    if isinstance(obj, MeetingNotes):
        participants = ", ".join(obj.participants)
        topics = ", ".join(obj.topics)
        decisions = ", ".join(obj.decisions)
        steps = ", ".join(obj.next_steps)
        return (
            f"Meeting on {obj.date} with {len(obj.participants)} participants ({participants}). "
            f"Topics: {topics}. Decisions: {decisions}. Next steps: {steps}."
        )
    return "Unknown object"


def run_extraction(text: str) -> None:
    schema = choose_schema(text)
    chain = build_chain(text, schema)
    try:
        result = chain.invoke({"text": text, "format_instructions": chain.prompt.format_instructions})
    except Exception as exc:
        print("❌ Extraction failed:", exc, file=sys.stderr)
        sys.exit(1)

    # ``result`` is already a validated Pydantic model.
    print("\n=== Structured Output ===")
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    print("\n=== Summary ===")
    print(summarize(result))


def interactive_menu() -> None:
    print("Select an example or press Enter to provide your own text:\n")
    print("1) Person example")
    print("2) Meeting example")
    choice = input("Enter 1 or 2 (or just press Enter): ").strip()
    if choice == "1":
        text = EXAMPLE_PERSON
    elif choice == "2":
        text = EXAMPLE_MEETING
    else:
        print("\nEnter your raw text (finish with an empty line):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        text = "\n".join(lines)
    print("\n--- Input Text ---\n", text, "\n--- End of Input ---\n")
    run_extraction(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Structured output extraction demo")
    parser.add_argument(
        "text",
        nargs="?",
        help="Raw text to process. If omitted, an interactive menu is shown.",
    )
    args = parser.parse_args()

    if args.text:
        run_extraction(args.text)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
