import sys
from pathlib import Path

# Ensure the project root is on PYTHONPATH for imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

from brief_agent import graph, BriefState

@pytest.fixture(scope="module")
def default_state():
    return {"topic": "Test topic for unit‑test"}

def test_outline_generation():
    # Run the whole graph; the outline node will be executed first
    result = graph.invoke({"topic": "Artificial intelligence in education"}, config={"recursion_limit": 15})
    assert isinstance(result.get("outline"), list)
    assert 4 <= len(result["outline"]) <= 5

def test_research_loop_counts():
    # Monkey‑patch the outline node to return a known short outline (3 items)
    from brief_agent import outline_node, workflow

    def fake_outline(state):
        return {"outline": ["A", "B", "C"], "step_index": 0, "notes": []}

    original = workflow.nodes["outline"]
    workflow.nodes["outline"] = fake_outline
    try:
        result = graph.invoke({"topic": "dummy"}, config={"recursion_limit": 30})
        assert len(result["notes"]) == 3
        assert result["step_index"] == 3
    finally:
        workflow.nodes["outline"] = original

def test_synthesize_output():
    # Provide a minimal state with pre‑filled notes and outline
    state: BriefState = {
        "topic": "dummy",
        "outline": ["Item 1", "Item 2"],
        "step_index": 2,
        "notes": ["Note one.", "Note two."],
        "final_brief": None,
    }
    from brief_agent import synthesize_node
    out = synthesize_node(state)
    brief = out["final_brief"]
    assert isinstance(brief, str)
    # At least one heading should appear
    assert "Item 1" in brief or "Item 2" in brief
    # Rough length check (more than 30 words)
    assert len(brief.split()) > 30
