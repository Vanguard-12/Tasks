from __future__ import annotations

from pathlib import Path

from agent.llm import RuntimeLLM
from agent.state import AgentState
from agent.tools.checks import run_compileall, run_git_diff_check, run_placeholder_scan
from agent.tools.git import GitRepo


async def run_sanity_checks_node(state: AgentState, repo: GitRepo) -> AgentState:
    checks = {"checks": [run_compileall(repo.root)]}
    if repo.is_repo():
        checks["checks"].append(run_git_diff_check(repo))
        checks["checks"].append(run_placeholder_scan(repo))
    else:
        checks["checks"].append(
            {
                "name": "git diff --check",
                "ok": False,
                "output": f"{repo.root} is not a git repository.",
            }
        )
        checks["checks"].append(
            {
                "name": "placeholder scan",
                "ok": False,
                "output": f"{repo.root} is not a git repository.",
            }
        )
    return {**state, "node": "run_sanity_checks", "checks": checks}


async def review_diff_node(state: AgentState, llm: RuntimeLLM, repo: GitRepo, prompt_dir: Path) -> AgentState:
    diff = repo.diff() if repo.is_repo() else ""
    review = await llm.structured(
        prompt_dir / "review_diff.md",
        {
            "task": state.get("current_task"),
            "analysis": state.get("analysis"),
            "plan": state.get("plan"),
            "teacher_feedback": state.get("teacher_feedback", ""),
            "is_revision": state.get("is_revision", False),
            "replacement_commit": state.get("replacement_commit", False),
            "repo_url": state.get("repo_url", ""),
            "branch": state.get("branch", ""),
            "base_sha": state.get("base_sha", ""),
            "diff": diff,
            "changed_files": state.get("changed_files", []),
            "checks": state.get("checks", {}),
        },
    )
    return {**state, "node": "review_diff", "review": review}
