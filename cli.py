import sys
from src.graph import build_graph
from src.state import ReflectState


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <question>")
        sys.exit(1)
    question = sys.argv[1]
    initial_state: ReflectState = {
        "question": question,
        "draft": "",
        "critique": "",
        "verdict": "",
        "round": 0,
        "max_rounds": 2
    }
    graph = build_graph()
    final_state = graph.run(initial_state)
    print("\nFinal Answer:\n", final_state["draft"])

if __name__ == "__main__":
    main()
