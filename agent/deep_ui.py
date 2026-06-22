from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from agent.nodes.assignments import item_id, status_of_submission, submission_id, title_of_task
from agent.state import AgentState


def append_ui_event(state: AgentState, node: str, status: str = "completed") -> AgentState:
    event = build_event(state, node, status)
    events = [*state.get("ui_events", []), event]
    messages = state.get("messages", [])
    assignments = update_ui_assignments(state, event)
    next_state: AgentState = {
        **state,
        "ui_events": events,
        "ui_assignments": assignments,
        "assignment_stats": submission_stats(state.get("submissions", [])),
    }
    if event.get("message"):
        next_state["messages"] = [
            *messages,
            {"id": str(uuid4()), "type": "ai", "content": event["message"]},
        ]
    next_state["todos"] = build_todos(next_state)
    next_state["files"] = build_files(next_state)
    return next_state


def build_event(state: AgentState, node: str, status: str) -> dict[str, Any]:
    task = state.get("current_task") or {}
    submission = state.get("current_submission") or {}
    title = title_of_task(task)
    event = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "node": node,
        "status": status,
        "taskId": item_id(task),
        "taskTitle": title,
        "submissionId": submission_id(submission),
        "message": event_message(state, node, title),
    }
    return event


def event_message(state: AgentState, node: str, title: str) -> str:
    if node == "fetch_my_submissions":
        stats = submission_stats(state.get("submissions", []))
        return (
            "Loaded submissions: "
            f"{stats['done']} accepted, {stats['review']} in review, {stats['todo']} to process."
        )
    if node == "select_next_assignment":
        if state.get("done"):
            return "All available assignments are processed."
        revision = " revision" if state.get("is_revision") else ""
        return f"Selected{revision} assignment: {title}"
    if node == "load_task_details":
        return f"Loaded full task details for: {title}"
    if node == "analyze_assignment":
        return f"Analyzed assignment requirements for: {title}"
    if node == "plan_code_changes":
        return f"Planned repository changes for: {title}"
    if node == "edit_repository":
        changed = len(state.get("changed_files", []))
        return f"Edited repository on {state.get('branch', '')}; changed files: {changed}."
    if node == "repair_repository":
        return f"Applied repair attempt {state.get('repair_attempts', 0)}."
    if node == "run_sanity_checks":
        failed = failed_checks(state)
        return "Sanity checks passed." if not failed else f"Sanity checks failed: {', '.join(failed)}."
    if node == "review_diff":
        review = state.get("review", {})
        if isinstance(review, dict) and review.get("acceptable") is False:
            return "LLM review requested fixes."
        return "LLM review accepted the diff."
    if node == "commit_changes":
        return f"Created commit {str(state.get('commit_sha', ''))[:12]}."
    if node == "push_changes":
        return f"Pushed branch {state.get('branch', '')}."
    if node == "save_commit_metadata":
        return "Saved commit metadata."
    if node == "submit_assignment":
        return "Submitted assignment for review."
    if node == "print_summary":
        return f"Finished assignment: {title}"
    if node == "fail_assignment":
        return f"Assignment failed after repair attempts: {title}"
    return f"Completed node: {node}"


def submission_stats(submissions: list[dict[str, Any]]) -> dict[str, int]:
    stats = {"total": 0, "done": 0, "review": 0, "todo": 0}
    for submission in submissions:
        if not isinstance(submission, dict):
            continue
        stats["total"] += 1
        grade = submission.get("grade")
        if isinstance(grade, dict) and grade.get("value") is True:
            stats["done"] += 1
            continue
        status = status_of_submission(submission)
        if status == "done":
            stats["done"] += 1
        elif status == "ready_for_review":
            stats["review"] += 1
        else:
            stats["todo"] += 1
    return stats


def failed_checks(state: AgentState) -> list[str]:
    names: list[str] = []
    for item in state.get("checks", {}).get("checks", []):
        if isinstance(item, dict) and not item.get("ok"):
            names.append(str(item.get("name", "check")))
    return names


def build_files(state: AgentState) -> dict[str, str]:
    return {
        "agent_status.md": status_markdown(state),
        "current_assignment.md": assignment_markdown(state),
        "checks_and_review.md": checks_review_markdown(state),
        "git_and_submission.md": git_submission_markdown(state),
        "event_timeline.md": timeline_markdown(state),
    }


WORKFLOW_TODOS = [
    ("load_api_schema", "Load Swagger/OpenAPI schema"),
    ("fetch_tasks", "Load course tasks"),
    ("fetch_my_submissions", "Load my submissions"),
    ("select_next_assignment", "Select next assignment"),
    ("load_task_details", "Load full task details"),
    ("analyze_assignment", "Analyze assignment requirements"),
    ("plan_code_changes", "Plan repository changes"),
    ("edit_repository", "Edit assignment repository"),
    ("run_sanity_checks", "Run sanity checks"),
    ("review_diff", "Review final diff"),
    ("commit_changes", "Create git commit"),
    ("push_changes", "Push branch"),
    ("save_commit_metadata", "Save commit metadata"),
    ("submit_assignment", "Submit assignment"),
]


def build_todos(state: AgentState) -> list[dict[str, str]]:
    completed = {event.get("node") for event in state.get("ui_events", []) if event.get("status") == "completed"}
    current = state.get("node", "")
    todos: list[dict[str, str]] = []
    for node, content in WORKFLOW_TODOS:
        if node in completed:
            status = "completed"
        elif node == current:
            status = "in_progress"
        else:
            status = "pending"
        todos.append({"id": node, "content": content, "status": status})
    return todos


