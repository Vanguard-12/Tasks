from __future__ import annotations

from collections import Counter
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent.config import Settings
from agent.nodes.assignments import (
    item_id,
    status_of_submission,
    submission_id,
    submission_task_id,
    title_of_task,
)
from agent.nodes.branches import assignment_branch_name


NODE_LABELS = {
    "load_api_schema": "Загрузка Swagger/OpenAPI",
    "fetch_tasks": "Загрузка списка заданий",
    "fetch_my_submissions": "Загрузка моих submissions",
    "select_next_assignment": "Выбор следующего задания",
    "load_task_details": "Загрузка деталей задания",
    "analyze_assignment": "Анализ условия",
    "plan_code_changes": "Планирование изменений",
    "edit_repository": "Редактирование репозитория",
    "repair_repository": "Исправление замечаний",
    "run_sanity_checks": "Sanity checks",
    "review_diff": "LLM-review diff",
    "commit_changes": "Git commit",
    "push_changes": "Git push",
    "save_commit_metadata": "Сохранение commit metadata",
    "submit_assignment": "Отправка задания",
    "print_summary": "Итог задания",
    "fail_assignment": "Ошибка задания",
}


def node_label(name: str) -> str:
    return NODE_LABELS.get(name, name)


def print_agent_started(console: Console) -> None:
    console.print(
        Panel.fit(
            "[bold green]Journal.bh Assignment Agent[/bold green]\n"
            "[dim]Автономный запуск: анализ, ветка, commit, push, submit[/dim]",
            border_style="green",
        )
    )


def print_node_start(console: Console, name: str) -> None:
    console.print(f"[bold cyan]Этап:[/bold cyan] {node_label(name)}")


def status_bucket(submission: dict[str, Any]) -> str:
    status = status_of_submission(submission)
    grade = submission.get("grade")
    if isinstance(grade, dict) and grade.get("value") is True:
        return "done"
    if status == "done":
        return "done"
    if status == "ready_for_review":
        return "review"
    return "todo"


def submission_stats(submissions: list[dict[str, Any]]) -> dict[str, int]:
    counter = Counter(status_bucket(item) for item in submissions if isinstance(item, dict))
    return {
        "total": len([item for item in submissions if isinstance(item, dict)]),
        "done": counter["done"],
        "review": counter["review"],
        "todo": counter["todo"],
    }


def print_submission_overview(console: Console, submissions: list[dict[str, Any]]) -> None:
    stats = submission_stats(submissions)
    table = Table(title="Статус заданий", show_header=True, header_style="bold magenta")
    table.add_column("Всего", justify="right")
    table.add_column("Зачтено", justify="right", style="green")
    table.add_column("На проверке", justify="right", style="yellow")
    table.add_column("Нужно сделать", justify="right", style="cyan")
    table.add_row(
        str(stats["total"]),
        str(stats["done"]),
        str(stats["review"]),
        str(stats["todo"]),
    )
    console.print(table)


def print_assignment_start(console: Console, state: dict[str, Any], settings: Settings) -> None:
    if state.get("done"):
        console.print(Panel.fit("[bold green]Все доступные задания обработаны.[/bold green]", border_style="green"))
        return
    task = state.get("current_task") or {}
    submission = state.get("current_submission") or {}
    branch = assignment_branch_name(task, settings)
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Задание", title_of_task(task))
    table.add_row("Task ID", item_id(task))
    table.add_row("Submission ID", submission_id(submission))
    table.add_row("Статус", status_of_submission(submission) or "unknown")
    table.add_row("Ветка", branch)
    console.print(Panel(table, title="[bold]Начинаю задание[/bold]", border_style="cyan"))


def print_edit_result(console: Console, state: dict[str, Any]) -> None:
    branch = state.get("branch", "")
    changed = state.get("changed_files", [])
    table = Table(title="Изменения в репозитории")
    table.add_column("Параметр")
    table.add_column("Значение")
    table.add_row("Ветка", str(branch))
    table.add_row("Base SHA", str(state.get("base_sha", ""))[:12])
    table.add_row("Файлов изменено", str(len(changed)))
    console.print(table)
    if changed:
        files = Table(show_header=True, header_style="bold")
        files.add_column("Файл")
        for path in changed:
            files.add_row(str(path))
        console.print(files)


def print_checks(console: Console, state: dict[str, Any]) -> None:
    checks = state.get("checks", {}).get("checks", [])
    table = Table(title="Sanity checks")
    table.add_column("Check")
    table.add_column("Status")
    for item in checks:
        if not isinstance(item, dict):
            continue
        ok = bool(item.get("ok"))
        table.add_row(str(item.get("name", "check")), "[green]OK[/green]" if ok else "[red]FAIL[/red]")
    console.print(table)


def print_review(console: Console, state: dict[str, Any]) -> None:
    review = state.get("review", {})
    if not isinstance(review, dict):
        return
    acceptable = review.get("acceptable") is not False
    color = "green" if acceptable else "red"
    status = "Принято" if acceptable else "Нужны исправления"
    details = []
    for key in ("missing_requirements", "missing_dependencies", "dependency_issues", "findings"):
        value = review.get(key)
        if isinstance(value, list) and value:
            details.append(f"[bold]{key}[/bold]: {len(value)}")
    body = "\n".join(details) if details else str(review.get("summary", ""))
    console.print(Panel(body or status, title=f"[bold {color}]Review: {status}[/bold {color}]", border_style=color))


def print_commit(console: Console, state: dict[str, Any]) -> None:
    table = Table(title="Commit")
    table.add_column("Параметр")
    table.add_column("Значение")
    table.add_row("Message", str(state.get("commit_message", "")))
    table.add_row("SHA", str(state.get("commit_sha", "")))
    table.add_row("Branch", str(state.get("branch", "")))
    console.print(table)


def print_submit_success(console: Console, state: dict[str, Any]) -> None:
    task = state.get("current_task") or {}
    body = (
        f"[bold]Задание:[/bold] {title_of_task(task)}\n"
        f"[bold]Commit:[/bold] {str(state.get('commit_sha', ''))[:12]}\n"
        f"[bold]Ссылка:[/bold] {state.get('submission_content', '')}"
    )
    console.print(Panel(body, title="[bold green]Задание отправлено[/bold green]", border_style="green"))


def print_node_result(console: Console, name: str, state: dict[str, Any], settings: Settings) -> None:
    if name == "fetch_my_submissions":
        print_submission_overview(console, state.get("submissions", []))
    elif name == "select_next_assignment":
        print_assignment_start(console, state, settings)
    elif name == "edit_repository":
        print_edit_result(console, state)
    elif name == "run_sanity_checks":
        print_checks(console, state)
    elif name == "review_diff":
        print_review(console, state)
    elif name == "repair_repository":
        console.print(f"[yellow]Repair attempt:[/yellow] {state.get('repair_attempts', 0)}")
    elif name == "commit_changes":
        print_commit(console, state)
    elif name == "push_changes":
        console.print(f"[green]Push выполнен:[/green] {state.get('branch', '')}")
    elif name == "save_commit_metadata":
        console.print("[green]Commit metadata сохранена в Journal.bh[/green]")
    elif name == "submit_assignment":
        print_submit_success(console, state)
