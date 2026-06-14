"""Command‑line interface for the *Structured Output – Union* demo.

The script can be executed directly::

    python main.py               # uses the built‑in example log
    python main.py --log "..."   # parses a custom log supplied on the command line

It relies on :pymod:`parser.parse_log` to obtain a list of ``ApiEvent``
instances and then prints a tidy table using ``tabulate``.
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from tabulate import tabulate

from models import ApiEvent, HttpOkEvent, HttpErrorEvent
from parser import parse_log

EXAMPLE_LOG = """
GET /api/users 200 duration=123ms
---
POST /api/orders 500 error="Internal Server Error"
---
GET /health 200 duration=5ms
"""


def _event_to_row(event: ApiEvent) -> List[str]:
    """Convert a concrete ``ApiEvent`` into a flat list suitable for ``tabulate``.

    The columns are: ``kind``, ``path``, ``status``, ``duration_ms`` (or ``-``),
    ``error_message`` (or ``-``).
    """
    base = [event.kind, getattr(event, "path", "-"), str(getattr(event, "status", "-"))]
    if isinstance(event, HttpOkEvent):
        return base + [str(event.duration_ms), "-"]
    elif isinstance(event, HttpErrorEvent):
        return base + ["-", event.error_message]
    else:
        # Fallback – should never happen because of the discriminated union.
        return base + ["-", "-"]


def _print_table(events: List[ApiEvent]) -> None:
    headers = ["kind", "path", "status", "duration_ms", "error_message"]
    rows = [_event_to_row(ev) for ev in events]
    print(tabulate(rows, headers=headers, tablefmt="github"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse a raw HTTP log into typed events using LangChain structured output."
    )
    parser.add_argument(
        "--log",
        type=str,
        help="Raw log text to parse. If omitted, a built‑in example is used.",
    )
    args = parser.parse_args()

    log_text = args.log if args.log is not None else EXAMPLE_LOG

    try:
        events = parse_log(log_text)
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    _print_table(events)


if __name__ == "__main__":
    main()
