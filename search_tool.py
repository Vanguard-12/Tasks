import httpx
from bs4 import BeautifulSoup
import urllib.parse

def _fetch_duckduckgo(query: str) -> str:
    """Fetch a short snippet from DuckDuckGo's HTML results page.

    This function is deliberately simple and does not require an API key.
    It returns the first result snippet if available, otherwise a fallback
    message.
    """
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # DuckDuckGo places snippets in elements with class "result__snippet"
        snippet_el = soup.select_one('.result__snippet')
        if snippet_el and snippet_el.get_text(strip=True):
            return snippet_el.get_text(strip=True)
        # Fallback to the title of the first result
        title_el = soup.select_one('.result__title')
        if title_el and title_el.get_text(strip=True):
            return title_el.get_text(strip=True)
        return f"No results found for '{query}'."
    except Exception as exc:
        # In a production setting you would log the exception; here we return a
        # readable message so that callers can still continue.
        return f"Search error: {exc}"

def search(query: str) -> str:
    """Public wrapper used by the DeepAgent.

    Currently it delegates to a lightweight DuckDuckGo scraper. The function
    always returns a string – either a snippet, a title, or an error message.
    """
    return _fetch_duckduckgo(query)
