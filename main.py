from __future__ import annotations

import os
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


class CodeReviewState(TypedDict):
    code: str
    draft_review: str
    critic_feedback: str
    verdict: Literal["ok", "needs_revision"]
    round: int
    max_rounds: int


class ReflectionResult(BaseModel):
    verdict: Literal["ok", "needs_revision"]
    feedback: str = Field(description="One concise overall critique of the review.")


def llm() -> ChatOpenAI:
    return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)


def draft_review(state: CodeReviewState) -> CodeReviewState:
    response = llm().invoke(
        [
            SystemMessage(
                content=(
                    "Write a concise Python code review in 3-6 bullet points. "
                    "Cover strengths and improvements for correctness, readability, typing, and edge cases."
                )
            ),
            HumanMessage(content=state["code"]),
        ]
    )
    return {**state, "draft_review": str(response.content)}


def reflect(state: CodeReviewState) -> CodeReviewState:
    structured_llm = llm().with_structured_output(ReflectionResult)
    result = structured_llm.invoke(
        [
            SystemMessage(
                content=(
                    "Evaluate the code review as a whole. Return only one overall verdict: "
                    "ok if the review is useful and complete, otherwise needs_revision. "
                    "Do not break the critique into separate criteria."
                )
            ),
            HumanMessage(
                content=(
                    f"Code:\n{state['code']}\n\n"
                    f"Review:\n{state['draft_review']}\n\n"
                    f"Round: {state['round']} of {state['max_rounds']}"
                )
            ),
        ]
    )
    return {**state, "verdict": result.verdict, "critic_feedback": result.feedback}


def rewrite(state: CodeReviewState) -> CodeReviewState:
    response = llm().invoke(
        [
            SystemMessage(
                content=(
                    "Rewrite the code review using the critic feedback. Keep it concise, concrete, "
                    "and focused on the reviewed Python function."
                )
            ),
            HumanMessage(
                content=(
                    f"Code:\n{state['code']}\n\n"
                    f"Current review:\n{state['draft_review']}\n\n"
                    f"Critic feedback:\n{state['critic_feedback']}"
                )
            ),
        ]
    )
    return {**state, "draft_review": str(response.content), "round": state["round"] + 1}


def route_after_reflect(state: CodeReviewState) -> str:
    if state["verdict"] == "ok":
        return END
    if state["round"] < state["max_rounds"]:
        return "rewrite"
    return END


def build_graph():
    graph = StateGraph(CodeReviewState)
    graph.add_node("draft_review", draft_review)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)
    graph.add_edge(START, "draft_review")
    graph.add_edge("draft_review", "reflect")
    graph.add_conditional_edges("reflect", route_after_reflect, {"rewrite": "rewrite", END: END})
    graph.add_edge("rewrite", "reflect")
    return graph.compile()


def initial_state(code: str, max_rounds: int = 2) -> CodeReviewState:
    return {
        "code": code,
        "draft_review": "",
        "critic_feedback": "",
        "verdict": "needs_revision",
        "round": 0,
        "max_rounds": max_rounds,
    }


def print_reflection(state: CodeReviewState) -> None:
    print(f"Verdict: {state['verdict']}")
    print(f"Critic feedback: {state['critic_feedback']}")
    print(f"Rounds used: {state['round']} / {state['max_rounds']}")


def main() -> None:
    load_dotenv()
    code = "def sort_numbers(arr):\n    return sorted(arr)"
    graph = build_graph()
    for event in graph.stream(initial_state(code)):
        for node, state in event.items():
            if node == "draft_review":
                print("Initial draft review:")
                print(state["draft_review"])
                print()
            elif node == "reflect":
                print_reflection(state)
                print()
            elif node == "rewrite":
                print(f"Rewritten review, round {state['round']}:")
                print(state["draft_review"])
                print()


if __name__ == "__main__":
    main()
