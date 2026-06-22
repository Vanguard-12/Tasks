from __future__ import annotations

from rich.console import Console

from agent.config import load_settings
from agent.graph import build_graph


settings = load_settings()
graph = build_graph(settings, Console())
