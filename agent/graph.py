from __future__ import annotations

from pathlib import Path

from langgraph.graph import END, StateGraph
from rich.console import Console

from agent.api.journal import JournalClient
from agent.config import Settings
from agent.deep_ui import append_ui_event
from agent.llm import RuntimeLLM
from agent.nodes.analyze import analyze_assignment_node, plan_code_changes_node
from agent.nodes.assignments import (
    fetch_my_submissions_node,
    fetch_tasks_node,
    load_api_schema_node,
    select_next_assignment_node,
)
from agent.nodes.assignments import load_task_details_node
from agent.nodes.edit import edit_repository_node, repair_repository_node
from agent.nodes.git_ops import commit_changes_node, push_changes_node
from agent.nodes.review import review_diff_node, run_sanity_checks_node
from agent.nodes.submit import print_summary_node, save_commit_metadata_node, submit_assignment_node
from agent.state import AgentState
from agent.tools.git import GitRepo
from agent.tools.repo_fs import RepoFS
from agent.ui import print_node_result, print_node_start


def normalize_initial_state(state: AgentState) -> AgentState:
    return {
        **state,
        "assignment_index": state.get("assignment_index", 0),
        "summaries": state.get("summaries", []),
        "errors": state.get("errors", []),
        "messages": state.get("messages", []),
        "todos": state.get("todos", []),
        "files": state.get("files", {}),
        "ui_events": state.get("ui_events", []),
        "assignment_stats": state.get("assignment_stats", {}),
        "ui_assignments": state.get("ui_assignments", {}),
    }


