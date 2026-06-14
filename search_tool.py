import httpx
from bs4 import BeautifulSoup
from typing import List


class DuckDuckGoSearch:
    """Very small DuckDuckGo HTML scraper.

    The implementation is deliberately lightweight – it does **not** use any
    paid API keys. It fetches the public HTML search page, extracts the first few
    result titles and snippets, and returns a concise plain‑text summary.
    """

    SEARCH_URL = "https://duckduckgo.com/html/"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    @staticmethod
    def _fetch(query: str) -> str:
        params = {"q": query}
        with httpx.Client(timeout=10.0, headers=DuckDuckGoSearch.HEADERS) as client:
            response = client.get(DuckDuckGoSearch.SEARCH_URL, params=params)
            response.raise_for_status()
            return response.text

    @staticmethod
    def _parse(html: str, max_results: int = 3) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for result in soup.select("div.result")[:max_results]:
            title_el = result.select_one("a.result__a")
            snippet_el = result.select_one("a.result__snippet") or result.select_one("div.result__snippet")
            title = title_el.get_text(strip=True) if title_el else ""
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            combined = f"{title}: {snippet}" if title else snippet
            results.append(combined)
        return results

    @classmethod
    def search(cls, query: str) -> str:
        """Return a short plain‑text summary of the top results.

        The function concatenates up to three result snippets separated by newlines.
        """
        html = cls._fetch(query)
        snippets = cls._parse(html)
        if not snippets:
            return "No results found."
        return "\n\n".join(snippets)
