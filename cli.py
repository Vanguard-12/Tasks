import sys
from agent import answer_question


def _run_presets():
    preset_questions = [
        "What is the grading policy?",
        "How many lectures are there?",
        "When is the next lecture?",
    ]
    print("=== Preset questions ===")
    for q in preset_questions:
        print(f"\nQ: {q}")
        print(f"A: {answer_question(q)}")


def _interactive_loop():
    print("\n=== Interactive mode (type 'exit' or 'quit' to stop) ===")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if user_input.lower() in {"exit", "quit"}:
            break
        print(f"Bot: {answer_question(user_input)}")


def main():
    _run_presets()
    _interactive_loop()


if __name__ == "__main__":
    main()
