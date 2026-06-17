from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    swagger_source: str
    swagger: dict[str, Any]
    api_base_url: str

    tasks: list[dict[str, Any]]
    submissions: list[dict[str, Any]]
    assignments: list[dict[str, Any]]
    assignment_index: int
    current_assignment: dict[str, Any] | None
    current_task: dict[str, Any] | None
    current_submission: dict[str, Any] | None

    analysis: dict[str, Any]
    plan: dict[str, Any]
    edit_result: dict[str, Any]
    checks: dict[str, Any]
    review: dict[str, Any]
    repair_result: dict[str, Any]
    repair_attempts: int

    changed_files: list[str]
    baseline_changed_files: list[str]
    commit_message: str
    commit_sha: str
    branch: str
    base_sha: str
    repo_url: str
    local_report_path: str

    node: str
    errors: list[str]
    summaries: list[dict[str, Any]]
    done: bool
