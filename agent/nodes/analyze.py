from __future__ import annotations

from pathlib import Path

from agent.llm import RuntimeLLM
from agent.state import AgentState


async def analyze_assignment_node(state: AgentState, llm: RuntimeLLM, prompt_dir: Path) -> AgentState:
    analysis = await llm.structured(
        prompt_dir / "analyze_assignment.md",
        {"task": state.get("current_task"), "submission": state.get("current_submission")},
    )
    return {**state, "node": "analyze_assignment", "analysis": analysis}


async def plan_code_changes_node(state: AgentState, llm: RuntimeLLM, prompt_dir: Path) -> AgentState:
    plan = await llm.structured(
        prompt_dir / "plan_changes.md",
        {
            "task": state.get("current_task"),
            "analysis": state.get("analysis"),
            "repository_files": state.get("repository_files", []),
        },
    )
    return {**state, "node": "plan_code_changes", "plan": plan}

