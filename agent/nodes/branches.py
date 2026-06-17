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


def checkout_assignment_branch(repo: GitRepo, task: dict, settings: Settings) -> tuple[str, str]:
    branch = assignment_branch_name(task, settings)
    base_sha = repo.root_commit()
    current = repo.checkout_branch_from(branch, base_sha)
    return current, base_sha
