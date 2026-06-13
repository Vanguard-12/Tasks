import argparse
from app import run_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="LangGraph Code Review Demo")
    parser.add_argument(
        "--rounds",
        type=int,
        default=2,
        help="Maximum number of revision rounds (default: 2)",
    )
    args = parser.parse_args()
    # The demo currently uses a fixed max_rounds; we could expose it via env or a config.
    # For simplicity, we just run the demo.
    run_demo()


if __name__ == "__main__":
    main()
