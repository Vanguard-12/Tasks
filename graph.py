'''graph.py

Compatibility wrapper for the HITL example.

The original implementation lives in ``hitl_graph.py``.  Tests and example
scripts in the repository import ``graph`` directly, so we re‑export the compiled
graph and its state type here.
'''

from hitl_graph import graph, GraphState

__all__ = ["graph", "GraphState"]
