from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

from agent.config import Settings
from agent.nodes.branches import assignment_branch_name
from agent.nodes.assignments import item_id, title_of_task
from agent.state import AgentState
from agent.tools.git import GitRepo


def commit_subject(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:72] if text else "assignment"


def committable_files(files: list[str]) -> list[str]:
    blocked = {".env", ".env.example"}
    return [path for path in files if path.replace("\\", "/") not in blocked]


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


async def commit_changes_node(state: AgentState, repo: GitRepo, settings: Settings) -> AgentState:
    failed_checks = [
        item for item in state.get("checks", {}).get("checks", []) if isinstance(item, dict) and not item.get("ok")
    ]
    if failed_checks:
        names = ", ".join(str(item.get("name", "check")) for item in failed_checks)
        raise RuntimeError(f"Cannot commit because sanity checks failed: {names}")
    review = state.get("review", {})
    if isinstance(review, dict) and review.get("acceptable") is False:
        raise RuntimeError(f"Cannot commit because LLM review rejected the diff: {review}")
    task = state.get("current_task") or {}
    title = title_of_task(task) or item_id(task)
    if state.get("is_revision"):
        message = f"fix: address feedback for {commit_subject(title)}"
    else:
        message = f"solve: {commit_subject(title)}"
    branch = state.get("branch") or assignment_branch_name(task, settings)
    repo.checkout_branch(branch)
    assignment_changed_files = committable_files(state.get("changed_files", []))
    if not assignment_changed_files:
        raise RuntimeError("No repository changes were produced for the assignment.")
    commit_sha = repo.commit_files(assignment_changed_files, message, settings.git_author_name, settings.git_author_email)
    return {
        **state,
        "node": "commit_changes",
        "commit_message": message,
        "commit_sha": commit_sha,
        "branch": branch,
        "changed_files": assignment_changed_files,
        "repo_url": public_repo_url(repo.remote_url() or settings.github_repo_url),
    }


async def push_changes_node(state: AgentState, repo: GitRepo, settings: Settings) -> AgentState:
    branch = state.get("branch") or settings.git_work_branch
    if not settings.should_push_changes():
        return {**state, "node": "push_changes"}
    repo.ensure_origin(settings.github_repo_url)
    repo.push(branch, force_with_lease=bool(state.get("replacement_commit")))
    return {**state, "node": "push_changes"}
