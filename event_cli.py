from __future__ import annotations

import argparse
import sys
from typing import List

from tabulate import tabulate

from event_models import ApiEvent
from event_parser import parse_events

DEFAULT_LOG = """
GET /api/users 200 123ms
POST /api/items 404 Not Found
GET /api/pay 500 Internal Server Error
"""


def _event_to_row(event: ApiEvent) -> List[str]:
    """Convert an ``ApiEvent`` instance into a list of table cells.

    The columns are: kind, path, status, duration_ms, error_message.
    Missing fields are rendered as an empty string.
    """
    base = {
        "kind": getattr(event, "kind", ""),
        "path": getattr(event, "path", ""),
        "status": getattr(event, "status", ""),
    }
    # ``duration_ms`` exists only on ok events, ``error_message`` only on error events.
    if hasattr(event, "duration_ms"):
        base["duration_ms"] = getattr(event, "duration_ms", "")
    else:
        base["duration_ms"] = ""
    if hasattr(event, "error_message"):
        base["error_message"] = getattr(event, "error_message", "")
    else:
        base["error_message"] = ""
    return [
        str(base["kind"]),
        str(base["path"]),
        str(base["status"]),
        str(base["duration_ms"]),
        str(base["error_message"]),
    ]


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Parse raw API logs into typed events and display a table.",
    )
    parser.add_argument(
        "log",
        nargs="?",
        help="Log text to parse. If omitted, the built‑in example is used.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=argparse.FileType("r"),
        help="Read log text from a file.",
    )
    args = parser.parse_args(argv)

    if args.file:
        raw_text = args.file.read()
    elif args.log:
        raw_text = args.log
    else:
        raw_text = DEFAULT_LOG.strip()

    events = parse_events(raw_text)
    if not events:
        print("No events were parsed.")
        sys.exit(0)

    headers = ["kind", "path", "status", "duration_ms", "error_message"]
    rows = [_event_to_row(ev) for ev in events]
    print(tabulate(rows, headers=headers, tablefmt="github"))


if __name__ == "__main__":
    main()
