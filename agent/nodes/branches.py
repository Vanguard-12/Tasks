from __future__ import annotations

import re

from agent.config import Settings
from agent.nodes.assignments import item_id, title_of_task
from agent.tools.git import GitRepo


def slugify_branch_part(text: str, *, max_length: int = 48) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    value = re.sub(r"-{2,}", "-", value)
    return value[:max_length].strip("-")


def assignment_branch_name(task: dict, settings: Settings) -> str:
    task_id = item_id(task)
    title = title_of_task(task)
    short_id = slugify_branch_part(task_id[:10]) or "task"
    title_slug = slugify_branch_part(title)
    if title_slug:
        return f"assignment-agent/task/{short_id}-{title_slug}"
    return f"assignment-agent/task/{short_id}"


def checkout_assignment_branch(
    repo: GitRepo,
    task: dict,
    settings: Settings,
    *,
    replace_existing: bool = False,
) -> tuple[str, str, bool]:
    branch = assignment_branch_name(task, settings)
    base_sha = repo.root_commit()
    branch_exists = repo.branch_exists(branch) or repo.remote_branch_exists(branch)
    if not branch_exists:
        repo.fetch_branch(branch)
        branch_exists = repo.remote_branch_exists(branch)
    current = repo.checkout_branch_from(branch, base_sha)
    replacement_commit = replace_existing and branch_exists
    if replacement_commit:
        if not repo.is_clean():
            raise RuntimeError(
                f"Cannot prepare revision branch {branch}; working tree is dirty. "
                "Clean or commit current changes before rerunning the agent."
            )
        repo.reset_hard(base_sha)
        repo.clean_untracked()
    return current, base_sha, replacement_commit
