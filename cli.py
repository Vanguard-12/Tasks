import argparse
import sys
from typing import Optional

from router import SchemaRouter, get_summary

# Example texts used by the CLI.
PERSON_EXAMPLE = (
    "Анна, 28 лет, Python-разработчик. Навыки: FastAPI, Docker."
)
MEETING_EXAMPLE = (
    "Встреча 2024-09-15. Участники: Иван, Мария. Тема: бюджет, тайм‑лайн. "
    "Решение: утвердить бюджет. Следующие шаги: отправить отчёт."
)


def run_extraction(text: str):
    try:
        obj = SchemaRouter.run(text)
        print("\n--- Result ---")
        # Pretty‑print the model as JSON‑like dict.
        import json
        print(json.dumps(obj.model_dump(), indent=2, ensure_ascii=False))
        print("\nSummary:", get_summary(obj))
    except Exception as e:
        print("Error during extraction:", e, file=sys.stderr)


def main(argv: Optional[list] = None):
    parser = argparse.ArgumentParser(
        description="Extract structured data (PersonInfo or MeetingNotes) from raw text using LangChain and Pydantic."
    )
    parser.add_argument(
        "--example",
        choices=["person", "meeting"],
        help="Run the built‑in example for a person or a meeting.",
    )
    args = parser.parse_args(argv)

    if args.example == "person":
        print("Running PersonInfo example...\n")
        run_extraction(PERSON_EXAMPLE)
        return
    if args.example == "meeting":
        print("Running MeetingNotes example...\n")
        run_extraction(MEETING_EXAMPLE)
        return

    # No example selected – read from stdin / prompt.
    print("Enter text describing a person or a meeting (Ctrl‑D / Ctrl‑Z to finish):")
    try:
        user_input = sys.stdin.read().strip()
        if not user_input:
            # Fallback to interactive input line by line.
            user_input = input("> ")
    except EOFError:
        print("No input provided.", file=sys.stderr)
        return
    run_extraction(user_input)


if __name__ == "__main__":
    main()
