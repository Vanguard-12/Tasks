from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from agent.api.journal import JournalClient
from agent.config import Settings
from agent.nodes.assignments import item_id, submission_id, title_of_task
from agent.state import AgentState


def public_repo_url(repo_url: str) -> str:
    repo_url = repo_url.strip()
    if not repo_url:
        return ""
    if repo_url.startswith("git@github.com:"):
        repo_url = "https://github.com/" + repo_url.removeprefix("git@github.com:")
    elif repo_url.startswith("ssh://git@github.com/"):
        repo_url = "https://github.com/" + repo_url.removeprefix("ssh://git@github.com/")
    if repo_url.startswith(("http://", "https://")):
        parts = urlsplit(repo_url)
        netloc = parts.hostname or parts.netloc.split("@")[-1]
        if parts.port:
            netloc = f"{netloc}:{parts.port}"
        repo_url = urlunsplit((parts.scheme, netloc, parts.path, "", ""))
    return repo_url.removesuffix(".git")


def submission_content(state: AgentState, settings: Settings) -> str:
    repo_url = public_repo_url(state.get("repo_url", "") or settings.github_repo_url)
    commit_sha = state.get("commit_sha", "")
    branch = state.get("branch", "") or settings.git_work_branch
    if repo_url and commit_sha and "github.com/" in repo_url:
        return f"{repo_url}/commit/{commit_sha}"
    if repo_url and branch and "github.com/" in repo_url:
        return f"{repo_url}/tree/{branch}"
    if repo_url:
        return repo_url
    return commit_sha or branch


def commit_metadata_payload(state: AgentState) -> dict[str, Any]:
    return {
        "repoUrl": state.get("repo_url", ""),
        "branch": state.get("branch", ""),
        "commitSha": state.get("commit_sha", ""),
        "message": state.get("commit_message", ""),
        "files": [{"path": path} for path in state.get("changed_files", [])],
        "artifacts": [],
        "meta": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "localSubmit": True,
            "baseSha": state.get("base_sha", ""),
        },
    }


async def save_commit_metadata_node(
    state: AgentState,
    client: JournalClient,
    settings: Settings,
) -> AgentState:
    submission = state.get("current_submission") or {}
    payload = commit_metadata_payload(state)
    if not settings.should_save_commit_metadata_to_journal():
        report_dir = (settings.repo_path / settings.local_reports_dir).resolve()
        report_dir.mkdir(parents=True, exist_ok=True)
        task = state.get("current_task") or {}
        task_id = item_id(task) or "unknown-task"
        report_path = report_dir / f"{task_id}.json"
        report_path.write_text(
            json.dumps(
                {
                    "taskId": task_id,
                    "taskTitle": title_of_task(task),
                    "submissionId": submission_id(submission),
                    "commit": payload,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return {**state, "node": "save_commit_metadata", "local_report_path": str(report_path)}

    sid = submission_id(submission)
    if not sid:
        raise ValueError(f"Cannot save commit metadata; submission keys: {sorted(submission.keys())}")
    await client.save_commit_metadata(sid, payload)
    return {**state, "node": "save_commit_metadata"}


async def submit_assignment_node(state: AgentState, client: JournalClient, settings: Settings) -> AgentState:
    if not settings.should_submit_to_journal():
        return {**state, "node": "submit_assignment"}
    submission = state.get("current_submission") or {}
    sid = submission_id(submission)
    if not sid:
        raise ValueError(f"Cannot submit assignment; submission keys: {sorted(submission.keys())}")
    content = submission_content(state, settings)
    if not content:
        raise ValueError("Cannot submit assignment; commit link/content is empty.")
    await client.update_submission(sid, content=content, answer_type="link")
    await client.submit(sid)
    return {**state, "node": "submit_assignment", "submission_content": content}


async def print_summary_node(state: AgentState) -> AgentState:
    task = state.get("current_task") or {}
    summary = {
        "taskId": item_id(task),
        "taskTitle": title_of_task(task),
        "commitSha": state.get("commit_sha", ""),
        "branch": state.get("branch", ""),
        "baseSha": state.get("base_sha", ""),
        "changedFiles": state.get("changed_files", []),
        "localReportPath": state.get("local_report_path", ""),
    }
    summaries = [*state.get("summaries", []), summary]
    return {
        **state,
        "node": "print_summary",
        "summaries": summaries,
        "assignment_index": 0,
    }