def build_graph(settings: Settings, console: Console):
    prompt_dir = Path("prompts").resolve()
    client = JournalClient(
        base_url=settings.journal_api_base_url,
        token=settings.journal_api_token,
        timeout=settings.request_timeout_seconds,
    )
    llm = RuntimeLLM(settings)
    repo = GitRepo(settings.repo_path)
    repo_fs = RepoFS(settings.repo_path)

    async def mark(name: str, coro):
        print_node_start(console, name)
        result = await coro
        result = append_ui_event(result, name)
        print_node_result(console, name, result, settings)
        return result

    async def load_api_schema(state: AgentState) -> AgentState:
        state = normalize_initial_state(state)
        return await mark("load_api_schema", load_api_schema_node(state, settings))

    async def fetch_tasks(state: AgentState) -> AgentState:
        return await mark("fetch_tasks", fetch_tasks_node(state, client, settings))

    async def fetch_my_submissions(state: AgentState) -> AgentState:
        return await mark("fetch_my_submissions", fetch_my_submissions_node(state, client, settings))

    async def select_next_assignment(state: AgentState) -> AgentState:
        return await mark("select_next_assignment", select_next_assignment_node(state, settings))

    async def load_task_details(state: AgentState) -> AgentState:
        return await mark("load_task_details", load_task_details_node(state, client))

    async def analyze_assignment(state: AgentState) -> AgentState:
        return await mark("analyze_assignment", analyze_assignment_node(state, llm, prompt_dir))

    async def plan_code_changes(state: AgentState) -> AgentState:
        return await mark("plan_code_changes", plan_code_changes_node(state, llm, prompt_dir))

    async def edit_repository(state: AgentState) -> AgentState:
        return await mark(
            "edit_repository",
            edit_repository_node(
                state,
                llm,
                repo_fs,
                repo,
                prompt_dir,
                settings,
                settings.adopt_existing_changes,
            ),
        )

    async def repair_repository(state: AgentState) -> AgentState:
        return await mark("repair_repository", repair_repository_node(state, llm, repo_fs, repo, prompt_dir))

    async def run_sanity_checks(state: AgentState) -> AgentState:
        return await mark("run_sanity_checks", run_sanity_checks_node(state, repo))

    async def review_diff(state: AgentState) -> AgentState:
        return await mark("review_diff", review_diff_node(state, llm, repo, prompt_dir))

    async def fail_assignment(state: AgentState) -> AgentState:
        return await mark("fail_assignment", fail_assignment_node(state, settings.max_repair_attempts))

    async def commit_changes(state: AgentState) -> AgentState:
        return await mark("commit_changes", commit_changes_node(state, repo, settings))

    async def push_changes(state: AgentState) -> AgentState:
        return await mark("push_changes", push_changes_node(state, repo, settings))

    async def save_commit_metadata(state: AgentState) -> AgentState:
        return await mark("save_commit_metadata", save_commit_metadata_node(state, client, settings))

    async def submit_assignment(state: AgentState) -> AgentState:
        return await mark("submit_assignment", submit_assignment_node(state, client, settings))

    async def print_summary(state: AgentState) -> AgentState:
        return await mark("print_summary", print_summary_node(state))

    workflow: StateGraph = StateGraph(AgentState)
    workflow.add_node("load_api_schema", load_api_schema)
    workflow.add_node("fetch_tasks", fetch_tasks)
    workflow.add_node("fetch_my_submissions", fetch_my_submissions)
    workflow.add_node("select_next_assignment", select_next_assignment)
    workflow.add_node("load_task_details", load_task_details)
    workflow.add_node("analyze_assignment", analyze_assignment)
    workflow.add_node("plan_code_changes", plan_code_changes)
    workflow.add_node("edit_repository", edit_repository)
    workflow.add_node("repair_repository", repair_repository)
    workflow.add_node("run_sanity_checks", run_sanity_checks)
    workflow.add_node("review_diff", review_diff)
    workflow.add_node("fail_assignment", fail_assignment)
    workflow.add_node("commit_changes", commit_changes)
    workflow.add_node("push_changes", push_changes)
    workflow.add_node("save_commit_metadata", save_commit_metadata)
    workflow.add_node("submit_assignment", submit_assignment)
    workflow.add_node("print_summary", print_summary)

    workflow.set_entry_point("load_api_schema")
    workflow.add_edge("load_api_schema", "fetch_tasks")
    workflow.add_edge("fetch_tasks", "fetch_my_submissions")
    workflow.add_edge("fetch_my_submissions", "select_next_assignment")
    workflow.add_conditional_edges(
        "select_next_assignment",
        lambda state: "done" if state.get("done") else "next",
        {"done": END, "next": "load_task_details"},
    )
    workflow.add_edge("load_task_details", "analyze_assignment")
    workflow.add_edge("analyze_assignment", "plan_code_changes")
    workflow.add_edge("plan_code_changes", "edit_repository")
    workflow.add_edge("edit_repository", "run_sanity_checks")
    workflow.add_conditional_edges(
        "run_sanity_checks",
        lambda state: next_after_checks(state, settings.max_repair_attempts),
        {"review": "review_diff", "repair": "repair_repository", "failed": "fail_assignment"},
    )
    workflow.add_edge("repair_repository", "run_sanity_checks")
    workflow.add_conditional_edges(
        "review_diff",
        lambda state: next_after_review(state, settings.max_repair_attempts),
        {"commit": "commit_changes", "repair": "repair_repository", "failed": "fail_assignment"},
    )
    workflow.add_edge("commit_changes", "push_changes")
    workflow.add_edge("push_changes", "save_commit_metadata")
    workflow.add_edge("save_commit_metadata", "submit_assignment")
    workflow.add_edge("submit_assignment", "print_summary")
    workflow.add_edge("print_summary", "fetch_my_submissions")
    return workflow.compile()


def checks_ok(state: AgentState) -> bool:
    checks = state.get("checks", {}).get("checks", [])
    return bool(checks) and all(isinstance(item, dict) and item.get("ok") for item in checks)


def next_after_checks(state: AgentState, max_repair_attempts: int) -> str:
    if checks_ok(state):
        return "review"
    if state.get("repair_attempts", 0) < max_repair_attempts:
        return "repair"
    return "failed"


def review_ok(state: AgentState) -> bool:
    review = state.get("review", {})
    return not (isinstance(review, dict) and review.get("acceptable") is False)


def next_after_review(state: AgentState, max_repair_attempts: int) -> str:
    if review_ok(state):
        return "commit"
    if state.get("repair_attempts", 0) < max_repair_attempts:
        return "repair"
    return "failed"


async def fail_assignment_node(state: AgentState, max_repair_attempts: int) -> AgentState:
    failed_checks = [
        item for item in state.get("checks", {}).get("checks", []) if isinstance(item, dict) and not item.get("ok")
    ]
    review = state.get("review", {})
    details = {
        "repair_attempts": state.get("repair_attempts", 0),
        "max_repair_attempts": max_repair_attempts,
        "failed_checks": failed_checks,
        "review": review,
    }
    raise RuntimeError(f"Assignment failed after repair attempts: {details}")
