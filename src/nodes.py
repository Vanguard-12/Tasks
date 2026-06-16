import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from .agent_state import AgentState
from .tools import unreliable_tool

# Initialise LLM (model name can be overridden via env)
LLM = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

def execute_task(state: AgentState) -> AgentState:
    """Call the unreliable tool and store the result or error."""
    try:
        result = unreliable_tool(state["task"])
        state["result"] = result
        state["error"] = None
    except Exception as e:
        state["result"] = None
        state["error"] = str(e)
    # After execution we keep status as pending – verification decides next step
    state["status"] = "pending"
    return state

def verify_result(state: AgentState) -> AgentState:
    """Ask the LLM to judge the result.

    The prompt forces the model to answer with exactly "success" or "failed".
    """
    task = state["task"]
    result = state.get("result")
    error = state.get("error")

    if error:
        # If the tool errored we can immediately mark as failed without LLM call
        verdict = "failed"
    else:
        prompt = (
            "You are a strict judge. Given the task and the result, respond with ONLY the word "
            "'success' if the result correctly fulfills the task, otherwise respond with 'failed'.\n"
            f"Task: {task}\nResult: {result}\n"
        )
        response = LLM.invoke([HumanMessage(content=prompt)])
        verdict = response.content.strip().lower()
        if verdict not in {"success", "failed"}:
            # Fallback safety
            verdict = "failed"
    state["status"] = verdict
    return state

def handle_error(state: AgentState) -> AgentState:
    """Increase attempt counter and prepare for a retry if possible."""
    state["attempts"] += 1
    # Reset transient fields for the next try
    state["result"] = None
    state["error"] = None
    if state["attempts"] >= state["max_attempts"]:
        state["status"] = "max_attempts"
    else:
        state["status"] = "pending"
    return state
