import os
import os
from dotenv import load_dotenv

from agent import create_agent


def _print_welcome():
    print("""\nRAG Agent Demo (type 'exit' or 'quit' to stop)\n""")


def main():
    # Load environment variables from a .env file if present.
    load_dotenv()

    # Warn the user if the Tavily API key is missing – the web search tool will raise an error.
    if not os.getenv("TAVILY_API_KEY"):
        print("Warning: TAVILY_API_KEY not set – web search will fail.")

    agent = create_agent()
    _print_welcome()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not user_input:
            continue
        try:
            response = agent.run(user_input)
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"Error during processing: {e}")
            continue


if __name__ == "__main__":
    main()
