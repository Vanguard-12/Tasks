from __future__ import annotations
"""Command‑line interface for the *Structured Output – Union* demo.

Run the module directly::

    python -m event_cli

or with a custom log::

    python -m event_cli --log "200 GET /api/users 123ms\n404 GET /api/unknown Not Found"

The script parses each line with the LLM, validates the result against the
Pydantic models and prints a tidy table.
"""


import argparse
import sys
from typing import List, Any

from tabulate import tabulate

from event_parser import parse_log
from event_models import ApiEvent

# ---------------------------------------------------------------------------
# Helper to turn a Pydantic model into a flat row for ``tabulate``
# ---------------------------------------------------------------------------

def _event_to_row(event: ApiEvent) -> List[Any]:
    base = {
        "kind": getattr(event, "kind", ""),
        "path": getattr(event, "path", ""),
        "status": getattr(event, "status", ""),
    }
    # ``duration_ms`` exists only for ok events, ``error_message`` only for error.
    if event.__class__.__name__ == "HttpOkEvent":
        base["duration_ms"] = getattr(event, "duration_ms", "")
        base["error_message"] = ""
    else:
        base["duration_ms"] = ""
        base["error_message"] = getattr(event, "error_message", "")
    # Preserve column order.
    return [
        base["kind"],
        base["path"],
        base["status"],
        base["duration_ms"],
        base["error_message"],
    ]


def _default_log() -> str:
    return """200 GET /api/users 123ms
404 GET /api/unknown Not Found
500 POST /api/create Internal Server Error"""


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Parse raw HTTP logs into structured events using LangChain.")
    parser.add_argument(
        "--log",
        type=str,
        help="Raw log text. If omitted a built‑in example is used.",
    )
    args = parser.parse_args(argv)

    raw_log = args.log if args.log is not None else _default_log()
    events: List[ApiEvent] = parse_log(raw_log)

    if not events:
        print("No events parsed.")
        sys.exit(0)

    headers = ["kind", "path", "status", "duration_ms", "error_message"]
    rows = [_event_to_row(ev) for ev in events]
    print(tabulate(rows, headers=headers, tablefmt="github"))


if __name__ == "__main__":
    main()