def update_ui_assignments(state: AgentState, event: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assignments = dict(state.get("ui_assignments", {}))
    task = state.get("current_task") or {}
    submission = state.get("current_submission") or {}
    task_id = item_id(task)
    if not task_id:
        return assignments
    current = dict(assignments.get(task_id, {}))
    current_events = [*current.get("events", []), event]
    current.update(
        {
            "taskId": task_id,
            "taskTitle": title_of_task(task),
            "submissionId": submission_id(submission),
            "submissionStatus": status_of_submission(submission) or "unknown",
            "isRevision": bool(state.get("is_revision")),
            "teacherFeedback": state.get("teacher_feedback", ""),
            "currentNode": state.get("node", event.get("node", "")),
            "status": assignment_card_status(state),
            "branch": state.get("branch", ""),
            "baseSha": state.get("base_sha", ""),
            "commitSha": state.get("commit_sha", ""),
            "submissionContent": state.get("submission_content", ""),
            "changedFiles": state.get("changed_files", []),
            "checks": state.get("checks", {}).get("checks", []),
            "review": state.get("review", {}),
            "repairAttempts": state.get("repair_attempts", 0),
            "events": current_events[-20:],
        }
    )
    assignments[task_id] = current
    return assignments


def assignment_card_status(state: AgentState) -> str:
    if state.get("node") == "submit_assignment":
        return "submitted"
    review = state.get("review", {})
    if isinstance(review, dict) and review.get("acceptable") is False:
        return "needs_repair"
    failed = failed_checks(state)
    if failed:
        return "checks_failed"
    if state.get("node") in {"commit_changes", "push_changes", "save_commit_metadata"}:
        return "publishing"
    if state.get("node") == "print_summary":
        return "finished"
    return "running"


def status_markdown(state: AgentState) -> str:
    stats = submission_stats(state.get("submissions", []))
    task = state.get("current_task") or {}
    return "\n".join(
        [
            "# Journal.bh Assignment Agent",
            "",
            f"- Current node: `{state.get('node', 'not started')}`",
            f"- Current task: {title_of_task(task) or 'none'}",
            f"- Done: {stats['done']}",
            f"- In review: {stats['review']}",
            f"- To process: {stats['todo']}",
            f"- Repair attempts: {state.get('repair_attempts', 0)}",
            f"- Branch: `{state.get('branch', '')}`",
            f"- Commit: `{state.get('commit_sha', '')}`",
        ]
    )


def assignment_markdown(state: AgentState) -> str:
    task = state.get("current_task") or {}
    submission = state.get("current_submission") or {}
    lines = [
        "# Current Assignment",
        "",
        f"- Title: {title_of_task(task) or 'none'}",
        f"- Task ID: `{item_id(task)}`",
        f"- Submission ID: `{submission_id(submission)}`",
        f"- Submission status: `{status_of_submission(submission) or 'unknown'}`",
        f"- Revision: `{bool(state.get('is_revision'))}`",
    ]
    feedback = state.get("teacher_feedback")
    if feedback:
        lines.extend(["", "## Teacher Feedback", "", str(feedback)])
    return "\n".join(lines)


def checks_review_markdown(state: AgentState) -> str:
    lines = ["# Checks And Review", "", "## Sanity Checks", ""]
    checks = state.get("checks", {}).get("checks", [])
    if checks:
        for item in checks:
            if not isinstance(item, dict):
                continue
            status = "OK" if item.get("ok") else "FAIL"
            lines.append(f"- `{item.get('name', 'check')}`: **{status}**")
            output = str(item.get("output", "")).strip()
            if output:
                lines.extend(["", "```text", output, "```", ""])
    else:
        lines.append("No checks have run yet.")
    lines.extend(["", "## LLM Review", ""])
    review = state.get("review", {})
    if isinstance(review, dict) and review:
        lines.append(f"- Acceptable: `{review.get('acceptable') is not False}`")
        for key in ("missing_requirements", "missing_dependencies", "dependency_issues", "findings"):
            value = review.get(key)
            if isinstance(value, list) and value:
                lines.extend(["", f"### {key}", ""])
                lines.extend(f"- {item}" for item in value)
        if review.get("summary"):
            lines.extend(["", "### Summary", "", str(review["summary"])])
    else:
        lines.append("No review has run yet.")
    return "\n".join(lines)


def git_submission_markdown(state: AgentState) -> str:
    changed = state.get("changed_files", [])
    lines = [
        "# Git And Submission",
        "",
        f"- Branch: `{state.get('branch', '')}`",
        f"- Base SHA: `{state.get('base_sha', '')}`",
        f"- Commit SHA: `{state.get('commit_sha', '')}`",
        f"- Commit message: `{state.get('commit_message', '')}`",
        f"- Repository URL: `{state.get('repo_url', '')}`",
        f"- Submission link: `{state.get('submission_content', '')}`",
        "",
        "## Changed Files",
        "",
    ]
    lines.extend(f"- `{path}`" for path in changed) if changed else lines.append("No changed files yet.")
    return "\n".join(lines)


def timeline_markdown(state: AgentState) -> str:
    lines = ["# Event Timeline", ""]
    events = state.get("ui_events", [])
    if not events:
        return "# Event Timeline\n\nNo events yet."
    for event in events:
        lines.append(f"- `{event.get('time')}` **{event.get('node')}**: {event.get('message')}")
    return "\n".join(lines)
