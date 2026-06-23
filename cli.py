import sys

from agent import build_agent, answer_query


def main():
    agent = build_agent()
    preset_questions = [
        "What topics are covered in the course?",
        "How should I submit assignments?",
        "When is the next class?",
    ]
    print("--- Preset queries ---")
    for q in preset_questions:
        print(f"\nQ: {q}")
        print("A:")
        print(answer_query(agent, q))
    print("\n--- Interactive mode (type 'exit' to quit) ---")
    while True:
        try:
            user_input = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.strip().lower() in {"exit", "quit"}:
            break
        print("Bot:")
        print(answer_query(agent, user_input))

if __name__ == "__main__":
    main()
