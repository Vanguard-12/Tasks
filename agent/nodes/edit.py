from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from agent.llm import RuntimeLLM
from agent.config import Settings
from agent.nodes.branches import checkout_assignment_branch
from agent.state import AgentState
from agent.tools.git import GitRepo
from agent.tools.repo_fs import RepoFS, RepoFSError


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _planned_files(plan: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for key in ("files_to_inspect", "files_to_modify"):
        files.extend(_as_string_list(plan.get(key)))
    return sorted(set(files))


def _changed_since_baseline(repo: GitRepo, baseline_changed_files: list[str], fallback: list[str]) -> list[str]:
    if repo.is_repo():
        after_changed_files = repo.changed_files()
        return sorted(set(after_changed_files) - set(baseline_changed_files))
    return sorted(set(fallback))


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


def apply_operations(repo_fs: RepoFS, operations: Any) -> list[str]:
    if not isinstance(operations, list):
        raise ValueError("LLM response must include operations list.")

    changed: list[str] = []
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        tool = operation.get("tool")
        path = operation.get("path")
        if not isinstance(path, str):
            raise ValueError(f"Invalid edit operation path: {operation}")
        if tool == "write_file":
            content = operation.get("content")
            if not isinstance(content, str):
                raise ValueError(f"write_file requires string content: {path}")
            try:
                changed.append(repo_fs.write_file(path, content))
            except RepoFSError as exc:
                if Path(path).name in {".env", ".env.example"}:
                    continue
                raise exc
        elif tool == "apply_patch":
            old = operation.get("old")
            new = operation.get("new")
            if not isinstance(old, str) or not isinstance(new, str):
                raise ValueError(f"apply_patch requires string old and new fields: {path}")
            try:
                changed.append(repo_fs.apply_patch(path, old, new))
            except FileNotFoundError:
                continue
            except RepoFSError as exc:
                if Path(path).name in {".env", ".env.example"}:
                    continue
                if "Patch target text not found" in str(exc):
                    continue
                raise exc
        elif tool == "create_directory":
            repo_fs.create_directory(path)
        else:
            raise ValueError(f"Unsupported edit tool: {tool}")
    return changed


async def edit_repository_node(
    state: AgentState,
    llm: RuntimeLLM,
    repo_fs: RepoFS,
    repo: GitRepo,
    prompt_dir: Path,
    settings: Settings,
    adopt_existing_changes: bool = False,
) -> AgentState:
    task = state.get("current_task") or {}
    branch, base_sha, replacement_commit = checkout_assignment_branch(
        repo,
        task,
        settings,
        replace_existing=bool(state.get("is_revision")),
    )
    repo_url = public_repo_url(repo.remote_url() or settings.github_repo_url)
    baseline_changed_files = [] if adopt_existing_changes else (repo.changed_files() if repo.is_repo() else [])
    all_files = repo_fs.list_files()
    plan = state.get("plan", {})
    file_context: dict[str, str] = {}
    for rel in _planned_files(plan)[:20]:
        if rel in all_files:
            file_context[rel] = repo_fs.read_file(rel)

    edit_result = await llm.structured(
        prompt_dir / "edit_repository.md",
        {
            "task": state.get("current_task"),
            "analysis": state.get("analysis"),
            "plan": plan,
            "teacher_feedback": state.get("teacher_feedback", ""),
            "is_revision": state.get("is_revision", False),
            "replacement_commit": replacement_commit,
            "repo_url": repo_url,
            "branch": branch,
            "base_sha": base_sha,
            "files": all_files,
            "file_context": file_context,
        },
    )

    changed = apply_operations(repo_fs, edit_result.get("operations", []))
    changed_files = _changed_since_baseline(repo, baseline_changed_files, changed)
    return {
        **state,
        "node": "edit_repository",
        "edit_result": edit_result,
        "changed_files": changed_files,
        "baseline_changed_files": baseline_changed_files,
        "branch": branch,
        "base_sha": base_sha,
        "replacement_commit": replacement_commit,
        "repo_url": repo_url,
        "repair_attempts": 0,
    }


async def repair_repository_node(
    state: AgentState,
    llm: RuntimeLLM,
    repo_fs: RepoFS,
    repo: GitRepo,
    prompt_dir: Path,
) -> AgentState:
    baseline_changed_files = state.get("baseline_changed_files", [])
    diff = repo.diff() if repo.is_repo() else ""
    repair_result = await llm.structured(
        prompt_dir / "repair_repository.md",
        {
            "task": state.get("current_task"),
            "analysis": state.get("analysis"),
            "plan": state.get("plan"),
            "checks": state.get("checks", {}),
            "review": state.get("review", {}),
            "teacher_feedback": state.get("teacher_feedback", ""),
            "is_revision": state.get("is_revision", False),
            "replacement_commit": state.get("replacement_commit", False),
            "repo_url": state.get("repo_url", ""),
            "branch": state.get("branch", ""),
            "base_sha": state.get("base_sha", ""),
            "changed_files": state.get("changed_files", []),
            "diff": diff,
        },
    )
    changed = apply_operations(repo_fs, repair_result.get("operations", []))
    changed_files = _changed_since_baseline(repo, baseline_changed_files, changed)
    return {
        **state,
        "node": "repair_repository",
        "repair_result": repair_result,
        "repair_attempts": state.get("repair_attempts", 0) + 1,
        "changed_files": changed_files,
    }
