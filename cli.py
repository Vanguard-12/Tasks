#!/usr/bin/env python3
"""Command‑line interface for the Structured‑Output API‑event parser.

The CLI can be invoked without arguments – it will use a built‑in example log –
or with ``--log <path>`` to point to a custom log file.  The parsed events are
displayed as a table using ``rich``.
"""

import argparse
import sys
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

from parser import parse_log

# ---------------------------------------------------------------------------
# Example log used when the user does not provide their own input.
# ---------------------------------------------------------------------------
EXAMPLE_LOG = """
200 GET /api/users duration=123ms
---
404 GET /api/orders error=\"Order not found\"
---
500 POST /api/payments error=\"Internal server error\"
"""


def build_table(events: List[object]) -> Table:
    """Create a Rich ``Table`` from a list of ``ApiEvent`` instances.

    The table contains the common columns ``kind`` and ``path`` as well as the
    fields that are specific to each branch of the union.
    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("kind", style="cyan", no_wrap=True)
    table.add_column("path", style="green")
    table.add_column("status", style="yellow")
    table.add_column("duration_ms", style="blue")
    table.add_column("error_message", style="red")

    for ev in events:
        # ``model_dump`` returns a plain dict; we use ``get`` for optional keys.
        data = ev.model_dump()
        table.add_row(
            str(data.get("kind", "")),
            str(data.get("path", "")),
            str(data.get("status", "")),
            str(data.get("duration_ms", "")),
            str(data.get("error_message", "")),
        )
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse raw API logs into structured events.")
    parser.add_argument(
        "--log",
        type=str,
        help="Path to a log file. If omitted, a built‑in example log is used.",
    )
    args = parser.parse_args()

    if args.log:
        log_path = Path(args.log)
        if not log_path.is_file():
            print(f"[error] Provided path does not exist or is not a file: {log_path}", file=sys.stderr)
            sys.exit(1)
        raw_text = log_path.read_text(encoding="utf-8")
    else:
        raw_text = EXAMPLE_LOG.strip()

    events = parse_log(raw_text)
    if not events:
        print("[warning] No events could be parsed.")
        sys.exit(0)

    console = Console()
    console.print("[bold underline]Parsed API Events[/]\n")
    for ev in events:
        console.print(ev.model_dump())
    console.print("\n")
    table = build_table(events)
    console.print(table)


if __name__ == "__main__":
    main()
