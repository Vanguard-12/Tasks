import sys
import json

from structured_output.router import get_chain_for_text


def main():
    # Determine input source
    if not sys.stdin.isatty():
        raw_text = sys.stdin.read().strip()
    else:
        # No piped input – show interactive examples
        example_person = "Анна, 28 лет, Python-разработчик. Навыки: FastAPI, Docker."
        example_meeting = (
            "Встреча 12.09.2024. Участники: Иван, Мария, Сергей. Темы: бюджет, сроки. "
            "Решения: увеличить бюджет на 10%. Следующие шаги: подготовить отчет, согласовать с руководством."
        )
        print("No input detected. Choose an example to run:")
        print("1) Person example")
        print("2) Meeting example")
        choice = input("Enter 1 or 2 (default 1): ").strip()
        raw_text = example_meeting if choice == "2" else example_person

    chain, model_cls = get_chain_for_text(raw_text)
    try:
        result = chain.invoke({"input_text": raw_text})
        # result is a Pydantic model instance
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        # Simple human‑readable summary
        if model_cls.__name__ == "PersonInfo":
            summary = f"{result.name} ({result.age or 'N/A'}), {result.profession}, skills: {', '.join(result.skills)}"
        else:
            summary = f"Meeting on {result.date} with {', '.join(result.participants)}. Topics: {', '.join(result.topics)}."
        print("\nSummary:", summary)
    except Exception as exc:
        print("Error during extraction:", exc)
        # If the LLM returned malformed JSON, the parser raises a ValidationError.
        # We surface the error without crashing.
        if hasattr(exc, "args"):
            print("Details:", exc.args)


if __name__ == "__main__":
    main()
