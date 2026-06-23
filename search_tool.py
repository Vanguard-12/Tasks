from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import BaseTool
from typing import Dict

class SearchTool(BaseTool):
    """A simple web search tool using SerpAPI."""

    name: str = "web_search"
    description: str = "Perform a web search and return the top results as a string."

    def _run(self, query: str) -> str:
        """Execute the search and return results as plain text."""
        search = SerpAPIWrapper()
        results = search.run(query)
        return results

    async def _arun(self, query: str) -> str:  # pragma: no cover
        return self._run(query)
