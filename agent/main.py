from __future__ import annotations

import asyncio
import sys
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from agent.config import load_settings
from agent.graph import build_graph
from agent.ui import print_agent_started

app = typer.Typer(help="Journal.bh autonomous assignment agent.")
console = Console()


def safe_text(value: object) -> str:
    text = str(value)
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def _print_config_summary(settings) -> None:
    table = Table(title="Runtime")
    table.add_column("Key")
    table.add_column("Value")
    table.add_row("Swagger", settings.swagger_url or str(settings.swagger_file_path))
    table.add_row("API base URL", settings.journal_api_base_url)
    table.add_row("Course ID", settings.course_id or "<missing>")
    table.add_row("Repo path", str(settings.repo_path))
    table.add_row("Work branch", settings.git_work_branch)
    table.add_row("Local submit", str(settings.local_submit))
    table.add_row("Dry run", str(settings.dry_run))
    table.add_row("Push changes", str(settings.should_push_changes()))
    table.add_row("Save metadata", str(settings.should_save_commit_metadata_to_journal()))
    table.add_row("Submit Journal", str(settings.should_submit_to_journal()))
    table.add_row("Force reprocess", str(settings.force_reprocess))
    table.add_row("Ignore reports", str(settings.ignore_local_reports))
    table.add_row("Include done", str(settings.include_done_submissions))
    table.add_row("Repair attempts", str(settings.max_repair_attempts))
    table.add_row("Adopt dirty", str(settings.adopt_existing_changes))
    table.add_row("LLM model", settings.llm_model)
    console.print(table)


def _print_summary(final_state: dict[str, Any]) -> None:
    summaries = final_state.get("summaries", [])
    if not summaries:
        console.print("[yellow]No assignments were processed.[/yellow]")
        return
    table = Table(title="Processed Assignments")
    table.add_column("Task")
    table.add_column("Title")
    table.add_column("Branch")
    table.add_column("Commit")
    table.add_column("Report")
    for item in summaries:
        table.add_row(
            str(item.get("taskId", "")),
            str(item.get("taskTitle", "")),
            str(item.get("branch", "")),
            str(item.get("commitSha", ""))[:12],
            str(item.get("localReportPath", "")),
        )
    console.print(table)


async def _run_async() -> None:
    settings = load_settings()
    _print_config_summary(settings)
    missing = settings.validate_runtime()
    if missing:
        raise typer.BadParameter(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Create .env from .env.example and fill them."
        )

    graph = build_graph(settings, console)
    initial_state = {"assignment_index": 0, "summaries": [], "errors": []}
    final_state = await graph.ainvoke(initial_state, config={"recursion_limit": 250})
    _print_summary(final_state)


@app.callback()
def main() -> None:
    """Journal.bh autonomous assignment agent."""


@app.command()
def run() -> None:
    """Run the assignment-solving workflow."""
    print_agent_started(console)
    try:
        asyncio.run(_run_async())
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {safe_text(exc)}")
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
