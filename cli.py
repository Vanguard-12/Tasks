import sys
from agent import answer_question

PRESET_QUESTIONS = [
    "What are the basic data types in Python?",
    "How do I import a module in Python?",
    "What is the schedule for the course?",
]


def run_demo():
    print("--- FAQ‑Bot demo ---\n")
    for q in PRESET_QUESTIONS:
        print(f"User: {q}")
        print(f"Bot: {answer_question(q)}\n")


def interactive_loop():
    print("Enter your questions (type 'exit' or press Ctrl‑D to quit).\n")
    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not user_input.strip():
            continue
        answer = answer_question(user_input)
        print(f"Bot: {answer}\n")


if __name__ == "__main__":
    run_demo()
    interactive_loop()
