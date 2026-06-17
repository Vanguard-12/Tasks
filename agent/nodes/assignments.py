from __future__ import annotations

from typing import Any

from agent.api.journal import JournalAPIError, JournalClient
from agent.api.openapi_loader import default_base_url_from_schema, load_openapi_schema, require_paths
from agent.config import Settings
from agent.state import AgentState


REQUIRED_PATHS = [
    "/api/task/list/{courseId}",
    "/api/task/{taskId}",
    "/api/v2/submission/my",
    "/api/v2/submission/{submissionId}",
    "/api/v2/submission/{submissionId}/commit-data",
    "/api/v2/submission/{submissionId}/submit",
]

DONE_STATUSES = {"done", "ready_for_review"}


def as_items(value: Any, *, label: str) -> list[dict[str, Any]]:
    if isinstance(value, dict) and "body" in value:
        return as_items(value["body"], label=label)
    if isinstance(value, list):
        items = value
    elif isinstance(value, dict):
        for key in ("items", "data", "result", "results", label):
            if isinstance(value.get(key), list):
                items = value[key]
                break
        else:
            raise ValueError(f"Cannot parse {label}; raw keys: {sorted(value.keys())}")
    else:
        raise ValueError(f"Cannot parse {label}; expected list or object, got {type(value).__name__}")
    return [item for item in items if isinstance(item, dict)]


def str_field(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    return value if isinstance(value, str) else ""


def nested_str_field(data: dict[str, Any], first_key: str, second_key: str) -> str:
    nested = data.get(first_key)
    if not isinstance(nested, dict):
        return ""
    value = nested.get(second_key)
    return value if isinstance(value, str) else ""


def task_id(task: dict[str, Any]) -> str:
    return str_field(task, "_id")


def submission_task_id(submission: dict[str, Any]) -> str:
    task = submission.get("task")
    if not isinstance(task, dict):
        return ""
    return task_id(task)


def submission_id(submission: dict[str, Any]) -> str:
    return str_field(submission, "_id")


def title_of_task(task: dict[str, Any]) -> str:
    return str_field(task, "title") or task_id(task)


def status_of_submission(submission: dict[str, Any]) -> str:
    return str_field(submission, "status").lower()


def submission_created_at(submission: dict[str, Any]) -> str:
    return str_field(submission, "createdAt")


def lesson_date(task: dict[str, Any]) -> str:
    return nested_str_field(task, "lesson", "date")


def item_id(data: dict[str, Any]) -> str:
    # Internal compatibility helper: in this app it is only used for task objects.
    return task_id(data)


def task_id_from_submission(data: dict[str, Any]) -> str:
    return submission_task_id(data)


def is_done_submission(data: dict[str, Any]) -> bool:
    status = status_of_submission(data)
    if status in DONE_STATUSES:
        return True
    grade = data.get("grade")
    if isinstance(grade, dict) and grade.get("value") is True:
        return True
    return False


async def load_api_schema_node(state: AgentState, settings: Settings) -> AgentState:
    schema, source = await load_openapi_schema(
        swagger_url=settings.swagger_url,
        swagger_file_path=settings.swagger_file_path,
        timeout=settings.request_timeout_seconds,
    )
    missing = require_paths(schema, REQUIRED_PATHS)
    if missing:
        raise RuntimeError(f"Swagger is missing required paths: {', '.join(missing)}")
    base_url = settings.journal_api_base_url.rstrip("/") or (default_base_url_from_schema(schema) or "")
    return {**state, "node": "load_api_schema", "swagger": schema, "swagger_source": source, "api_base_url": base_url}


async def fetch_tasks_node(state: AgentState, client: JournalClient, settings: Settings) -> AgentState:
    try:
        raw = await client.list_tasks(settings.course_id)
        tasks = as_items(raw, label="tasks")
    except JournalAPIError as exc:
        if "teacher access required" not in str(exc):
            raise
        errors = [
            *state.get("errors", []),
            "GET /api/task/list/{courseId} requires teacher access; falling back to my submissions.",
        ]
        return {**state, "node": "fetch_tasks", "tasks": [], "errors": errors}
    return {**state, "node": "fetch_tasks", "tasks": tasks}


async def fetch_my_submissions_node(state: AgentState, client: JournalClient, settings: Settings) -> AgentState:
    raw = await client.my_submissions(settings.course_id)
    submissions = as_items(raw, label="submissions")
    return {**state, "node": "fetch_my_submissions", "submissions": submissions}


async def select_next_assignment_node(state: AgentState, settings: Settings) -> AgentState:
    tasks = state.get("tasks", [])
    submissions = state.get("submissions", [])
    if not tasks:
        tasks = tasks_from_submissions(submissions)
    by_task_id = {task_id_from_submission(item): item for item in submissions if task_id_from_submission(item)}
    assignments: list[dict[str, Any]] = []
    for task in tasks:
        task_id = item_id(task)
        if not task_id:
            raise ValueError(f"Cannot parse task id; raw keys: {sorted(task.keys())}")
        submission = by_task_id.get(task_id)
        include_done = settings.force_reprocess or settings.include_done_submissions
        ignore_reports = settings.force_reprocess or settings.ignore_local_reports
        if not include_done and submission and is_done_submission(submission):
            continue
        if not ignore_reports and has_local_report(task_id, settings):
            continue
        assignments.append({"task": task, "submission": submission})

    assignments = sort_assignments(assignments)

    index = state.get("assignment_index", 0)
    if index >= len(assignments):
        return {**state, "node": "select_next_assignment", "assignments": assignments, "done": True}
    current = assignments[index]
    return {
        **state,
        "node": "select_next_assignment",
        "assignments": assignments,
        "current_assignment": current,
        "current_task": current["task"],
        "current_submission": current.get("submission"),
        "done": False,
    }


def sort_assignments(assignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(assignments, key=assignment_sort_key)


def assignment_sort_key(assignment: dict[str, Any]) -> tuple[str, str, str, str]:
    task = assignment.get("task") if isinstance(assignment.get("task"), dict) else {}
    submission = assignment.get("submission") if isinstance(assignment.get("submission"), dict) else {}
    return (
        lesson_date(task),
        submission_created_at(submission),
        task_id(task),
        title_of_task(task).casefold(),
    )


def has_local_report(task_id: str, settings: Settings) -> bool:
    if settings.should_save_commit_metadata_to_journal() and settings.should_submit_to_journal():
        return False
    return (settings.repo_path / settings.local_reports_dir / f"{task_id}.json").exists()


def tasks_from_submissions(submissions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for submission in submissions:
        task: dict[str, Any]
        nested = submission.get("task")
        if isinstance(nested, dict):
            task = nested
        else:
            tid = task_id_from_submission(submission)
            if not tid:
                continue
            task = {"_id": tid, "title": tid}
        tid = item_id(task)
        if tid and tid not in seen:
            tasks.append(task)
            seen.add(tid)
    return tasks


async def load_task_details_node(state: AgentState, client: JournalClient) -> AgentState:
    task = state.get("current_task") or {}
    task_id = item_id(task)
    if not task_id:
        raise ValueError(f"Cannot load task details; raw keys: {sorted(task.keys())}")
    try:
        details = await client.get_task(task_id)
    except JournalAPIError as exc:
        if "teacher access required" not in str(exc):
            raise
        errors = [
            *state.get("errors", []),
            f"GET /api/task/{task_id} requires teacher access; using task data from submission.",
        ]
        return {**state, "node": "load_task_details", "current_task": task, "errors": errors}
    if not isinstance(details, dict):
        raise ValueError(f"Task details for {task_id} are not an object.")
    return {**state, "node": "load_task_details", "current_task": details}
